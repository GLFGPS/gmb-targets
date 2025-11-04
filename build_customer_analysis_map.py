#!/usr/bin/env python3
"""
Build Customer Analysis Map with heat maps and zip aggregations
Replaces the old zip code demographics map
"""

import folium
from folium.plugins import HeatMap
import pandas as pd
from branca.colormap import LinearColormap
import json

print("🗺️  Building Customer Analysis Map...")
print("=" * 70)

# Load customer data
print("📊 Loading customer data...")
df = pd.read_csv('/workspace/customer_locations.csv', dtype={'Postal Code': str})
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces from column names

# Clean up column data
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df['Customer Status'] = pd.to_numeric(df['Customer Status'], errors='coerce')
df['Postal Code'] = df['Postal Code'].astype(str).str.strip()

# Remove any rows with invalid coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

print(f"   Total customers loaded: {len(df):,}")

# Separate active vs all customers (status = 9.0)
df_active = df[df['Customer Status'] == 9.0].copy()
print(f"   Active customers (Status=9): {len(df_active):,}")
print(f"   Inactive customers: {len(df) - len(df_active):,}")

# Create map centered on service area
m = folium.Map(
    location=[40.0, -75.5],
    zoom_start=9,
    tiles='cartodbpositron',
    control_scale=True
)

print("\n🔥 Creating heat map layers...")

# Layer 1: Active Customer Heat Map
active_heat_data = [[row['Latitude'], row['Longitude']] for _, row in df_active.iterrows()]
active_heat_layer = folium.FeatureGroup(name='🔥 Active Customer Heat Map', show=False)
HeatMap(
    active_heat_data,
    radius=12,
    blur=15,
    max_zoom=13,
    min_opacity=0.4,
    gradient={0.0: 'navy', 0.25: 'blue', 0.5: 'cyan', 0.65: 'yellow', 0.8: 'orange', 1.0: 'red'}
).add_to(active_heat_layer)
active_heat_layer.add_to(m)
print(f"   ✅ Active customer heat map: {len(active_heat_data):,} points")

# Layer 2: All Customer Heat Map
all_heat_data = [[row['Latitude'], row['Longitude']] for _, row in df.iterrows()]
all_heat_layer = folium.FeatureGroup(name='🔥 All Customer Heat Map', show=False)
HeatMap(
    all_heat_data,
    radius=12,
    blur=15,
    max_zoom=13,
    min_opacity=0.4,
    gradient={0.0: 'darkblue', 0.25: 'blue', 0.5: 'cyan', 0.65: 'lime', 0.8: 'yellow', 1.0: 'red'}
).add_to(all_heat_layer)
all_heat_layer.add_to(m)
print(f"   ✅ All customer heat map: {len(all_heat_data):,} points")

print("\n📊 Aggregating customers by ZIP code...")

# Aggregate active customers by zip
active_zip_counts = df_active.groupby('Postal Code').size().reset_index(name='count')
active_zip_coords = df_active.groupby('Postal Code').agg({
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()
active_zip_data = active_zip_coords.merge(active_zip_counts, on='Postal Code')
print(f"   Active customers: {len(active_zip_data)} zip codes")

# Aggregate all customers by zip
all_zip_counts = df.groupby('Postal Code').size().reset_index(name='count')
all_zip_coords = df.groupby('Postal Code').agg({
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()
all_zip_data = all_zip_coords.merge(all_zip_counts, on='Postal Code')
print(f"   All customers: {len(all_zip_data)} zip codes")

print("\n🎨 Creating ZIP aggregation layers...")

# Layer 3: Active Customers by Zip
active_zip_layer = folium.FeatureGroup(name='📊 Active Customers by Zip', show=True)

# Create colormap for active customers
max_active = active_zip_data['count'].max()
active_colormap = LinearColormap(
    colors=['#FFF5E6', '#FF8C00', '#CC5500'],  # Light to dark orange
    vmin=0,
    vmax=max_active
)

for _, row in active_zip_data.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=min(3 + (row['count'] / 50), 20),  # Size based on count
        color='#000000',
        fillColor=active_colormap(row['count']),
        fillOpacity=0.7,
        weight=1,
        popup=f"<b>Zip: {row['Postal Code']}</b><br>Active Customers: {int(row['count'])}"
    ).add_to(active_zip_layer)

active_zip_layer.add_to(m)
print(f"   ✅ Active customers by zip: {len(active_zip_data)} zip codes visualized")

# Layer 4: All Customers by Zip
all_zip_layer = folium.FeatureGroup(name='📊 All Customers by Zip', show=False)

# Create colormap for all customers
max_all = all_zip_data['count'].max()
all_colormap = LinearColormap(
    colors=['#E6F5FF', '#4DA6FF', '#0066CC'],  # Light to dark blue
    vmin=0,
    vmax=max_all
)

for _, row in all_zip_data.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=min(3 + (row['count'] / 50), 20),  # Size based on count
        color='#000000',
        fillColor=all_colormap(row['count']),
        fillOpacity=0.7,
        weight=1,
        popup=f"<b>Zip: {row['Postal Code']}</b><br>Total Customers: {int(row['count'])}"
    ).add_to(all_zip_layer)

all_zip_layer.add_to(m)
print(f"   ✅ All customers by zip: {len(all_zip_data)} zip codes visualized")

# Business locations (same as before)
current_locations = [
    {'name': 'Hillsborough Township, NJ', 'lat': 40.4990, 'lon': -74.6362},
    {'name': 'Pennington, NJ', 'lat': 40.3071, 'lon': -74.7985},
    {'name': 'Lindenwold, NJ', 'lat': 39.8221, 'lon': -74.9957},
    {'name': 'Bethlehem, PA', 'lat': 40.6810, 'lon': -75.3620},
    {'name': 'North Wales, PA', 'lat': 40.2281, 'lon': -75.2814},
    {'name': 'West Chester, PA', 'lat': 39.9852, 'lon': -75.5938},
    {'name': 'Wilmington, DE', 'lat': 39.7614, 'lon': -75.5532},
    {'name': 'Mount Laurel Township, NJ', 'lat': 39.9368, 'lon': -74.9527},
    {'name': 'Doylestown, PA', 'lat': 40.3118, 'lon': -75.1355},
    {'name': 'Langhorne, PA', 'lat': 40.1856, 'lon': -74.8804},
    {'name': 'Allentown, PA', 'lat': 40.6080, 'lon': -75.4900},
    {'name': 'South Philadelphia, PA', 'lat': 39.9231, 'lon': -75.1753},
    {'name': 'Media, PA', 'lat': 39.9168, 'lon': -75.3877},
    {'name': 'NE Philadelphia, PA', 'lat': 40.0601, 'lon': -75.0850},
    {'name': 'Trenton, NJ', 'lat': 40.2171, 'lon': -74.7429},
    {'name': 'Lancaster, PA', 'lat': 40.0379, 'lon': -76.3055},
    {'name': 'Bowmansville, PA', 'lat': 40.2057, 'lon': -76.0167},
]

prospect_locations = [
    {'name': 'Old Bridge Township, NJ (Middlesex)', 'lat': 40.404632, 'lon': -74.308537},
    {'name': 'King of Prussia, PA', 'lat': 40.0890, 'lon': -75.3800},
]

print("\n🏢 Adding GMB location markers...")

current_layer = folium.FeatureGroup(name='🟢 Current Locations', show=True)
prospect_layer = folium.FeatureGroup(name='🔵 Prospective Locations', show=True)

for loc in current_locations:
    # White halo
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=22, color='#FFFFFF', fillColor='#FFFFFF',
        fillOpacity=0.9, weight=0
    ).add_to(current_layer)
    
    # Bold marker
    icon_html = f"""
    <div style="width: 36px; height: 36px; background-color: #FFFF00;
        border: 5px solid #000000; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: bold;
        box-shadow: 0 0 15px rgba(0,0,0,0.8), 0 0 30px rgba(255,255,0,0.6);
        cursor: pointer;">🟢</div>
    """
    
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        icon=folium.DivIcon(html=icon_html),
        popup=f"<b style='font-size:16px;'>{loc['name']}</b><br><b>CURRENT LOCATION</b>",
        tooltip=f"<b>{loc['name']}</b>"
    ).add_to(current_layer)

for loc in prospect_locations:
    # White halo
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=21, color='#FFFFFF', fillColor='#FFFFFF',
        fillOpacity=0.9, weight=0
    ).add_to(prospect_layer)
    
    # Bold marker
    icon_html = f"""
    <div style="width: 34px; height: 34px; background-color: #FF6600;
        border: 5px solid #000000; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: bold;
        box-shadow: 0 0 15px rgba(0,0,0,0.8), 0 0 30px rgba(255,102,0,0.6);
        cursor: pointer;">🔵</div>
    """
    
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        icon=folium.DivIcon(html=icon_html),
        popup=f"<b style='font-size:16px;'>{loc['name']}</b><br><b>PROSPECT LOCATION</b>",
        tooltip=f"<b>{loc['name']}</b>"
    ).add_to(prospect_layer)

current_layer.add_to(m)
prospect_layer.add_to(m)
print(f"   ✅ Current locations: {len(current_locations)}")
print(f"   ✅ Prospect locations: {len(prospect_locations)}")

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Add title
title_html = '''
<div style="position: fixed; top: 10px; left: 50px; width: 650px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid #333; border-radius: 8px; padding: 14px; 
     box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
     <h4 style="margin:0; color:#333; font-size:16px;">Customer Analysis Map</h4>
     <p style="margin:6px 0 0 0; font-size:13px; color:#666;">
     <span style="display:inline-block; width:14px; height:14px; background:#FFFF00; border-radius:50%; border:4px solid #000; margin-right:6px;"></span><b>Current</b> |
     <span style="display:inline-block; width:14px; height:14px; background:#FF6600; border-radius:50%; border:4px solid #000; margin:0 6px 0 12px;"></span><b>Prospects</b> |
     <span style="margin-left:12px; color:#FF8C00;">🔥 Heat Maps</span> | <span style="color:#4DA6FF;">📊 Zip Aggregations</span>
     </p>
</div>
'''

m.get_root().html.add_child(folium.Element(title_html))

# Save map
m.save('/workspace/interactive-map.html')

print("\n✅ Customer Analysis Map created successfully!")
print(f"   Saved to: /workspace/interactive-map.html")
print("=" * 70)
