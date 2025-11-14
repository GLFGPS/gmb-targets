#!/usr/bin/env python3
"""
Check customer counts within 5-mile radius of Langhorne and Mount Laurel
"""

import pandas as pd
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

gmb_locations = [
    {'name': 'Langhorne, PA', 'lat': 40.1856, 'lon': -74.8804},
    {'name': 'Mount Laurel Township, NJ', 'lat': 39.9368, 'lon': -74.9527},
]

print("="*100)
print("🔍 DETAILED ANALYSIS: Langhorne & Mount Laurel 5-Mile Radius")
print("="*100)

# Load customers
customers = pd.read_csv('customer_locations.csv')
customers.columns = customers.columns.str.strip()
customers['Customer Since'] = pd.to_datetime(customers['Customer Since'], errors='coerce')
customers['year'] = customers['Customer Since'].dt.year
customers = customers[customers['year'].notna()]
customers['is_google'] = customers['Customer Source (GreenLawn)'].str.lower().str.contains(
    'google|gmb|my business', na=False
)

# Get zip coordinates
zip_coords = customers.groupby('Postal Code').agg({
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()

for gmb in gmb_locations:
    print(f"\n{'='*100}")
    print(f"📍 {gmb['name']}")
    print(f"   Coordinates: {gmb['lat']:.4f}, {gmb['lon']:.4f}")
    print(f"{'='*100}")
    
    # Find all zips within 5 miles
    zips_in_radius = []
    for _, row in zip_coords.iterrows():
        try:
            dist = geodesic(
                (row['Latitude'], row['Longitude']),
                (gmb['lat'], gmb['lon'])
            ).miles
            if dist <= 5:
                zips_in_radius.append({
                    'zip': row['Postal Code'],
                    'lat': row['Latitude'],
                    'lon': row['Longitude'],
                    'distance': dist
                })
        except:
            pass
    
    # Sort by distance
    zips_in_radius.sort(key=lambda x: x['distance'])
    
    print(f"\n📊 ZIPS WITHIN 5 MILES: {len(zips_in_radius)} total")
    print("─"*100)
    print(f"{'Zip Code':<15} {'Distance':<12} {'Total Cust':<12} {'Google':<12} {'2024':<12} {'2025':<12}")
    print("─"*100)
    
    total_customers = 0
    total_google = 0
    total_2024 = 0
    total_2025 = 0
    
    for zip_info in zips_in_radius:
        zip_code = zip_info['zip']
        dist = zip_info['distance']
        
        # Get customers in this zip
        zip_cust = customers[customers['Postal Code'] == zip_code]
        zip_google = zip_cust[zip_cust['is_google'] == True]
        zip_2024 = zip_cust[zip_cust['year'] == 2024]
        zip_2025 = zip_cust[zip_cust['year'] == 2025]
        
        print(f"{zip_code:<15} {dist:>10.2f}mi  {len(zip_cust):<12} {len(zip_google):<12} {len(zip_2024):<12} {len(zip_2025):<12}")
        
        total_customers += len(zip_cust)
        total_google += len(zip_google)
        total_2024 += len(zip_2024)
        total_2025 += len(zip_2025)
    
    print("─"*100)
    print(f"{'TOTAL':<15} {'':>12}  {total_customers:<12} {total_google:<12} {total_2024:<12} {total_2025:<12}")
    print("─"*100)
    
    print(f"\n💡 SUMMARY:")
    print(f"   Total customers within 5 miles: {total_customers:,}")
    print(f"   Google leads within 5 miles: {total_google:,}")
    print(f"   2024 customers: {total_2024:,}")
    print(f"   2025 customers: {total_2025:,}")
    print(f"   Average per year (all time): {total_customers/23:.1f}")
    
    # Show year-by-year for recent years
    print(f"\n📅 RECENT YEARS (within 5-mile radius):")
    for year in [2020, 2021, 2022, 2023, 2024, 2025]:
        year_zips = [z['zip'] for z in zips_in_radius]
        year_cust = customers[(customers['Postal Code'].isin(year_zips)) & (customers['year'] == year)]
        year_google = year_cust[year_cust['is_google'] == True]
        print(f"   {year}: {len(year_cust):4d} all leads, {len(year_google):3d} Google leads")

print("\n" + "="*100)
print("✅ ANALYSIS COMPLETE")
print("="*100)
