#!/usr/bin/env python3
"""
Check if we have all zip codes for the required counties
"""

import pandas as pd
import pgeocode

print("🔍 Checking county coverage for all required counties...")
print("=" * 70)

# Target counties by state
target_counties = {
    'PA': [
        'Berks', 'Bucks', 'Chester', 'Delaware', 'Lancaster',
        'Lehigh', 'Montgomery', 'Northampton', 'Philadelphia'
    ],
    'NJ': [
        'Atlantic', 'Burlington', 'Camden', 'Cumberland', 'Gloucester',
        'Hunterdon', 'Mercer', 'Middlesex', 'Monmouth', 'Ocean', 'Somerset'
    ],
    'DE': [
        'Kent', 'New Castle'
    ]
}

# Initialize geocoder
nomi = pgeocode.Nominatim('us')

# Get all US zip codes
all_zips = nomi.query_postal_code('')

print(f"📊 Loaded {len(all_zips)} total US zip codes")

# Filter by state and county
found_zips = []
missing_counties = []

for state, counties in target_counties.items():
    print(f"\n{state} - Checking {len(counties)} counties:")
    
    for county in counties:
        # Filter zips for this state and county
        # Note: pgeocode uses full county names with " County" suffix
        county_filter = all_zips[
            (all_zips['state_code'] == state) & 
            (all_zips['county_name'].str.contains(county, case=False, na=False))
        ]
        
        if len(county_filter) > 0:
            found_zips.extend(county_filter['postal_code'].tolist())
            print(f"  ✅ {county} County: {len(county_filter)} zip codes")
        else:
            missing_counties.append(f"{state} - {county}")
            print(f"  ⚠️  {county} County: NO ZIP CODES FOUND")

print("\n" + "=" * 70)
print(f"\n📊 SUMMARY:")
print(f"   Total zip codes found: {len(found_zips)}")
print(f"   Counties covered: {len(target_counties['PA']) + len(target_counties['NJ']) + len(target_counties['DE']) - len(missing_counties)}")

if missing_counties:
    print(f"\n⚠️  Missing counties: {len(missing_counties)}")
    for county in missing_counties:
        print(f"      - {county}")

# Save the list of zip codes we should have
zip_df = pd.DataFrame({'zip_code': found_zips})
zip_df.to_csv('/workspace/required_zips_by_county.csv', index=False)

print(f"\n✅ Saved required zip codes to: required_zips_by_county.csv")
print("=" * 70)
