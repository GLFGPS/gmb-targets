#!/usr/bin/env python3
"""
Fix zip code coordinates using pgeocode
"""

import pandas as pd
import pgeocode

print("🗺️  Fixing zip code coordinates with pgeocode...")
print("=" * 70)

# Initialize geocoder for US
nomi = pgeocode.Nominatim('us')

# Read demographic data
df = pd.read_csv('/workspace/demographic_data.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes")

print("📍 Geocoding zip codes...")

# Get coordinates
coords_list = []
for idx, row in df.iterrows():
    zip_code = row['zip_code']
    
    # Query the zip code
    result = nomi.query_postal_code(zip_code)
    
    if pd.notna(result.latitude) and pd.notna(result.longitude):
        coords_list.append({
            'zip_code': zip_code,
            'lat': result.latitude,
            'lon': result.longitude
        })
    
    if (idx + 1) % 100 == 0:
        print(f"   Processed {idx + 1}/{len(df)}...")

print(f"\n✅ Successfully geocoded {len(coords_list)} zip codes")

# Create dataframe and merge
coords_df = pd.DataFrame(coords_list)
df_merged = df.merge(coords_df, on='zip_code', how='inner')

print(f"📊 Final dataset: {len(df_merged)} zip codes with accurate coordinates")

# Add colors
def get_color(value, min_val, max_val, color_scheme='green'):
    norm = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    norm = max(0, min(1, norm))
    
    if color_scheme == 'green':
        r, g, b = int(0 + (0-150) * norm), int(255 - (255-100) * norm), 0
    elif color_scheme == 'blue':
        r, g, b = int(173 - 173 * norm), int(216 - 126 * norm), int(230 - 70 * norm)
    elif color_scheme == 'purple':
        r, g, b = int(221 - 91 * norm), int(160 - 110 * norm), int(221 - 91 * norm)
    elif color_scheme == 'orange':
        r, g, b = 255, int(200 - 55 * norm), 0
    elif color_scheme == 'red':
        r, g, b = 255, int(160 - 160 * norm), int(122 - 122 * norm)
    else:
        return '#999999'
    
    return f'#{max(0,r):02x}{max(0,g):02x}{max(0,b):02x}'

# Calculate ranges and apply colors
for col, scheme in [('population', 'blue'), ('median_income', 'green'), 
                     ('median_age', 'orange'), ('housing_units', 'red'), 
                     ('density', 'purple')]:
    min_val, max_val = df_merged[col].min(), df_merged[col].max()
    color_col = col.split('_')[0] if '_' in col else col
    if col == 'median_income':
        color_col = 'income'
    elif col == 'median_age':
        color_col = 'age'
    elif col == 'housing_units':
        color_col = 'housing'
    elif col == 'population':
        color_col = 'pop'
    
    df_merged[f'{color_col}_color'] = df_merged[col].apply(
        lambda x: get_color(x, min_val, max_val, scheme)
    )

# Save
output_file = '/workspace/demographic_data_accurate_coords.csv'
df_merged.to_csv(output_file, index=False)

print(f"\n✅ Saved to: {output_file}")
print(f"\n📈 Coordinate ranges:")
print(f"   Latitude: {df_merged['lat'].min():.4f} to {df_merged['lat'].max():.4f}")
print(f"   Longitude: {df_merged['lon'].min():.4f} to {df_merged['lon'].max():.4f}")
print("\n" + "=" * 70)
