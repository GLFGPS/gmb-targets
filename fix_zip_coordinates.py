#!/usr/bin/env python3
"""
Fix zip code coordinates using actual geocoded data
"""

import pandas as pd
from uszipcode import SearchEngine

print("🗺️  Fixing zip code coordinates with accurate geocoded data...")
print("=" * 70)

# Read the demographic data (without coordinates)
df = pd.read_csv('/workspace/demographic_data.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes")

# Initialize the zip code search engine
search = SearchEngine()

print("📍 Geocoding zip codes (this may take a minute)...")

# Get actual coordinates for each zip code
coords_data = []
not_found = []

for idx, row in df.iterrows():
    zip_code = row['zip_code']
    
    # Search for zip code
    zipcode_obj = search.by_zipcode(zip_code)
    
    if zipcode_obj and zipcode_obj.lat and zipcode_obj.lng:
        coords_data.append({
            'zip_code': zip_code,
            'lat': zipcode_obj.lat,
            'lon': zipcode_obj.lng,
            'city': zipcode_obj.major_city,
            'county': zipcode_obj.county
        })
    else:
        not_found.append(zip_code)
    
    # Progress indicator
    if (idx + 1) % 100 == 0:
        print(f"   Processed {idx + 1}/{len(df)} zip codes...")

print(f"\n✅ Successfully geocoded {len(coords_data)} zip codes")
if not_found:
    print(f"⚠️  Could not find coordinates for {len(not_found)} zip codes")

# Create coordinates dataframe
coords_df = pd.DataFrame(coords_data)

# Merge with demographic data
df_merged = df.merge(coords_df[['zip_code', 'lat', 'lon']], on='zip_code', how='inner')

print(f"\n📊 Final dataset: {len(df_merged)} zip codes with accurate coordinates")

# Recalculate color scales
pop_min, pop_max = df_merged['population'].min(), df_merged['population'].max()
income_min, income_max = df_merged['median_income'].min(), df_merged['median_income'].max()
age_min, age_max = df_merged['median_age'].min(), df_merged['median_age'].max()
housing_min, housing_max = df_merged['housing_units'].min(), df_merged['housing_units'].max()
density_min, density_max = df_merged['density'].min(), df_merged['density'].max()

def get_color(value, min_val, max_val, color_scheme='green'):
    """Generate color based on value within range"""
    norm = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    norm = max(0, min(1, norm))
    
    if color_scheme == 'green':  # Income
        r = int(0 + (0-150) * norm)
        g = int(255 - (255-100) * norm)
        b = int(0)
        return f'#{max(0,r):02x}{max(0,g):02x}{b:02x}'
    elif color_scheme == 'blue':  # Population
        r = int(173 - 173 * norm)
        g = int(216 - 126 * norm)
        b = int(230 - 70 * norm)
        return f'#{r:02x}{g:02x}{b:02x}'
    elif color_scheme == 'purple':  # Density
        r = int(221 - 91 * norm)
        g = int(160 - 110 * norm)
        b = int(221 - 91 * norm)
        return f'#{r:02x}{g:02x}{b:02x}'
    elif color_scheme == 'orange':  # Age
        r = int(255)
        g = int(200 - 55 * norm)
        b = int(0)
        return f'#{r:02x}{g:02x}{b:02x}'
    elif color_scheme == 'red':  # Housing
        r = int(255)
        g = int(160 - 160 * norm)
        b = int(122 - 122 * norm)
        return f'#{r:02x}{g:02x}{b:02x}'
    return '#999999'

# Apply colors
df_merged['pop_color'] = df_merged['population'].apply(lambda x: get_color(x, pop_min, pop_max, 'blue'))
df_merged['income_color'] = df_merged['median_income'].apply(lambda x: get_color(x, income_min, income_max, 'green'))
df_merged['age_color'] = df_merged['median_age'].apply(lambda x: get_color(x, age_min, age_max, 'orange'))
df_merged['housing_color'] = df_merged['housing_units'].apply(lambda x: get_color(x, housing_min, housing_max, 'red'))
df_merged['density_color'] = df_merged['density'].apply(lambda x: get_color(x, density_min, density_max, 'purple'))

# Save
output_file = '/workspace/demographic_data_accurate_coords.csv'
df_merged.to_csv(output_file, index=False)

print(f"\n✅ Saved to: {output_file}")
print(f"\n📈 Coordinate ranges:")
print(f"   Latitude: {df_merged['lat'].min():.4f} to {df_merged['lat'].max():.4f}")
print(f"   Longitude: {df_merged['lon'].min():.4f} to {df_merged['lon'].max():.4f}")
print("\n" + "=" * 70)
