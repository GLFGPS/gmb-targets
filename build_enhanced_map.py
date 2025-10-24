#!/usr/bin/env python3
"""
Build enhanced interactive map with demographic overlays
"""

import folium
from folium import plugins
import pandas as pd

print("🗺️  Building enhanced interactive map with demographic overlays...")
print("=" * 70)

# Read the enhanced demographic data
df = pd.read_csv('/workspace/demographic_data_with_coords.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes with demographics and coordinates")

# Read the original locations data from the existing map
# We'll extract this from the second (non-overlay) map since it's smaller
print("📍 Reading existing location data...")

# Center map on the tri-state area
center_lat = 40.1
center_lon = -74.9

# Create the base map
print("🗺️  Creating base map...")
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles='cartodbpositron',
    control_scale=True
)

print("🎨 Creating demographic overlay layers...")

# Create feature groups for each demographic overlay
population_layer = folium.FeatureGroup(name='📊 Population', show=False)
density_layer = folium.FeatureGroup(name='🏘️ Population Density', show=False)
income_layer = folium.FeatureGroup(name='💰 Median Income', show=True)  # Show by default
age_layer = folium.FeatureGroup(name='👥 Median Age', show=False)
housing_layer = folium.FeatureGroup(name='🏠 Housing Units', show=False)

# Sample every Nth zip code to avoid overwhelming the map
sample_rate = 3  # Show every 3rd zip code
df_sample = df.iloc[::sample_rate]

print(f"   Sampling {len(df_sample)} of {len(df)} zip codes for performance...")

# Add circles for each demographic layer
for idx, row in df_sample.iterrows():
    lat, lon = row['lat'], row['lon']
    zip_code = row['zip_code']
    
    # Population overlay
    folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        color=row['pop_color'],
        fill=True,
        fillColor=row['pop_color'],
        fillOpacity=0.6,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Population: {row['population']:,}"
    ).add_to(population_layer)
    
    # Density overlay
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['density_color'],
        fill=True,
        fillColor=row['density_color'],
        fillOpacity=0.7,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Density: {row['density']:,}/sq mi<br>{row['density_category']}"
    ).add_to(density_layer)
    
    # Income overlay
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['income_color'],
        fill=True,
        fillColor=row['income_color'],
        fillOpacity=0.7,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Median Income: ${row['median_income']:,}<br>{row['income_category']}"
    ).add_to(income_layer)
    
    # Age overlay
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['age_color'],
        fill=True,
        fillColor=row['age_color'],
        fillOpacity=0.7,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Median Age: {row['median_age']}"
    ).add_to(age_layer)
    
    # Housing overlay
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['housing_color'],
        fill=True,
        fillColor=row['housing_color'],
        fillOpacity=0.7,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Housing Units: {row['housing_units']:,}"
    ).add_to(housing_layer)

print("   ✅ Population layer created")
print("   ✅ Density layer created")
print("   ✅ Income layer created")
print("   ✅ Age layer created")
print("   ✅ Housing layer created")

# Add layers to map
population_layer.add_to(m)
density_layer.add_to(m)
income_layer.add_to(m)
age_layer.add_to(m)
housing_layer.add_to(m)

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Add title and legend
title_html = '''
<div style="position: fixed; 
     top: 10px; left: 50px; width: 500px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid grey; border-radius: 5px; padding: 10px">
     <h4 style="margin:0;">NJ/DE/PA Demographic Map</h4>
     <p style="margin:5px 0 0 0; font-size:12px;">Toggle layers to view different demographics</p>
</div>
'''

# Add legend for color scales
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 300px; height: auto;
     background-color: white; z-index:9999; font-size:11px;
     border:2px solid grey; border-radius: 5px; padding: 10px">
     <h5 style="margin:0 0 8px 0;">Color Scale Legends</h5>
     <div style="margin-bottom:5px;">
         <b>💰 Income:</b> <span style="color:#00ff00">██</span> Low → 
         <span style="color:#006400">██</span> High
     </div>
     <div style="margin-bottom:5px;">
         <b>📊 Population:</b> <span style="color:#add8e6">██</span> Low → 
         <span style="color:#00008b">██</span> High
     </div>
     <div style="margin-bottom:5px;">
         <b>🏘️ Density:</b> <span style="color:#dda0dd">██</span> Low → 
         <span style="color:#800080">██</span> High
     </div>
     <div style="margin-bottom:5px;">
         <b>👥 Age:</b> <span style="color:#ffc800">██</span> Young → 
         <span style="color:#ff8900">██</span> Old
     </div>
     <div>
         <b>🏠 Housing:</b> <span style="color:#ffa07a">██</span> Few → 
         <span style="color:#ff0000">██</span> Many
     </div>
</div>
'''

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
output_file = '/workspace/interactive-map-demographics.html'
m.save(output_file)

print(f"\n✅ Enhanced map saved to: {output_file}")
print("\n📊 Map Features:")
print("   • 5 demographic overlay layers (toggleable)")
print("   • Color-coded visualizations")
print("   • Hover tooltips with data")
print("   • Covers NJ, DE, and Eastern PA")
print("\n" + "=" * 70)
