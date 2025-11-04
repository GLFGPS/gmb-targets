#!/usr/bin/env python3
"""
Option A: Marker Clusters for Customer Visualization
"""

import folium
from folium.plugins import MarkerCluster
import pandas as pd

print("🗺️  Building Option A: Marker Clusters Map...")
print("=" * 70)

# Load customer data
df = pd.read_csv('/workspace/customer_locations.csv', dtype={'Postal Code': str})
df.columns = df.columns.str.strip()
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df['Customer Status'] = pd.to_numeric(df['Customer Status'], errors='coerce')
df = df.dropna(subset=['Latitude', 'Longitude'])

df_active = df[df['Customer Status'] == 9.0].copy()

print(f"   Total: {len(df):,} | Active: {len(df_active):,}")

# Create map
m = folium.Map(location=[40.0, -75.5], zoom_start=9, tiles='cartodbpositron', control_scale=True)

# Active Customer Clusters
active_cluster = MarkerCluster(name='🎯 Active Customer Clusters', show=True)
for _, row in df_active.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        color='#FF6600',
        fill=True,
        fillColor='#FF6600',
        fillOpacity=0.7
    ).add_to(active_cluster)
active_cluster.add_to(m)
print(f"   ✅ Active clusters: {len(df_active):,} points")

# All Customer Clusters
all_cluster = MarkerCluster(name='🎯 All Customer Clusters', show=False)
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        color='#4DA6FF',
        fill=True,
        fillColor='#4DA6FF',
        fillOpacity=0.7
    ).add_to(all_cluster)
all_cluster.add_to(m)
print(f"   ✅ All clusters: {len(df):,} points")

# GMB Locations
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
    {'name': 'Old Bridge Township, NJ', 'lat': 40.404632, 'lon': -74.308537},
    {'name': 'King of Prussia, PA', 'lat': 40.0890, 'lon': -75.3800},
]

current_layer = folium.FeatureGroup(name='🟢 Current Locations', show=True)
for loc in current_locations:
    icon_html = f'<div style="width: 36px; height: 36px; background-color: #FFFF00; border: 5px solid #000000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 0 15px rgba(0,0,0,0.8);">🟢</div>'
    folium.Marker([loc['lat'], loc['lon']], icon=folium.DivIcon(html=icon_html), tooltip=f"<b>{loc['name']}</b>").add_to(current_layer)

prospect_layer = folium.FeatureGroup(name='🔵 Prospect Locations', show=True)
for loc in prospect_locations:
    icon_html = f'<div style="width: 34px; height: 34px; background-color: #FF6600; border: 5px solid #000000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: 0 0 15px rgba(0,0,0,0.8);">🔵</div>'
    folium.Marker([loc['lat'], loc['lon']], icon=folium.DivIcon(html=icon_html), tooltip=f"<b>{loc['name']}</b>").add_to(prospect_layer)

current_layer.add_to(m)
prospect_layer.add_to(m)

folium.LayerControl(position='topright', collapsed=False).add_to(m)

title_html = '''<div style="position: fixed; top: 10px; left: 50px; width: 550px; background-color: white; z-index:9999; font-size:14px; border:2px solid #333; border-radius: 8px; padding: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
<h4 style="margin:0; color:#333; font-size:16px;">Option A: Marker Clusters</h4>
<p style="margin:6px 0 0 0; font-size:13px; color:#666;">Click numbered clusters to zoom in and see individual customers</p></div>'''
m.get_root().html.add_child(folium.Element(title_html))

m.save('/workspace/option-a-clusters.html')
print("✅ Option A: Marker Clusters saved!")
