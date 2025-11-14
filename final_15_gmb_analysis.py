#!/usr/bin/env python3
"""
Complete GMB Analysis for 15 CURRENT Locations Only (excluding prospective)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

# 15 CURRENT GMB LOCATIONS (excluding prospective)
# Based on data volume, excluding Mount Laurel and Langhorne as they appear to be prospective (minimal data)
gmb_locations = [
    {'name': 'Hillsborough Township, NJ', 'lat': 40.4990, 'lon': -74.6362, 'opened': None},
    {'name': 'Pennington, NJ', 'lat': 40.3071, 'lon': -74.7985, 'opened': None},
    {'name': 'Lindenwold, NJ', 'lat': 39.8221, 'lon': -74.9957, 'opened': None},
    {'name': 'Bethlehem, PA', 'lat': 40.6810, 'lon': -75.3620, 'opened': None},
    {'name': 'North Wales, PA', 'lat': 40.2281, 'lon': -75.2814, 'opened': None},
    {'name': 'West Chester, PA', 'lat': 39.9852, 'lon': -75.5938, 'opened': None},
    {'name': 'Wilmington, DE', 'lat': 39.7614, 'lon': -75.5532, 'opened': None},
    {'name': 'Doylestown, PA', 'lat': 40.3118, 'lon': -75.1355, 'opened': None},
    {'name': 'Allentown, PA', 'lat': 40.6080, 'lon': -75.4900, 'opened': None},
    {'name': 'South Philadelphia, PA', 'lat': 39.9231, 'lon': -75.1753, 'opened': None},
    {'name': 'Media, PA', 'lat': 39.9168, 'lon': -75.3877, 'opened': None},
    {'name': 'NE Philadelphia, PA', 'lat': 40.0601, 'lon': -75.0850, 'opened': None},
    {'name': 'Trenton, NJ', 'lat': 40.2171, 'lon': -74.7429, 'opened': None},
    {'name': 'Lancaster, PA', 'lat': 40.0379, 'lon': -76.3055, 'opened': None},
    {'name': 'Bowmansville, PA', 'lat': 40.2057, 'lon': -76.0167, 'opened': None},
]

print("="*100)
print("🏢 COMPLETE GMB ANALYSIS - 15 CURRENT LOCATIONS")
print("="*100)
print(f"\nTotal Current GMB Locations: {len(gmb_locations)}")
print("(Excluding 2 prospective locations)")

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
print("🔍 INFERRING GMB OPENING DATES & FINDING NEAREST ZIP CODES")
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
        
        # Find year with significant spike (>50% increase from previous year)
        inferred_year = None
        max_increase = 0
        for year in range(2004, 2024):
            if year in yearly_counts and year-1 in yearly_counts:
                prev_count = yearly_counts[year-1]
                curr_count = yearly_counts[year]
                if prev_count > 0:
                    increase = (curr_count - prev_count) / prev_count
                    if increase > 0.5 and increase > max_increase:
                        max_increase = increase
                        inferred_year = year
        
        gmb['opened'] = inferred_year if inferred_year else 'Unknown'
        gmb['nearest_zip'] = nearest_zip
        gmb['zip_distance'] = nearest_dist
        
        print(f"\n{idx+1:2d}. {gmb['name']:<30} Zip: {nearest_zip:<10} Opening: {str(gmb['opened']):<8} ({len(zip_customers):4d} all / {len(zip_google):3d} Google)")

# Calculate distances and classify all zips relative to 15 GMBs
print("\n" + "="*100)
print("📏 CALCULATING DISTANCES TO ALL 15 GMB LOCATIONS")
print("="*100)

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

print(f"\n📍 Zip Code Classification (with 15 GMB locations):")
print(f"   GMB zip codes (< 1 mile from any GMB):     {zip_coords['gmb_zip'].sum():3d} zips")
print(f"   Adjacent zip codes (1-10 miles from GMB):  {zip_coords['adjacent_zip'].sum():3d} zips")
print(f"   Control zip codes (> 10 miles from GMB):   {zip_coords['control_zip'].sum():3d} zips")
print(f"   Total:                                      {len(zip_coords):3d} zips")

# Merge back to customers
customers = customers.merge(
    zip_coords[['Postal Code', 'gmb_zip', 'adjacent_zip', 'control_zip', 'min_distance']],
    on='Postal Code',
    how='left'
)

# Calculate yearly growth statistics
print("\n" + "="*100)
print("📊 OVERALL GROWTH ANALYSIS - ALL 15 GMB LOCATIONS COMBINED")
print("="*100)

years = range(2003, 2025)

print("\n" + "─"*100)
print("ALL LEADS - Year by Year Breakdown")
print("─"*100)
print(f"{'Year':<8} {'GMB Zips':<12} {'Adjacent':<12} {'Control':<12} {'Total':<12} {'% GMB+Adj':<12}")
print("─"*100)

for year in years:
    year_data = customers[customers['year'] == year]
    gmb_count = len(year_data[year_data['gmb_zip'] == True])
    adj_count = len(year_data[year_data['adjacent_zip'] == True])
    ctrl_count = len(year_data[year_data['control_zip'] == True])
    total = gmb_count + adj_count + ctrl_count
    pct_gmb_adj = ((gmb_count + adj_count) / total * 100) if total > 0 else 0
    print(f"{year:<8} {gmb_count:<12} {adj_count:<12} {ctrl_count:<12} {total:<12} {pct_gmb_adj:<11.1f}%")

print("\n" + "─"*100)
print("GOOGLE LEADS - Year by Year Breakdown")
print("─"*100)
print(f"{'Year':<8} {'GMB Zips':<12} {'Adjacent':<12} {'Control':<12} {'Total':<12} {'% GMB+Adj':<12}")
print("─"*100)

google_customers = customers[customers['is_google'] == True]
for year in years:
    year_data = google_customers[google_customers['year'] == year]
    gmb_count = len(year_data[year_data['gmb_zip'] == True])
    adj_count = len(year_data[year_data['adjacent_zip'] == True])
    ctrl_count = len(year_data[year_data['control_zip'] == True])
    total = gmb_count + adj_count + ctrl_count
    pct_gmb_adj = ((gmb_count + adj_count) / total * 100) if total > 0 else 0
    print(f"{year:<8} {gmb_count:<12} {adj_count:<12} {ctrl_count:<12} {total:<12} {pct_gmb_adj:<11.1f}%")

# Summary statistics
pre_2018 = customers[customers['year'] < 2018]
post_2018 = customers[customers['year'] >= 2018]

pre_years = 2018 - 2003
post_years = 2024 - 2018 + 1

print("\n" + "="*100)
print("📈 SUMMARY: PRE-2018 vs POST-2018 COMPARISON")
print("="*100)

categories = [
    ('GMB Zip Codes', 'gmb_zip'),
    ('Adjacent Zips (1-10mi)', 'adjacent_zip'),
    ('Control Zips (>10mi)', 'control_zip')
]

print("\n🔵 ALL LEADS:")
print("─"*100)
print(f"{'Category':<25} {'Pre-2018 (avg/yr)':<20} {'Post-2018 (avg/yr)':<20} {'Growth Rate':<15}")
print("─"*100)
for label, col in categories:
    pre = len(pre_2018[pre_2018[col] == True])
    post = len(post_2018[post_2018[col] == True])
    pre_avg = pre / pre_years
    post_avg = post / post_years
    growth = ((post_avg / pre_avg) - 1) * 100 if pre_avg > 0 else 0
    
    print(f"{label:<25} {pre_avg:>18.1f}  {post_avg:>18.1f}  {growth:>13.1f}%")

print("\n🟢 GOOGLE LEADS:")
print("─"*100)
print(f"{'Category':<25} {'Pre-2018 (avg/yr)':<20} {'Post-2018 (avg/yr)':<20} {'Growth Rate':<15}")
print("─"*100)
google_pre = pre_2018[pre_2018['is_google'] == True]
google_post = post_2018[post_2018['is_google'] == True]

for label, col in categories:
    pre = len(google_pre[google_pre[col] == True])
    post = len(google_post[google_post[col] == True])
    pre_avg = pre / pre_years
    post_avg = post / post_years
    growth = ((post_avg / pre_avg) - 1) * 100 if pre_avg > 0 else 0
    
    print(f"{label:<25} {pre_avg:>18.1f}  {post_avg:>18.1f}  {growth:>13.1f}%")

# Individual GMB performance with better formatting
print("\n" + "="*100)
print("🏢 INDIVIDUAL GMB LOCATION PERFORMANCE")
print("="*100)

# Sort by total customers
gmb_performance = []
for gmb in gmb_locations:
    if gmb.get('nearest_zip'):
        zip_cust = customers[customers['Postal Code'] == gmb['nearest_zip']]
        zip_google = zip_cust[zip_cust['is_google'] == True]
        
        perf = {
            'name': gmb['name'],
            'zip': gmb['nearest_zip'],
            'opened': gmb['opened'],
            'total': len(zip_cust),
            'google': len(zip_google)
        }
        
        if gmb['opened'] and gmb['opened'] != 'Unknown':
            pre = zip_cust[zip_cust['year'] < gmb['opened']]
            post = zip_cust[zip_cust['year'] >= gmb['opened']]
            pre_g = zip_google[zip_google['year'] < gmb['opened']]
            post_g = zip_google[zip_google['year'] >= gmb['opened']]
            
            perf['pre_all'] = len(pre)
            perf['post_all'] = len(post)
            perf['pre_google'] = len(pre_g)
            perf['post_google'] = len(post_g)
            perf['all_growth'] = ((len(post)/len(pre))-1)*100 if len(pre) > 0 else 0
            perf['google_growth'] = ((len(post_g)/len(pre_g))-1)*100 if len(pre_g) > 0 else 0
        
        gmb_performance.append(perf)

# Sort by total customers descending
gmb_performance.sort(key=lambda x: x['total'], reverse=True)

print("\n📊 Ranked by Total Customer Volume:")
print("─"*100)
print(f"{'Rank':<6} {'Location':<30} {'Zip':<10} {'Opened':<10} {'Total':<10} {'Google':<10}")
print("─"*100)

for idx, perf in enumerate(gmb_performance, 1):
    print(f"{idx:<6} {perf['name']:<30} {perf['zip']:<10} {str(perf['opened']):<10} {perf['total']:<10} {perf['google']:<10}")

print("\n📈 Growth Analysis (Before vs After Opening):")
print("─"*100)
print(f"{'Location':<30} {'Opened':<10} {'Before':<15} {'After':<15} {'All Growth':<15} {'Google Growth':<15}")
print("─"*100)

for perf in gmb_performance:
    if 'pre_all' in perf:
        print(f"{perf['name']:<30} {str(perf['opened']):<10} {perf['pre_all']:<7} all     {perf['post_all']:<7} all     {perf['all_growth']:>12.1f}%  {perf['google_growth']:>12.1f}%")

print("\n" + "="*100)
print("✅ ANALYSIS COMPLETE - 15 CURRENT GMB LOCATIONS")
print("="*100)
print("\n💡 Note: Opening dates were inferred from customer data patterns.")
print("   Please provide actual GMB opening dates for more accurate analysis.")
