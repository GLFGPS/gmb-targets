#!/usr/bin/env python3
"""
Build census tract map with PROPER GeoJSON FeatureCollection
"""

import folium
import pandas as pd
import json
from branca.colormap import LinearColormap

print("🗺️  Building census tract map with FeatureCollection approach...")
print("=" * 70)

# Load data with GAP-FREE cartographic boundaries (ALL 21 NJ counties) + CITY NAMES
df = pd.read_csv('/workspace/complete_census_all_nj_with_cities.csv', dtype={'geoid': str})
print(f"📊 Loaded {len(df)} census tracts with gap-free boundaries")
print(f"   ALL 21 NJ counties + DE + PA")

# Minimal cleaning
df = df[df['geometry'].notna()]  # Must have geometry

print(f"📊 After cleaning: {len(df)} census tracts")
print(f"   (Using cartographic boundaries - NO GAPS!)")

# Create map
m = folium.Map(location=[40.1, -74.9], zoom_start=9, tiles='cartodbpositron', control_scale=True)

# Demographics config
demographics_config = {
    'median_income': ('💰 Median Income', 'YlGn'),
    'population': ('📊 Population', 'YlGnBu'),
    'density': ('🏘️ Population Density', 'PuRd'),
    'median_home_value': ('🏡 Median Home Value', 'YlOrRd')
}

print("🎨 Creating heat map layers using FeatureCollection...")

for demo, (layer_name, colormap_name) in demographics_config.items():
    # Create FeatureCollection for this demographic
    features = []
    
    for idx, row in df.iterrows():
        if pd.notna(row['geometry']):
            try:
                geometry_data = json.loads(row['geometry'])
                
                # Handle missing demographic data - use 0 or min value
                value = row[demo] if pd.notna(row[demo]) else 0
                
                # Create feature with properties
                feature = {
                    "type": "Feature",
                    "geometry": geometry_data,
                    "properties": {
                        "geoid": row['geoid'],
                        "city": row.get('city', 'Unknown'),
                        "county": row.get('county_name', 'Unknown'),
                        "state": row.get('state_name', ''),
                        "value": float(value) if value else 0,
                        "demo": demo
                    }
                }
                features.append(feature)
            except Exception as e:
                pass
    
    if len(features) == 0:
        continue
        
    # Create FeatureCollection
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Create colormap
    min_val = df[demo].min()
    max_val = df[demo].max()
    
    # Cap density at 10,000 for better color distribution in suburban areas
    if demo == 'density':
        max_val = min(max_val, 10000)
        print(f"   📊 Capping density at 10,000 per sq mi for better visualization")
    
    colormap = LinearColormap(
        colors=['#F7FFF7', '#00AA00', '#004D00'] if demo == 'median_income' 
        else ['#F0F8FF', '#0066CC', '#00008B'] if demo == 'population'
        else ['#FDF5FF', '#7B2D9E', '#2E0854'] if demo == 'density'
        else ['#FFFFF0', '#228B22', '#006400'],
        vmin=min_val,
        vmax=max_val
    )
    
    # Style function
    def style_function(feature, colormap=colormap, demo=demo, max_val=max_val):
        value = feature['properties']['value']
        # Cap density values at max_val (20,000 for density)
        if demo == 'density' and value > max_val:
            value = max_val
        return {
            'fillColor': colormap(value),
            'color': colormap(value),
            'weight': 0.5,
            'fillOpacity': 0.7
        }
    
    # Tooltip function
    def highlight_function(feature):
        return {
            'fillColor': '#ffff00',
            'color': '#000000',
            'weight': 2,
            'fillOpacity': 0.9
        }
    
    # Add to map as single GeoJson layer
    layer = folium.FeatureGroup(name=layer_name, show=False)
    
    folium.GeoJson(
        feature_collection,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['city', 'geoid', 'value'],
            aliases=['City:', 'Tract:', f'{layer_name}:'],
            localize=True
        )
    ).add_to(layer)
    
    layer.add_to(m)
    print(f"   ✅ {layer_name}: {len(features)} tracts")

# Business locations
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
    {'name': 'Monroe Township, NJ (Middlesex)', 'lat': 40.319474, 'lon': -74.428802},
    {'name': 'Middletown Township, NJ (Monmouth)', 'lat': 40.404786, 'lon': -74.071404},
    {'name': 'Old Bridge Township, NJ (Middlesex)', 'lat': 40.404632, 'lon': -74.308537},
    {'name': 'Marlboro Township, NJ (Monmouth)', 'lat': 40.342931, 'lon': -74.257197},
    {'name': 'New Brunswick, NJ (Middlesex)', 'lat': 40.486678, 'lon': -74.444414},
    {'name': 'Swedesboro, NJ (Gloucester)', 'lat': 39.745884, 'lon': -75.310947},
    {'name': 'Newark, DE (New Castle)', 'lat': 39.683723, 'lon': -75.749657},
    {'name': 'Toms River, NJ', 'lat': 39.994264, 'lon': -74.166154},
    {'name': 'Manchester Township, NJ', 'lat': 39.965138, 'lon': -74.373819},
    {'name': 'Little Egg Harbor Township, NJ', 'lat': 39.633000, 'lon': -74.331030},
    {'name': 'Reading, PA', 'lat': 40.341692, 'lon': -75.926301},
    {'name': 'Cheltenham Township, PA', 'lat': 40.066670, 'lon': -75.116390},
    {'name': 'Elkins Park, PA', 'lat': 40.076940, 'lon': -75.126940},
    {'name': 'Abington Township, PA', 'lat': 40.100000, 'lon': -75.099720},
    {'name': 'Mullica Township, NJ', 'lat': 39.596486, 'lon': -74.676500},
    {'name': 'Vineland, NJ', 'lat': 39.465000, 'lon': -75.006390},
    {'name': 'Phoenixville, PA', 'lat': 40.1304, 'lon': -75.5149},
    {'name': 'Warminster, PA', 'lat': 40.2009, 'lon': -75.0871},
    {'name': 'King of Prussia, PA', 'lat': 40.0890, 'lon': -75.3800},
]

print("🏢 Creating business markers...")

current_layer = folium.FeatureGroup(name='🟢 Current Locations', show=True)
prospect_layer = folium.FeatureGroup(name='🔵 Prospective Locations', show=True)

for loc in current_locations:
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=22, color='#FFFFFF', fillColor='#FFFFFF',
        fillOpacity=0.9, weight=0
    ).add_to(current_layer)
    
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
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=21, color='#FFFFFF', fillColor='#FFFFFF',
        fillOpacity=0.9, weight=0
    ).add_to(prospect_layer)
    
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

print("   ✅ Markers created")

current_layer.add_to(m)
prospect_layer.add_to(m)

folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Title
title_html = '''
<div style="position: fixed; top: 10px; left: 50px; width: 600px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid #333; border-radius: 8px; padding: 14px; 
     box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
     <h4 style="margin:0; color:#333; font-size:16px;">NJ/DE/PA Census Tract Demographics</h4>
     <p style="margin:6px 0 0 0; font-size:13px; color:#666;">
     <span style="display:inline-block; width:14px; height:14px; background:#FFFF00; border-radius:50%; border:4px solid #000; margin-right:6px;"></span><b>Current</b> |
     <span style="display:inline-block; width:14px; height:14px; background:#FF6600; border-radius:50%; border:4px solid #000; margin:0 6px 0 12px;"></span><b>Prospects</b>
     </p>
</div>
'''

m.get_root().html.add_child(folium.Element(title_html))

m.save('/workspace/search-map.html')

print("\n✅ Census tract map saved with FeatureCollection approach!")
print("=" * 70)
