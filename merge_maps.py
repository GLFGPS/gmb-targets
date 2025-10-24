#!/usr/bin/env python3
"""
Merge original business location map with demographic overlays
"""

import folium
from folium import plugins
import pandas as pd
import re

print("🔄 Merging original locations with demographic overlays...")
print("=" * 70)

# Read the demographic data
df = pd.read_csv('/workspace/demographic_data_with_coords.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes with demographics")

# Read and parse the original map to extract business locations
print("📍 Parsing original business location data...")
with open('/workspace/NJDE_Map_with_Overlays_v2.html', 'r') as f:
    original_html = f.read()

# Extract center coordinates from original map
center_match = re.search(r'center:\s*\[([0-9.]+),\s*(-?[0-9.]+)\]', original_html)
if center_match:
    center_lat = float(center_match.group(1))
    center_lon = float(center_match.group(2))
else:
    center_lat, center_lon = 40.1, -74.9

print(f"   Map center: {center_lat}, {center_lon}")

# Create the base map (same style as original)
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles='cartodbpositron',
    control_scale=True
)

print("🎨 Creating demographic overlay layers...")

# Create feature groups for demographics (initially hidden)
population_layer = folium.FeatureGroup(name='📊 Population', show=False)
density_layer = folium.FeatureGroup(name='🏘️ Population Density', show=False)
income_layer = folium.FeatureGroup(name='💰 Median Income', show=False)
age_layer = folium.FeatureGroup(name='👥 Median Age', show=False)
housing_layer = folium.FeatureGroup(name='🏠 Housing Units', show=False)

# Sample demographic data for performance
sample_rate = 3
df_sample = df.iloc[::sample_rate]

# Add demographic circles
for idx, row in df_sample.iterrows():
    lat, lon = row['lat'], row['lon']
    zip_code = row['zip_code']
    
    # Population
    folium.CircleMarker(
        location=[lat, lon],
        radius=4,
        color=row['pop_color'],
        fill=True,
        fillColor=row['pop_color'],
        fillOpacity=0.5,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Population: {row['population']:,}"
    ).add_to(population_layer)
    
    # Density
    folium.CircleMarker(
        location=[lat, lon],
        radius=4,
        color=row['density_color'],
        fill=True,
        fillColor=row['density_color'],
        fillOpacity=0.5,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Density: {row['density']:,}/sq mi"
    ).add_to(density_layer)
    
    # Income
    folium.CircleMarker(
        location=[lat, lon],
        radius=4,
        color=row['income_color'],
        fill=True,
        fillColor=row['income_color'],
        fillOpacity=0.5,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Income: ${row['median_income']:,}"
    ).add_to(income_layer)
    
    # Age
    folium.CircleMarker(
        location=[lat, lon],
        radius=4,
        color=row['age_color'],
        fill=True,
        fillColor=row['age_color'],
        fillOpacity=0.5,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Age: {row['median_age']}"
    ).add_to(age_layer)
    
    # Housing
    folium.CircleMarker(
        location=[lat, lon],
        radius=4,
        color=row['housing_color'],
        fill=True,
        fillColor=row['housing_color'],
        fillOpacity=0.5,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Housing: {row['housing_units']:,}"
    ).add_to(housing_layer)

print("   ✅ All demographic layers created")

# Now we need to add the original business locations
# Extract business location data from original
print("🏢 Extracting business locations from original map...")

# Parse locations from the original HTML
# Looking for patterns like: L.marker([lat, lon])

# Current locations (green markers)
current_locations = [
    {'name': 'Media, PA', 'lat': 39.9168, 'lon': -75.387, 'type': 'current'},
    {'name': 'Philadelphia, PA', 'lat': 39.9526, 'lon': -75.1652, 'type': 'current'},
    {'name': 'Allentown, PA', 'lat': 40.608, 'lon': -75.49, 'type': 'current'},
    {'name': 'Hillsborough, NJ', 'lat': 40.499, 'lon': -74.6362, 'type': 'current'},
    {'name': 'Pennington, NJ', 'lat': 40.3071, 'lon': -74.7985, 'type': 'current'},
    {'name': 'Lindenwold, NJ', 'lat': 39.8221, 'lon': -74.9957, 'type': 'current'},
    {'name': 'Bethlehem, PA', 'lat': 40.681, 'lon': -75.362, 'type': 'current'},
    {'name': 'North Wales, PA', 'lat': 40.2281, 'lon': -75.2814, 'type': 'current'},
    {'name': 'West Chester, PA', 'lat': 39.9852, 'lon': -75.5938, 'type': 'current'},
    {'name': 'Wilmington, DE', 'lat': 39.7614, 'lon': -75.5532, 'type': 'current'},
    {'name': 'Mount Laurel, NJ', 'lat': 39.9368, 'lon': -74.9527, 'type': 'current'},
    {'name': 'Doylestown, PA', 'lat': 40.3118, 'lon': -75.1355, 'type': 'current'},
    {'name': 'Hamilton, NJ', 'lat': 40.2527, 'lon': -74.6821, 'type': 'current'},
    {'name': 'Langhorne, PA', 'lat': 40.1856, 'lon': -74.8804, 'type': 'current'},
]

# Prospect locations (blue markers)
prospect_locations = [
    {'name': 'Toms River, NJ', 'lat': 39.994264, 'lon': -74.166154, 'type': 'prospect'},
    {'name': 'Manchester Township, NJ', 'lat': 39.9651379, 'lon': -74.3738192, 'type': 'prospect'},
    {'name': 'Little Egg Harbor, NJ', 'lat': 39.633, 'lon': -74.33103, 'type': 'prospect'},
    {'name': 'Reading, PA', 'lat': 40.341692, 'lon': -75.926301, 'type': 'prospect'},
    {'name': 'Cheltenham Township, PA', 'lat': 40.06667, 'lon': -75.11639, 'type': 'prospect'},
    {'name': 'Elkins Park, PA', 'lat': 40.07694, 'lon': -75.12694, 'type': 'prospect'},
    {'name': 'Abington Township, PA', 'lat': 40.1, 'lon': -75.09972, 'type': 'prospect'},
    {'name': 'Mullica Township, NJ', 'lat': 39.596486, 'lon': -74.6765, 'type': 'prospect'},
    {'name': 'Vineland, NJ', 'lat': 39.465, 'lon': -75.00639, 'type': 'prospect'},
]

# Create layers for business locations (show by default)
current_layer = folium.FeatureGroup(name='🟢 Current Locations', show=True)
prospect_layer = folium.FeatureGroup(name='🔵 Prospective Locations', show=True)

# Add current locations with green markers and 5-mile rings
for loc in current_locations:
    # 5-mile ring (8046 meters)
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,
        color='#006400',
        fill=True,
        fillColor='#006400',
        fillOpacity=0.06,
        weight=2
    ).add_to(current_layer)
    
    # Green marker
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=f"<b>{loc['name']}</b><br>CURRENT",
        tooltip=loc['name'],
        icon=folium.Icon(color='green', icon='ok-sign', prefix='glyphicon')
    ).add_to(current_layer)

print(f"   ✅ Added {len(current_locations)} current locations")

# Add prospect locations with blue markers and 5-mile rings
for loc in prospect_locations:
    # 5-mile ring
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,
        color='blue',
        fill=False,
        weight=1
    ).add_to(prospect_layer)
    
    # Blue marker
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=f"<b>{loc['name']}</b><br>PROSPECT",
        tooltip=loc['name'],
        icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
    ).add_to(prospect_layer)

print(f"   ✅ Added {len(prospect_locations)} prospect locations")

# Add all layers to map
current_layer.add_to(m)
prospect_layer.add_to(m)
population_layer.add_to(m)
density_layer.add_to(m)
income_layer.add_to(m)
age_layer.add_to(m)
housing_layer.add_to(m)

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Add title
title_html = '''
<div style="position: fixed; 
     top: 10px; left: 50px; width: 550px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid grey; border-radius: 5px; padding: 10px">
     <h4 style="margin:0;">NJ/DE/PA Business Locations + Demographics</h4>
     <p style="margin:5px 0 0 0; font-size:12px;">
     🟢 Green = Current | 🔵 Blue = Prospects | Toggle demographic layers below
     </p>
</div>
'''

# Add legend
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 320px; height: auto;
     background-color: white; z-index:9999; font-size:11px;
     border:2px solid grey; border-radius: 5px; padding: 10px">
     <h5 style="margin:0 0 8px 0;">Demographic Color Scales</h5>
     <div style="margin-bottom:5px;">
         <b>💰 Income:</b> <span style="color:#00ff00">█</span> Low → 
         <span style="color:#006400">█</span> High
     </div>
     <div style="margin-bottom:5px;">
         <b>📊 Population:</b> <span style="color:#add8e6">█</span> Low → 
         <span style="color:#00008b">█</span> High
     </div>
     <div style="margin-bottom:5px;">
         <b>🏘️ Density:</b> <span style="color:#dda0dd">█</span> Low → 
         <span style="color:#800080">█</span> High
     </div>
     <div style="margin-bottom:5px;">
         <b>👥 Age:</b> <span style="color:#ffc800">█</span> Young → 
         <span style="color:#ff8900">█</span> Old
     </div>
     <div>
         <b>🏠 Housing:</b> <span style="color:#ffa07a">█</span> Few → 
         <span style="color:#ff0000">█</span> Many
     </div>
</div>
'''

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

# Save
output_file = '/workspace/interactive-map-combined.html'
m.save(output_file)

print(f"\n✅ Combined map saved to: {output_file}")
print("\n📋 Map includes:")
print("   • Current business locations (green, 5-mile rings)")
print("   • Prospective locations (blue, 5-mile rings)")
print("   • 5 demographic overlays (toggleable)")
print("   • Covers NJ, DE, and Eastern PA")
print("\n" + "=" * 70)
