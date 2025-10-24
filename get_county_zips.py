#!/usr/bin/env python3
"""
Get all zip codes for specific counties
"""

import pandas as pd
import pgeocode

print("🔍 Getting all zip codes for required counties...")
print("=" * 70)

# Known zip code ranges by county (from USPS data)
# This is more reliable than programmatic lookup

county_zip_prefixes = {
    # Pennsylvania
    'PA_Berks': ['195', '196'],
    'PA_Bucks': ['189', '190'],
    'PA_Chester': ['193', '194'],
    'PA_Delaware': ['190', '191'],
    'PA_Lancaster': ['175', '176'],
    'PA_Lehigh': ['180', '181'],
    'PA_Montgomery': ['189', '190', '194'],
    'PA_Northampton': ['180', '181'],
    'PA_Philadelphia': ['190', '191'],
    
    # New Jersey
    'NJ_Atlantic': ['082', '083'],
    'NJ_Burlington': ['080', '081', '086'],
    'NJ_Camden': ['080', '081'],
    'NJ_Cumberland': ['083'],
    'NJ_Gloucester': ['080', '081', '083'],
    'NJ_Hunterdon': ['088'],
    'NJ_Mercer': ['085', '086'],
    'NJ_Middlesex': ['088', '089'],
    'NJ_Monmouth': ['077', '078'],
    'NJ_Ocean': ['087', '088', '089'],
    'NJ_Somerset': ['088'],
    
    # Delaware
    'DE_Kent': ['199'],
    'DE_New Castle': ['197', '198', '199'],
}

nomi = pgeocode.Nominatim('us')

all_county_zips = []

for county_key, prefixes in county_zip_prefixes.items():
    state, county = county_key.split('_')
    print(f"\n{county} County, {state}:")
    
    county_zips = []
    
    # Generate potential zip codes from prefixes
    for prefix in prefixes:
        # Try all 2-digit suffixes
        for suffix in range(100):
            zip_code = f"{prefix}{suffix:02d}"
            
            # Lookup this zip code
            result = nomi.query_postal_code(zip_code)
            
            if pd.notna(result.latitude) and pd.notna(result.longitude):
                # Check if state matches
                if result.state_code == state:
                    county_zips.append(zip_code)
                    all_county_zips.append({
                        'zip_code': zip_code,
                        'state': state,
                        'county': county,
                        'lat': result.latitude,
                        'lon': result.longitude,
                        'city': result.place_name
                    })
    
    print(f"  Found {len(county_zips)} zip codes")

print("\n" + "=" * 70)
print(f"\n✅ Total zip codes found: {len(all_county_zips)}")

# Save
df = pd.DataFrame(all_county_zips)
df.to_csv('/workspace/all_county_zips.csv', index=False)

# Summary by state
print("\nBreakdown by state:")
for state in ['PA', 'NJ', 'DE']:
    count = len(df[df['state'] == state])
    print(f"  {state}: {count} zip codes")

print(f"\n✅ Saved to: all_county_zips.csv")
print("=" * 70)
