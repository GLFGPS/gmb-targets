#!/usr/bin/env python3
"""
Build map with accurate zip code coordinates
"""

import folium
import pandas as pd

print("🗺️  Building map with ACCURATE zip code coordinates...")
print("=" * 70)

# Read accurate demographic data
df = pd.read_csv('/workspace/demographic_data_accurate_coords.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes with real coordinates")

# Map center
center_lat = 40.1
center_lon = -74.9

# Create base map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles='cartodbpositron',
    control_scale=True
)

print("🎨 Creating demographic layers...")

# Create feature groups
population_layer = folium.FeatureGroup(name='📊 Population', show=False)
density_layer = folium.FeatureGroup(name='🏘️ Population Density', show=False)
income_layer = folium.FeatureGroup(name='💰 Median Income', show=False)
age_layer = folium.FeatureGroup(name='👥 Median Age', show=False)
housing_layer = folium.FeatureGroup(name='🏠 Housing Units', show=False)

# Add all zip codes (no sampling - we have real data now)
for idx, row in df.iterrows():
    lat, lon = row['lat'], row['lon']
    zip_code = row['zip_code']
    
    # Population
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['pop_color'],
        fill=True,
        fillColor=row['pop_color'],
        fillOpacity=0.6,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Population: {row['population']:,}"
    ).add_to(population_layer)
    
    # Density
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['density_color'],
        fill=True,
        fillColor=row['density_color'],
        fillOpacity=0.6,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Density: {row['density']:,}/sq mi"
    ).add_to(density_layer)
    
    # Income
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['income_color'],
        fill=True,
        fillColor=row['income_color'],
        fillOpacity=0.6,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Income: ${row['median_income']:,}"
    ).add_to(income_layer)
    
    # Age
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['age_color'],
        fill=True,
        fillColor=row['age_color'],
        fillOpacity=0.6,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Age: {row['median_age']}"
    ).add_to(age_layer)
    
    # Housing
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=row['housing_color'],
        fill=True,
        fillColor=row['housing_color'],
        fillOpacity=0.6,
        weight=1,
        tooltip=f"<b>ZIP {zip_code}</b><br>Housing: {row['housing_units']:,}"
    ).add_to(housing_layer)

print("   ✅ All demographic layers created with real coordinates")

# Add business locations
print("🏢 Adding business locations...")

# Current locations
current_locations = [
    {'name': 'Media, PA', 'lat': 39.9168, 'lon': -75.387},
    {'name': 'Philadelphia, PA', 'lat': 39.9526, 'lon': -75.1652},
    {'name': 'Allentown, PA', 'lat': 40.608, 'lon': -75.49},
    {'name': 'Hillsborough, NJ', 'lat': 40.499, 'lon': -74.6362},
    {'name': 'Pennington, NJ', 'lat': 40.3071, 'lon': -74.7985},
    {'name': 'Lindenwold, NJ', 'lat': 39.8221, 'lon': -74.9957},
    {'name': 'Bethlehem, PA', 'lat': 40.681, 'lon': -75.362},
    {'name': 'North Wales, PA', 'lat': 40.2281, 'lon': -75.2814},
    {'name': 'West Chester, PA', 'lat': 39.9852, 'lon': -75.5938},
    {'name': 'Wilmington, DE', 'lat': 39.7614, 'lon': -75.5532},
    {'name': 'Mount Laurel, NJ', 'lat': 39.9368, 'lon': -74.9527},
    {'name': 'Doylestown, PA', 'lat': 40.3118, 'lon': -75.1355},
    {'name': 'Hamilton, NJ', 'lat': 40.2527, 'lon': -74.6821},
    {'name': 'Langhorne, PA', 'lat': 40.1856, 'lon': -74.8804},
]

# Prospects
prospect_locations = [
    {'name': 'Toms River, NJ', 'lat': 39.994264, 'lon': -74.166154},
    {'name': 'Manchester Township, NJ', 'lat': 39.9651379, 'lon': -74.3738192},
    {'name': 'Little Egg Harbor, NJ', 'lat': 39.633, 'lon': -74.33103},
    {'name': 'Reading, PA', 'lat': 40.341692, 'lon': -75.926301},
    {'name': 'Cheltenham Township, PA', 'lat': 40.06667, 'lon': -75.11639},
    {'name': 'Elkins Park, PA', 'lat': 40.07694, 'lon': -75.12694},
    {'name': 'Abington Township, PA', 'lat': 40.1, 'lon': -75.09972},
    {'name': 'Mullica Township, NJ', 'lat': 39.596486, 'lon': -74.6765},
    {'name': 'Vineland, NJ', 'lat': 39.465, 'lon': -75.00639},
]

current_layer = folium.FeatureGroup(name='🟢 Current Locations', show=True)
prospect_layer = folium.FeatureGroup(name='🔵 Prospective Locations', show=True)

# Add current locations
for loc in current_locations:
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,  # 5 miles
        color='#006400',
        fill=True,
        fillColor='#006400',
        fillOpacity=0.06,
        weight=2
    ).add_to(current_layer)
    
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=f"<b>{loc['name']}</b><br>CURRENT",
        tooltip=loc['name'],
        icon=folium.Icon(color='green', icon='ok-sign', prefix='glyphicon')
    ).add_to(current_layer)

# Add prospect locations
for loc in prospect_locations:
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,
        color='blue',
        fill=False,
        weight=1
    ).add_to(prospect_layer)
    
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=f"<b>{loc['name']}</b><br>PROSPECT",
        tooltip=loc['name'],
        icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
    ).add_to(prospect_layer)

print(f"   ✅ Added {len(current_locations)} current + {len(prospect_locations)} prospect locations")

# Add all layers
current_layer.add_to(m)
prospect_layer.add_to(m)
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
     top: 10px; left: 50px; width: 550px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid grey; border-radius: 5px; padding: 10px">
     <h4 style="margin:0;">NJ/DE/PA Business Locations + Demographics</h4>
     <p style="margin:5px 0 0 0; font-size:12px;">
     🟢 Green = Current | 🔵 Blue = Prospects | Toggle demographic layers
     </p>
</div>
'''

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
output_file = '/workspace/interactive-map-fixed.html'
m.save(output_file)

print(f"\n✅ Map saved to: {output_file}")
print(f"\n📋 Map includes:")
print(f"   • {len(df)} real zip codes with accurate coordinates")
print(f"   • 14 current business locations")
print(f"   • 9 prospective locations")
print(f"   • 5 demographic overlays")
print("\n" + "=" * 70)
