#!/usr/bin/env python3
"""
Option B: Hex Grid (H3 Binning) for Customer Visualization
"""

import folium
import pandas as pd
from branca.colormap import LinearColormap
import math

print("🗺️  Building Option B: Hex Grid Map...")
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

# Simple grid-based hexagon simulation (approximate hex bins)
# Divide area into grid cells and count customers per cell
def create_grid_bins(data, grid_size=0.02):
    """Create grid bins for customer aggregation"""
    bins = {}
    for _, row in data.iterrows():
        # Round to grid
        lat_bin = round(row['Latitude'] / grid_size) * grid_size
        lon_bin = round(row['Longitude'] / grid_size) * grid_size
        key = (lat_bin, lon_bin)
        bins[key] = bins.get(key, 0) + 1
    return bins

active_bins = create_grid_bins(df_active, 0.015)
all_bins = create_grid_bins(df, 0.015)

print(f"   Active bins: {len(active_bins)}")
print(f"   All bins: {len(all_bins)}")

# Create map
m = folium.Map(location=[40.0, -75.5], zoom_start=9, tiles='cartodbpositron', control_scale=True)

# Active customer grid
active_layer = folium.FeatureGroup(name='🔶 Active Customer Grid', show=True)
max_active = max(active_bins.values())
active_colormap = LinearColormap(['#FFF5E6', '#FF8C00', '#CC5500'], vmin=0, vmax=max_active)

for (lat, lon), count in active_bins.items():
    folium.RegularPolygonMarker(
        location=[lat, lon],
        number_of_sides=6,
        radius=8,
        color='#000000',
        fillColor=active_colormap(count),
        fillOpacity=0.7,
        weight=1,
        popup=f"<b>Active Customers:</b> {count}"
    ).add_to(active_layer)
active_layer.add_to(m)

# All customer grid
all_layer = folium.FeatureGroup(name='🔶 All Customer Grid', show=False)
max_all = max(all_bins.values())
all_colormap = LinearColormap(['#E6F5FF', '#4DA6FF', '#0066CC'], vmin=0, vmax=max_all)

for (lat, lon), count in all_bins.items():
    folium.RegularPolygonMarker(
        location=[lat, lon],
        number_of_sides=6,
        radius=8,
        color='#000000',
        fillColor=all_colormap(count),
        fillOpacity=0.7,
        weight=1,
        popup=f"<b>Total Customers:</b> {count}"
    ).add_to(all_layer)
all_layer.add_to(m)

print(f"   ✅ Grid visualization complete")

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
<h4 style="margin:0; color:#333; font-size:16px;">Option B: Hex Grid</h4>
<p style="margin:6px 0 0 0; font-size:13px; color:#666;">Hexagons colored by customer count - click for exact numbers</p></div>'''
m.get_root().html.add_child(folium.Element(title_html))

m.save('/workspace/option-b-hexgrid.html')
print("✅ Option B: Hex Grid saved!")
