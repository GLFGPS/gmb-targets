#!/usr/bin/env python3
"""
Complete GMB Analysis for All 17 Locations
Infer opening dates from customer data patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

# ALL 17 CURRENT GMB LOCATIONS
gmb_locations = [
    {'name': 'Hillsborough Township, NJ', 'lat': 40.4990, 'lon': -74.6362, 'opened': None},
    {'name': 'Pennington, NJ', 'lat': 40.3071, 'lon': -74.7985, 'opened': None},
    {'name': 'Lindenwold, NJ', 'lat': 39.8221, 'lon': -74.9957, 'opened': None},
    {'name': 'Bethlehem, PA', 'lat': 40.6810, 'lon': -75.3620, 'opened': None},
    {'name': 'North Wales, PA', 'lat': 40.2281, 'lon': -75.2814, 'opened': None},
    {'name': 'West Chester, PA', 'lat': 39.9852, 'lon': -75.5938, 'opened': None},
    {'name': 'Wilmington, DE', 'lat': 39.7614, 'lon': -75.5532, 'opened': None},
    {'name': 'Mount Laurel Township, NJ', 'lat': 39.9368, 'lon': -74.9527, 'opened': None},
    {'name': 'Doylestown, PA', 'lat': 40.3118, 'lon': -75.1355, 'opened': None},
    {'name': 'Langhorne, PA', 'lat': 40.1856, 'lon': -74.8804, 'opened': None},
    {'name': 'Allentown, PA', 'lat': 40.6080, 'lon': -75.4900, 'opened': None},
    {'name': 'South Philadelphia, PA', 'lat': 39.9231, 'lon': -75.1753, 'opened': None},
    {'name': 'Media, PA', 'lat': 39.9168, 'lon': -75.3877, 'opened': None},
    {'name': 'NE Philadelphia, PA', 'lat': 40.0601, 'lon': -75.0850, 'opened': None},
    {'name': 'Trenton, NJ', 'lat': 40.2171, 'lon': -74.7429, 'opened': None},
    {'name': 'Lancaster, PA', 'lat': 40.0379, 'lon': -76.3055, 'opened': None},
    {'name': 'Bowmansville, PA', 'lat': 40.2057, 'lon': -76.0167, 'opened': None},
]

print("="*100)
print("🏢 COMPLETE GMB ANALYSIS - ALL 17 LOCATIONS")
print("="*100)
print(f"\nTotal GMB Locations: {len(gmb_locations)}")

# Load customer data
print("\n📂 Loading customer data...")
customers = pd.read_csv('customer_locations.csv')
customers.columns = customers.columns.str.strip()
customers['Customer Since'] = pd.to_datetime(customers['Customer Since'], errors='coerce')
customers['year'] = customers['Customer Since'].dt.year
customers = customers[customers['year'].notna()]
customers = customers[(customers['year'] >= 2003) & (customers['year'] <= 2024)]
customers['is_google'] = customers['Customer Source (GreenLawn)'].str.lower().str.contains(
    'google|gmb|my business', na=False
)

print(f"   Total customers: {len(customers):,}")
print(f"   Google leads: {customers['is_google'].sum():,} ({customers['is_google'].mean()*100:.1f}%)")

# Get unique zip codes with coordinates
zip_coords = customers.groupby('Postal Code').agg({
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()

print(f"   Unique zip codes: {len(zip_coords)}")

# For each GMB, find the nearest zip and infer opening date
print("\n" + "="*100)
print("🔍 INFERRING GMB OPENING DATES FROM CUSTOMER DATA PATTERNS")
print("="*100)

for idx, gmb in enumerate(gmb_locations):
    # Find nearest zip code
    distances = []
    for _, row in zip_coords.iterrows():
        try:
            dist = geodesic(
                (row['Latitude'], row['Longitude']),
                (gmb['lat'], gmb['lon'])
            ).miles
            distances.append((row['Postal Code'], dist))
        except:
            pass
    
    distances.sort(key=lambda x: x[1])
    nearest_zip = distances[0][0] if distances else None
    nearest_dist = distances[0][1] if distances else 999
    
    if nearest_zip:
        # Get customer data for this zip
        zip_customers = customers[customers['Postal Code'] == nearest_zip]
        zip_google = zip_customers[zip_customers['is_google'] == True]
        
        # Analyze year-by-year growth to find spike
        yearly_counts = zip_customers.groupby('year').size().to_dict()
        yearly_google = zip_google.groupby('year').size().to_dict()
        
        # Find year with significant spike (>50% increase)
        inferred_year = None
        max_increase = 0
        for year in range(2004, 2024):
            if year in yearly_counts and year-1 in yearly_counts:
                prev_count = yearly_counts[year-1]
                curr_count = yearly_counts[year]
                if prev_count > 0:
                    increase = (curr_count - prev_count) / prev_count
                    if increase > 0.5 and increase > max_increase:  # >50% increase
                        max_increase = increase
                        inferred_year = year
        
        # Update GMB opening year
        gmb['opened'] = inferred_year if inferred_year else 'Unknown'
        gmb['nearest_zip'] = nearest_zip
        gmb['zip_distance'] = nearest_dist
        
        print(f"\n{idx+1}. {gmb['name']}")
        print(f"   Nearest Zip: {nearest_zip} ({nearest_dist:.2f} miles)")
        print(f"   Inferred Opening: {gmb['opened']}")
        print(f"   Total customers in zip: {len(zip_customers)}")
        print(f"   Google customers in zip: {len(zip_google)}")

# Now calculate distances and classify all zips
print("\n" + "="*100)
print("📏 CALCULATING DISTANCES TO ALL GMB LOCATIONS")
print("="*100)

# For each zip, find minimum distance to any GMB
min_distances = []
for _, row in zip_coords.iterrows():
    min_dist = 999
    for gmb in gmb_locations:
        try:
            dist = geodesic(
                (row['Latitude'], row['Longitude']),
                (gmb['lat'], gmb['lon'])
            ).miles
            min_dist = min(min_dist, dist)
        except:
            pass
    min_distances.append(min_dist)

zip_coords['min_distance'] = min_distances
zip_coords['gmb_zip'] = zip_coords['min_distance'] < 1
zip_coords['adjacent_zip'] = (zip_coords['min_distance'] >= 1) & (zip_coords['min_distance'] <= 10)
zip_coords['control_zip'] = zip_coords['min_distance'] > 10

print(f"\n📍 Zip Code Classification:")
print(f"   GMB zip codes (< 1 mile from any GMB): {zip_coords['gmb_zip'].sum()}")
print(f"   Adjacent zip codes (1-10 miles): {zip_coords['adjacent_zip'].sum()}")
print(f"   Control zip codes (> 10 miles): {zip_coords['control_zip'].sum()}")

# Merge back to customers
customers = customers.merge(
    zip_coords[['Postal Code', 'gmb_zip', 'adjacent_zip', 'control_zip', 'min_distance']],
    on='Postal Code',
    how='left'
)

# Calculate yearly growth statistics
print("\n" + "="*100)
print("📊 OVERALL GROWTH ANALYSIS (ALL GMB LOCATIONS COMBINED)")
print("="*100)

years = range(2003, 2025)

print("\n" + "─"*100)
print("ALL LEADS - Year by Year")
print("─"*100)
print(f"{'Year':<8} {'GMB Zips':<15} {'Adjacent Zips':<15} {'Control Zips':<15} {'Total':<15}")
print("─"*100)

for year in years:
    year_data = customers[customers['year'] == year]
    gmb_count = len(year_data[year_data['gmb_zip'] == True])
    adj_count = len(year_data[year_data['adjacent_zip'] == True])
    ctrl_count = len(year_data[year_data['control_zip'] == True])
    total = gmb_count + adj_count + ctrl_count
    print(f"{year:<8} {gmb_count:<15} {adj_count:<15} {ctrl_count:<15} {total:<15}")

print("\n" + "─"*100)
print("GOOGLE LEADS - Year by Year")
print("─"*100)
print(f"{'Year':<8} {'GMB Zips':<15} {'Adjacent Zips':<15} {'Control Zips':<15} {'Total':<15}")
print("─"*100)

google_customers = customers[customers['is_google'] == True]
for year in years:
    year_data = google_customers[google_customers['year'] == year]
    gmb_count = len(year_data[year_data['gmb_zip'] == True])
    adj_count = len(year_data[year_data['adjacent_zip'] == True])
    ctrl_count = len(year_data[year_data['control_zip'] == True])
    total = gmb_count + adj_count + ctrl_count
    print(f"{year:<8} {gmb_count:<15} {adj_count:<15} {ctrl_count:<15} {total:<15}")

# Summary statistics
pre_2018 = customers[customers['year'] < 2018]
post_2018 = customers[customers['year'] >= 2018]

pre_years = 2018 - 2003
post_years = 2024 - 2018 + 1

print("\n" + "="*100)
print("📈 SUMMARY STATISTICS (Pre-2018 vs Post-2018)")
print("="*100)

categories = [
    ('GMB Zip Codes', 'gmb_zip'),
    ('Adjacent Zip Codes', 'adjacent_zip'),
    ('Control Zip Codes', 'control_zip')
]

print("\nALL LEADS:")
print("─"*100)
for label, col in categories:
    pre = len(pre_2018[pre_2018[col] == True])
    post = len(post_2018[post_2018[col] == True])
    pre_avg = pre / pre_years
    post_avg = post / post_years
    growth = ((post_avg / pre_avg) - 1) * 100 if pre_avg > 0 else 0
    
    print(f"{label:<25} Pre: {pre_avg:>8.1f}/yr  Post: {post_avg:>8.1f}/yr  Growth: {growth:>+7.1f}%")

print("\nGOOGLE LEADS:")
print("─"*100)
google_pre = pre_2018[pre_2018['is_google'] == True]
google_post = post_2018[post_2018['is_google'] == True]

for label, col in categories:
    pre = len(google_pre[google_pre[col] == True])
    post = len(google_post[google_post[col] == True])
    pre_avg = pre / pre_years
    post_avg = post / post_years
    growth = ((post_avg / pre_avg) - 1) * 100 if pre_avg > 0 else 0
    
    print(f"{label:<25} Pre: {pre_avg:>8.1f}/yr  Post: {post_avg:>8.1f}/yr  Growth: {growth:>+7.1f}%")

# Individual GMB performance
print("\n" + "="*100)
print("🏢 INDIVIDUAL GMB LOCATION PERFORMANCE")
print("="*100)

for gmb in gmb_locations:
    if gmb.get('nearest_zip'):
        print(f"\n📍 {gmb['name']}")
        print(f"   Nearest Zip: {gmb['nearest_zip']} ({gmb['zip_distance']:.2f} miles)")
        print(f"   Inferred Opening: {gmb['opened']}")
        
        zip_cust = customers[customers['Postal Code'] == gmb['nearest_zip']]
        zip_google = zip_cust[zip_cust['is_google'] == True]
        
        if gmb['opened'] and gmb['opened'] != 'Unknown':
            pre = zip_cust[zip_cust['year'] < gmb['opened']]
            post = zip_cust[zip_cust['year'] >= gmb['opened']]
            pre_g = zip_google[zip_google['year'] < gmb['opened']]
            post_g = zip_google[zip_google['year'] >= gmb['opened']]
            
            print(f"   Before Opening: {len(pre)} all / {len(pre_g)} Google")
            print(f"   After Opening:  {len(post)} all / {len(post_g)} Google")
            if len(pre) > 0:
                print(f"   All Leads Growth: {((len(post)/len(pre))-1)*100:+.1f}%")
            if len(pre_g) > 0:
                print(f"   Google Growth: {((len(post_g)/len(pre_g))-1)*100:+.1f}%")

print("\n" + "="*100)
print("✅ COMPLETE ANALYSIS FINISHED")
print("="*100)
