#!/usr/bin/env python3
"""
Create enhanced interactive map with demographic overlays
"""

import pandas as pd
import json

print("🗺️  Creating enhanced interactive map with demographic overlays...")
print("=" * 70)

# Read the demographic data
df = pd.read_csv('/workspace/demographic_data.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes with demographic data")

# We need to get approximate coordinates for zip codes
# Using a simple geocoding approach based on zip code ranges and known locations

def estimate_zip_coordinates(zip_code, state):
    """
    Estimate coordinates based on zip code and state
    This is a simplified approach - in production, use a geocoding API
    """
    zip_code = str(zip_code).zfill(5)  # Ensure it's a string with leading zeros
    zip_num = int(zip_code)
    
    if state == 'NJ':
        # NJ ranges from ~07xxx (north) to 08xxx (south/central)
        if zip_code.startswith('070') or zip_code.startswith('071') or zip_code.startswith('072'):
            # North Jersey (near NYC)
            lat = 40.8 + (zip_num % 100) * 0.01
            lon = -74.2 - (zip_num % 50) * 0.01
        elif zip_code.startswith('073') or zip_code.startswith('074') or zip_code.startswith('075'):
            # Central/North
            lat = 40.6 + (zip_num % 100) * 0.01
            lon = -74.4 - (zip_num % 50) * 0.01
        elif zip_code.startswith('076') or zip_code.startswith('077'):
            # Central
            lat = 40.3 + (zip_num % 100) * 0.01
            lon = -74.6 - (zip_num % 50) * 0.01
        else:
            # South Jersey
            lat = 39.8 + (zip_num % 100) * 0.01
            lon = -74.8 - (zip_num % 50) * 0.01
            
    elif state == 'DE':
        # Delaware
        lat = 39.5 + (zip_num % 100) * 0.02
        lon = -75.5 - (zip_num % 50) * 0.01
        
    elif state == 'PA':
        if zip_code.startswith('190') or zip_code.startswith('191'):
            # Philadelphia
            lat = 39.95 + (zip_num % 100) * 0.005
            lon = -75.16 - (zip_num % 50) * 0.005
        elif zip_code.startswith('189') or zip_code.startswith('193') or zip_code.startswith('194'):
            # Suburban Philly
            lat = 40.0 + (zip_num % 100) * 0.01
            lon = -75.3 - (zip_num % 50) * 0.01
        elif zip_code.startswith('180') or zip_code.startswith('181') or zip_code.startswith('182'):
            # Lehigh Valley
            lat = 40.6 + (zip_num % 100) * 0.008
            lon = -75.4 - (zip_num % 50) * 0.008
        elif zip_code.startswith('183') or zip_code.startswith('184') or zip_code.startswith('186'):
            # Poconos/NEPA
            lat = 41.0 + (zip_num % 100) * 0.008
            lon = -75.6 - (zip_num % 50) * 0.008
        else:
            # Reading area
            lat = 40.3 + (zip_num % 100) * 0.01
            lon = -75.9 - (zip_num % 50) * 0.01
    
    return lat, lon

print("📍 Estimating zip code coordinates...")
df[['lat', 'lon']] = df.apply(lambda row: pd.Series(estimate_zip_coordinates(row['zip_code'], row['state'])), axis=1)

# Create color scales for each metric
def get_color(value, min_val, max_val, color_scheme='green'):
    """Generate color based on value within range"""
    # Normalize value to 0-1
    norm = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    norm = max(0, min(1, norm))  # Clamp to 0-1
    
    if color_scheme == 'green':  # For income
        # Light green to dark green
        r = int(0 + (0-150) * norm)
        g = int(255 - (255-100) * norm)
        b = int(0)
        return f'#{max(0,r):02x}{max(0,g):02x}{b:02x}'
    
    elif color_scheme == 'blue':  # For population
        # Light blue to dark blue
        r = int(173 - 173 * norm)
        g = int(216 - 126 * norm)
        b = int(230 - 70 * norm)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    elif color_scheme == 'purple':  # For density
        # Light purple to dark purple
        r = int(221 - 91 * norm)
        g = int(160 - 110 * norm)
        b = int(221 - 91 * norm)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    elif color_scheme == 'orange':  # For age
        # Light orange to dark orange
        r = int(255)
        g = int(200 - 55 * norm)
        b = int(0)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    elif color_scheme == 'red':  # For housing
        # Light red to dark red
        r = int(255)
        g = int(160 - 160 * norm)
        b = int(122 - 122 * norm)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    return '#999999'

# Calculate min/max for color scaling
pop_min, pop_max = df['population'].min(), df['population'].max()
income_min, income_max = df['median_income'].min(), df['median_income'].max()
age_min, age_max = df['median_age'].min(), df['median_age'].max()
housing_min, housing_max = df['housing_units'].min(), df['housing_units'].max()
density_min, density_max = df['density'].min(), df['density'].max()

print("📊 Calculating color scales for each metric...")
print(f"   Population: {pop_min:,} - {pop_max:,}")
print(f"   Income: ${income_min:,} - ${income_max:,}")
print(f"   Age: {age_min} - {age_max}")
print(f"   Housing: {housing_min:,} - {housing_max:,}")
print(f"   Density: {density_min:,} - {density_max:,} per sq mi")

# Assign colors
df['pop_color'] = df['population'].apply(lambda x: get_color(x, pop_min, pop_max, 'blue'))
df['income_color'] = df['median_income'].apply(lambda x: get_color(x, income_min, income_max, 'green'))
df['age_color'] = df['median_age'].apply(lambda x: get_color(x, age_min, age_max, 'orange'))
df['housing_color'] = df['housing_units'].apply(lambda x: get_color(x, housing_min, housing_max, 'red'))
df['density_color'] = df['density'].apply(lambda x: get_color(x, density_min, density_max, 'purple'))

# Save enhanced data
output_file = '/workspace/demographic_data_with_coords.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ Enhanced data saved to: {output_file}")
print(f"📊 Total zip codes with coordinates and colors: {len(df)}")
print("\n" + "=" * 70)
