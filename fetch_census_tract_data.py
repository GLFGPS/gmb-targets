#!/usr/bin/env python3
"""
Fetch census tract boundaries and demographic data for NJ, DE, and PA counties
"""

import requests
import pandas as pd
import json
import time

print("🏛️ Fetching Census Tract Data from US Census Bureau")
print("=" * 70)

# Counties we need
COUNTIES = {
    'New Jersey': {
        'state_fips': '34',
        'counties': {
            'Atlantic': '001', 'Burlington': '005', 'Camden': '007',
            'Cumberland': '011', 'Gloucester': '015', 'Hunterdon': '019',
            'Mercer': '021', 'Middlesex': '023', 'Monmouth': '025',
            'Ocean': '029', 'Somerset': '035'
        }
    },
    'Delaware': {
        'state_fips': '10',
        'counties': {
            'Kent': '001', 'New Castle': '003'
        }
    },
    'Pennsylvania': {
        'state_fips': '42',
        'counties': {
            'Berks': '011', 'Bucks': '017', 'Chester': '029',
            'Delaware': '045', 'Lancaster': '071', 'Lehigh': '077',
            'Montgomery': '091', 'Northampton': '095', 'Philadelphia': '101'
        }
    }
}

# ACS 5-Year 2022 variables (most recent census tract level data)
VARIABLES = {
    'B01003_001E': 'population',           # Total Population
    'B19013_001E': 'median_income',        # Median Household Income
    'B01002_001E': 'median_age',           # Median Age
    'B25001_001E': 'housing_units',        # Total Housing Units
    'B25077_001E': 'median_home_value',    # Median Home Value (Owner-Occupied)
}

all_tracts = []

print("\n📊 Fetching demographic data from ACS 2022 5-Year...")

for state_name, state_info in COUNTIES.items():
    state_fips = state_info['state_fips']
    
    for county_name, county_fips in state_info['counties'].items():
        print(f"   Fetching {county_name} County, {state_name}...")
        
        # Build ACS API query
        var_string = ','.join(VARIABLES.keys())
        url = f"https://api.census.gov/data/2022/acs/acs5"
        params = {
            'get': f"NAME,{var_string}",
            'for': 'tract:*',
            'in': f'state:{state_fips} county:{county_fips}'
        }
        
        try:
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200:
                data = response.json()
                headers = data[0]
                rows = data[1:]
                
                for row in rows:
                    tract_data = dict(zip(headers, row))
                    
                    # Create GEOID (state + county + tract)
                    tract_data['geoid'] = tract_data['state'] + tract_data['county'] + tract_data['tract']
                    tract_data['county_name'] = county_name
                    tract_data['state_name'] = state_name
                    
                    # Rename variables to friendly names
                    for var_code, var_name in VARIABLES.items():
                        if var_code in tract_data:
                            value = tract_data[var_code]
                            # Handle null values
                            if value is None or value == '' or value == '-666666666':
                                tract_data[var_name] = None
                            else:
                                try:
                                    tract_data[var_name] = float(value)
                                except:
                                    tract_data[var_name] = None
                    
                    all_tracts.append(tract_data)
                
                print(f"      ✅ Got {len(rows)} tracts")
            else:
                print(f"      ❌ Failed: {response.status_code}")
            
            time.sleep(0.2)  # Be nice to Census API
            
        except Exception as e:
            print(f"      ❌ Error: {e}")

print(f"\n📦 Total tracts collected: {len(all_tracts)}")

# Create DataFrame
df = pd.DataFrame(all_tracts)

# Calculate population density (need to get area from TIGER/Line)
print("\n🗺️ Fetching tract boundaries from TIGER/Line...")

# We'll get boundaries from Census TIGER/Line API
tract_boundaries = {}

for state_name, state_info in COUNTIES.items():
    state_fips = state_info['state_fips']
    
    for county_name, county_fips in state_info['counties'].items():
        print(f"   Fetching boundaries for {county_name}, {state_name}...")
        
        # TIGER/Line GeoJSON API
        url = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/8/query"
        params = {
            'where': f"STATE='{state_fips}' AND COUNTY='{county_fips}'",
            'outFields': 'GEOID,AREALAND,NAME',
            'outSR': '4326',
            'f': 'geojson'
        }
        
        try:
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200:
                geojson = response.json()
                
                for feature in geojson.get('features', []):
                    geoid = feature['properties']['GEOID']
                    # Normalize GEOID to 11 digits (remove extra block digit if present)
                    if len(geoid) == 12:
                        geoid = geoid[:11]
                    arealand = float(feature['properties']['AREALAND'])  # in square meters
                    
                    tract_boundaries[geoid] = {
                        'geometry': feature['geometry'],
                        'area_sqm': arealand,
                        'area_sqmi': arealand / 2589988.11  # Convert to square miles
                    }
                
                print(f"      ✅ Got {len(geojson.get('features', []))} boundaries")
            else:
                print(f"      ❌ Failed: {response.status_code}")
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"      ❌ Error: {e}")

print(f"\n📐 Total boundaries collected: {len(tract_boundaries)}")

# Debug: Check GEOID formats
if len(df) > 0 and len(tract_boundaries) > 0:
    sample_df_geoid = df['geoid'].iloc[0]
    sample_boundary_geoid = list(tract_boundaries.keys())[0]
    print(f"\n🔍 Debug - GEOID formats:")
    print(f"   Data GEOID example: {sample_df_geoid} (len: {len(sample_df_geoid)})")
    print(f"   Boundary GEOID example: {sample_boundary_geoid} (len: {len(sample_boundary_geoid)})")

# Add boundaries and calculate density
df['geometry'] = None
df['area_sqmi'] = None
df['density'] = None

matches = 0
for idx, row in df.iterrows():
    geoid = row['geoid']
    if geoid in tract_boundaries:
        boundary_info = tract_boundaries[geoid]
        df.at[idx, 'geometry'] = json.dumps(boundary_info['geometry'])
        df.at[idx, 'area_sqmi'] = boundary_info['area_sqmi']
        matches += 1
        
        # Calculate population density
        if pd.notna(row['population']) and boundary_info['area_sqmi'] > 0:
            df.at[idx, 'density'] = row['population'] / boundary_info['area_sqmi']

print(f"\n✅ Matched {matches} tracts with boundaries")

# Clean up data - remove tracts with missing critical data
print("\n🧹 Cleaning data...")
initial_count = len(df)

# Keep only tracts with geometry and at least some demographic data
df = df[df['geometry'].notna()]
df = df.dropna(subset=['population', 'median_income'], how='all')

print(f"   Removed {initial_count - len(df)} tracts with missing data")
print(f"   Final tract count: {len(df)}")

# Save to CSV
output_file = '/workspace/census_tract_demographics.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ Data saved to: {output_file}")
print("\n📊 Summary Statistics:")
print(f"   Population: {df['population'].min():.0f} - {df['population'].max():.0f}")
print(f"   Income: ${df['median_income'].min():.0f} - ${df['median_income'].max():.0f}")
print(f"   Home Value: ${df['median_home_value'].min():.0f} - ${df['median_home_value'].max():.0f}")
print(f"   Age: {df['median_age'].min():.1f} - {df['median_age'].max():.1f}")
print(f"   Density: {df['density'].min():.0f} - {df['density'].max():.0f} per sq mi")
print("=" * 70)
