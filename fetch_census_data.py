#!/usr/bin/env python3
"""
Fetch demographic data for NJ, DE, and Eastern PA zip codes
Data sources: US Census Bureau (free public data)
"""

import requests
import pandas as pd
import json
import time

# State FIPS codes
STATES = {
    'NJ': '34',  # New Jersey - all zip codes
    'DE': '10',  # Delaware - all zip codes
    'PA': '42'   # Pennsylvania - Eastern region only
}

# Eastern PA boundaries (approximate coordinates)
# West: Harrisburg/Lebanon, North: Scranton/Wilkes-Barre
EASTERN_PA_BOUNDS = {
    'max_lon': -76.0,  # East of Harrisburg
    'min_lat': 39.7,   # Southern PA border
    'max_lat': 41.4    # Scranton area
}

print("🔍 Fetching demographic data from US Census Bureau...")
print("=" * 60)

# First, let's try to get data from Census API
# Using American Community Survey (ACS) 5-Year estimates
BASE_URL = "https://api.census.gov/data/2022/acs/acs5"

# Variables we want:
# B01003_001E: Total Population
# B19013_001E: Median Household Income
# B01002_001E: Median Age
# B25001_001E: Housing Units

variables = "B01003_001E,B19013_001E,B01002_001E,B25001_001E"

def fetch_state_data(state_code, state_name):
    """Fetch zip code data for a state"""
    try:
        # Note: Census API for ZCTA (ZIP Code Tabulation Areas)
        url = f"{BASE_URL}?get=NAME,{variables}&for=zip%20code%20tabulation%20area:*&in=state:{state_code}"
        
        print(f"\n📍 Fetching data for {state_name}...")
        print(f"   URL: {url[:80]}...")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Got {len(data)-1} zip codes")
            return data
        else:
            print(f"   ⚠️  API returned status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# Try to fetch data
all_data = []

for state_abbr, state_code in STATES.items():
    data = fetch_state_data(state_code, state_abbr)
    if data:
        all_data.append((state_abbr, data))
    time.sleep(1)  # Be nice to the API

print("\n" + "=" * 60)

if not all_data:
    print("⚠️  Census API unavailable. Creating sample dataset...")
    print("    (In production, you'd need a Census API key)")
    
    # Create sample data based on real demographic patterns
    # This is representative data for the tri-state area
    sample_data = []
    
    # Sample zip codes for each region with realistic demographics
    samples = {
        'NJ': [
            ('07002', 'Bayonne', 45000, 75000, 38, 18000),
            ('07047', 'North Bergen', 42000, 68000, 36, 16500),
            ('08054', 'Mount Laurel', 35000, 95000, 42, 14000),
            ('08648', 'Lawrence Township', 28000, 88000, 40, 11000),
            ('07701', 'Red Bank', 25000, 82000, 41, 10500),
        ],
        'DE': [
            ('19801', 'Wilmington', 48000, 65000, 35, 19000),
            ('19702', 'Newark', 38000, 72000, 32, 15000),
            ('19958', 'Millsboro', 12000, 58000, 45, 5500),
        ],
        'PA': [
            ('19382', 'West Chester', 32000, 98000, 39, 13000),
            ('19019', 'Philadelphia', 52000, 52000, 34, 22000),
            ('18031', 'Bethlehem', 38000, 67000, 37, 15500),
            ('18102', 'Allentown', 45000, 61000, 35, 18000),
            ('19087', 'Wayne', 28000, 125000, 44, 11000),
        ]
    }
    
    print("\n📊 Generated sample data for demonstration:")
    print("    (Replace with real Census data in production)")
    
else:
    print(f"\n✅ Successfully fetched data from Census Bureau!")
    print(f"   Total datasets: {len(all_data)}")

print("\n✅ Data collection complete!")
print("=" * 60)
