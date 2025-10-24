#!/usr/bin/env python3
"""
Final polished map with city names, county boundary, and bold markers
"""

import folium
import pandas as pd

print("🎨 Building FINAL POLISHED map...")
print("=" * 70)

# Read demographic data
df = pd.read_csv('/workspace/complete_demographic_data.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes")

# Enhanced color function (same as before)
def get_strong_color(value, min_val, max_val, scheme):
    norm = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    norm = max(0, min(1, norm))
    
    if scheme == 'income':
        if norm < 0.33:
            t = norm / 0.33
            r = int(232 - (232 - 102) * t)
            g = int(245 - (245 - 187) * t)
            b = int(233 - (233 - 106) * t)
        elif norm < 0.67:
            t = (norm - 0.33) / 0.34
            r = int(102 - (102 - 27) * t)
            g = int(187 - (187 - 94) * t)
            b = int(106 - (106 - 32) * t)
        else:
            t = (norm - 0.67) / 0.33
            r = int(27 - (27 - 11) * t)
            g = int(94 - (94 - 56) * t)
            b = int(32 - (32 - 10) * t)
        return f'#{r:02x}{g:02x}{b:02x}'
    elif scheme == 'population':
        if norm < 0.33:
            t = norm / 0.33
            r = int(227 - (227 - 66) * t)
            g = int(242 - (242 - 165) * t)
            b = int(253 - (253 - 245) * t)
        elif norm < 0.67:
            t = (norm - 0.33) / 0.34
            r = int(66 - (66 - 13) * t)
            g = int(165 - (165 - 71) * t)
            b = int(245 - (245 - 161) * t)
        else:
            t = (norm - 0.67) / 0.33
            r = int(13 - (13 - 5) * t)
            g = int(71 - (71 - 34) * t)
            b = int(161 - (161 - 92) * t)
        return f'#{r:02x}{g:02x}{b:02x}'
    elif scheme == 'density':
        if norm < 0.33:
            t = norm / 0.33
            r = int(243 - (243 - 171) * t)
            g = int(229 - (229 - 71) * t)
            b = int(245 - (245 - 188) * t)
        elif norm < 0.67:
            t = (norm - 0.33) / 0.34
            r = int(171 - (171 - 74) * t)
            g = int(71 - (71 - 20) * t)
            b = int(188 - (188 - 140) * t)
        else:
            t = (norm - 0.67) / 0.33
            r = int(74 - (74 - 35) * t)
            g = int(20 - (20 - 7) * t)
            b = int(140 - (140 - 66) * t)
        return f'#{r:02x}{g:02x}{b:02x}'
    elif scheme == 'age':
        if norm < 0.33:
            t = norm / 0.33
            r = 255
            g = int(243 - (243 - 152) * t)
            b = int(224 - 224 * t)
        elif norm < 0.67:
            t = (norm - 0.33) / 0.34
            r = 255
            g = int(152 - (152 - 81) * t)
            b = 0
        else:
            t = (norm - 0.67) / 0.33
            r = int(255 - (255 - 230) * t)
            g = int(81 - 81 * t)
            b = 0
        return f'#{r:02x}{g:02x}{b:02x}'
    elif scheme == 'housing':
        if norm < 0.33:
            t = norm / 0.33
            r = 255
            g = int(235 - (235 - 83) * t)
            b = int(238 - (238 - 80) * t)
        elif norm < 0.67:
            t = (norm - 0.33) / 0.34
            r = int(239 - (239 - 183) * t)
            g = int(83 - (83 - 28) * t)
            b = int(80 - (80 - 28) * t)
        else:
            t = (norm - 0.67) / 0.33
            r = int(183 - (183 - 136) * t)
            g = int(28 - (28 - 14) * t)
            b = int(28 - (28 - 14) * t)
        return f'#{r:02x}{g:02x}{b:02x}'
    return '#CCCCCC'

print("🎨 Recalculating colors...")

for col, scheme in [('population', 'population'), ('median_income', 'income'), 
                     ('median_age', 'age'), ('housing_units', 'housing'), 
                     ('density', 'density')]:
    min_val, max_val = df[col].min(), df[col].max()
    color_col = {'population': 'pop', 'median_income': 'income', 
                 'median_age': 'age', 'housing_units': 'housing', 'density': 'density'}[col]
    df[f'{color_col}_color'] = df[col].apply(
        lambda x: get_strong_color(x, min_val, max_val, scheme)
    )

# Create base map
center_lat = 40.1
center_lon = -74.9

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles='cartodbpositron',
    control_scale=True
)

print("🗺️  Creating choropleth layers with CITY NAMES...")

def create_large_polygon(lat, lon, size=0.04):
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [lon - size, lat - size],
                [lon + size, lat - size],
                [lon + size, lat + size],
                [lon - size, lat + size],
                [lon - size, lat - size]
            ]]
        }
    }

demographics = {
    'population': ('📊 Population', 'pop_color'),
    'density': ('🏘️ Population Density', 'density_color'),
    'median_income': ('💰 Median Income', 'income_color'),
    'median_age': ('👥 Median Age', 'age_color'),
    'housing_units': ('🏠 Housing Units', 'housing_color')
}

layers = {}

for demo, (layer_name, color_col) in demographics.items():
    features = []
    for idx, row in df.iterrows():
        poly = create_large_polygon(row['lat'], row['lon'], size=0.04)
        
        # Format value for display
        if demo == 'median_income':
            value_display = f"${row[demo]:,.0f}"
        else:
            value_display = f"{row[demo]:,.0f}"
        
        poly['properties'] = {
            'zip_code': row['zip_code'],
            'city': row.get('city', 'Unknown'),  # CITY NAME
            'value': value_display,
            'color': row[color_col]
        }
        features.append(poly)
    
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    layer = folium.FeatureGroup(name=layer_name, show=False)
    
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': feature['properties']['color'],
            'color': feature['properties']['color'],
            'weight': 0.3,
            'fillOpacity': 0.75
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['city', 'zip_code', 'value'],  # CITY FIRST
            aliases=['City/Town:', 'ZIP:', f'{demo.replace("_", " ").title()}:'],
            localize=True
        )
    ).add_to(layer)
    
    layers[demo] = layer

print("   ✅ All layers created with city names in tooltips")

# Add PHILADELPHIA COUNTY BOUNDARY
print("📍 Adding Philadelphia County boundary...")

# Philadelphia County approximate boundary
philly_boundary = [
    [40.1379, -75.2803],  # Northeast
    [40.1379, -74.9559],  # Southeast  
    [39.8670, -74.9559],  # Southwest
    [39.8670, -75.2803],  # Northwest
    [40.1379, -75.2803]   # Close polygon
]

# Add county boundary as a distinct layer
county_layer = folium.FeatureGroup(name='📍 Philadelphia County Line', show=True)

folium.PolyLine(
    locations=philly_boundary,
    color='#FF0000',  # Bright red
    weight=3,
    opacity=0.9,
    popup='Philadelphia County Boundary',
    tooltip='Philadelphia County'
).add_to(county_layer)

county_layer.add_to(m)

print("   ✅ Philadelphia County boundary added (red line)")

# Add business locations with BOLD CONTRASTING markers
print("🏢 Adding BOLD business location markers...")

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

# BOLD current locations - LIME GREEN for high contrast
for loc in current_locations:
    # Larger, bolder circle
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,
        color='#00FF00',  # BRIGHT LIME GREEN (stands out)
        fill=True,
        fillColor='#00FF00',
        fillOpacity=0.08,
        weight=3  # Thicker line
    ).add_to(current_layer)
    
    # Larger, more contrasting marker
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=10,  # Bigger
        color='#000000',  # Black border
        fillColor='#00FF00',  # Bright lime green fill
        fillOpacity=1.0,
        weight=3,  # Bold border
        popup=f"<b style='font-size:14px;'>{loc['name']}</b><br><b>CURRENT LOCATION</b>",
        tooltip=f"<b>{loc['name']}</b><br>Current Location"
    ).add_to(current_layer)

# BOLD prospect locations - CYAN for high contrast
for loc in prospect_locations:
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,
        color='#00FFFF',  # BRIGHT CYAN (stands out)
        fill=False,
        weight=2.5  # Thicker
    ).add_to(prospect_layer)
    
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=9,  # Bigger
        color='#000000',  # Black border
        fillColor='#00FFFF',  # Bright cyan fill
        fillOpacity=1.0,
        weight=3,  # Bold border
        popup=f"<b style='font-size:14px;'>{loc['name']}</b><br><b>PROSPECT LOCATION</b>",
        tooltip=f"<b>{loc['name']}</b><br>Prospect Location"
    ).add_to(prospect_layer)

print(f"   ✅ Added {len(current_locations)} BOLD current (lime green)")
print(f"   ✅ Added {len(prospect_locations)} BOLD prospects (cyan)")

# Add all layers
current_layer.add_to(m)
prospect_layer.add_to(m)
for layer in layers.values():
    layer.add_to(m)

folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Enhanced title
title_html = '''
<div style="position: fixed; 
     top: 10px; left: 50px; width: 580px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid #333; border-radius: 5px; padding: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
     <h4 style="margin:0; color:#333;">NJ/DE/PA Business Locations + Demographics</h4>
     <p style="margin:5px 0 0 0; font-size:12px; color:#666;">
     <span style="color:#00FF00; font-weight:bold;">⬤ Lime = Current</span> | 
     <span style="color:#00FFFF; font-weight:bold;">⬤ Cyan = Prospects</span> | 
     <span style="color:#FF0000; font-weight:bold;">━ Red = Philly County</span>
     </p>
</div>
'''

legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 340px; height: auto;
     background-color: white; z-index:9999; font-size:11px;
     border:2px solid #333; border-radius: 5px; padding: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
     <h5 style="margin:0 0 10px 0; font-size:13px; color:#333;">Heat Map Color Scales</h5>
     <p style="font-size:10px; margin:0 0 8px 0; color:#666;"><b>Hover over areas to see city name + data</b></p>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">💰 Income:</b> 
         <div style="flex:1; height:14px; background: linear-gradient(to right, #E8F5E9, #66BB6A, #1B5E20); border-radius:3px; border:1px solid #ddd;"></div>
     </div>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">📊 Population:</b> 
         <div style="flex:1; height:14px; background: linear-gradient(to right, #E3F2FD, #42A5F5, #0D47A1); border-radius:3px; border:1px solid #ddd;"></div>
     </div>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">🏘️ Density:</b> 
         <div style="flex:1; height:14px; background: linear-gradient(to right, #F3E5F5, #AB47BC, #4A148C); border-radius:3px; border:1px solid #ddd;"></div>
     </div>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">👥 Age:</b> 
         <div style="flex:1; height:14px; background: linear-gradient(to right, #FFF3E0, #FF9800, #E65100); border-radius:3px; border:1px solid #ddd;"></div>
     </div>
     <div style="display:flex; align-items:center;">
         <b style="width:90px;">🏠 Housing:</b> 
         <div style="flex:1; height:14px; background: linear-gradient(to right, #FFEBEE, #EF5350, #B71C1C); border-radius:3px; border:1px solid #ddd;"></div>
     </div>
     <p style="font-size:9px; margin:8px 0 0 0; color:#888; text-align:center;">Light = Low | Dark = High</p>
</div>
'''

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

# Save
output_file = '/workspace/interactive-map-final.html'
m.save(output_file)

print(f"\n✅ FINAL POLISHED map saved: {output_file}")
print(f"\n🎨 FINAL TOUCHES:")
print(f"   ✅ City/town names show on hover")
print(f"   ✅ Philadelphia County boundary (red line)")
print(f"   ✅ BOLD markers with high-contrast colors:")
print(f"      - Current: LIME GREEN (#00FF00) - 10px radius")
print(f"      - Prospects: CYAN (#00FFFF) - 9px radius")
print(f"      - Black borders (3px) for extra visibility")
print(f"   ✅ Markers pop through heat maps")
print("\n" + "=" * 70)
