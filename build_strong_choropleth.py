#!/usr/bin/env python3
"""
Build STRONG choropleth map with better colors and larger coverage
"""

import folium
import pandas as pd
import numpy as np

print("🗺️  Building ENHANCED choropleth with strong visual contrast...")
print("=" * 70)

# Read demographic data
df = pd.read_csv('/workspace/complete_demographic_data.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes")

# IMPROVED COLOR FUNCTIONS with much better contrast
def get_strong_color(value, min_val, max_val, scheme):
    """
    Generate colors with MUCH stronger contrast and visual appeal
    """
    # Normalize 0-1
    norm = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    norm = max(0, min(1, norm))
    
    if scheme == 'income':
        # GREEN: Strong gradient from light yellow-green to deep forest green
        # Low income: Light yellow-green (#E8F5E9)
        # Mid income: Medium green (#66BB6A)
        # High income: Deep forest green (#1B5E20)
        if norm < 0.33:
            # Light green range
            t = norm / 0.33
            r = int(232 - (232 - 102) * t)
            g = int(245 - (245 - 187) * t)
            b = int(233 - (233 - 106) * t)
        elif norm < 0.67:
            # Medium green range
            t = (norm - 0.33) / 0.34
            r = int(102 - (102 - 27) * t)
            g = int(187 - (187 - 94) * t)
            b = int(106 - (106 - 32) * t)
        else:
            # Dark green range
            t = (norm - 0.67) / 0.33
            r = int(27 - (27 - 11) * t)
            g = int(94 - (94 - 56) * t)
            b = int(32 - (32 - 10) * t)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    elif scheme == 'population':
        # BLUE: Light sky blue to deep navy
        # Low pop: Very light blue (#E3F2FD)
        # Mid pop: Medium blue (#42A5F5)
        # High pop: Deep navy (#0D47A1)
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
        # PURPLE: Light lavender to deep purple
        # Low density: Light lavender (#F3E5F5)
        # Mid density: Medium purple (#AB47BC)
        # High density: Deep purple (#4A148C)
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
        # ORANGE: Light peach to deep orange-red
        # Young: Light peach (#FFF3E0)
        # Mid age: Bright orange (#FF9800)
        # Old: Deep orange-red (#E65100)
        if norm < 0.33:
            t = norm / 0.33
            r = 255
            g = int(243 - (243 - 152) * t)
            b = int(224 - 224 * t)
        elif norm < 0.67:
            t = (norm - 0.33) / 0.34
            r = 255
            g = int(152 - (152 - 81) * t)
            b = int(0)
        else:
            t = (norm - 0.67) / 0.33
            r = int(255 - (255 - 230) * t)
            g = int(81 - 81 * t)
            b = 0
        return f'#{r:02x}{g:02x}{b:02x}'
    
    elif scheme == 'housing':
        # RED: Light pink to deep red
        # Few units: Light pink (#FFEBEE)
        # Mid units: Medium red (#EF5350)
        # Many units: Deep red (#B71C1C)
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

print("🎨 Recalculating colors with enhanced contrast...")

# Recalculate all colors with new strong gradients
for col, scheme in [('population', 'population'), ('median_income', 'income'), 
                     ('median_age', 'age'), ('housing_units', 'housing'), 
                     ('density', 'density')]:
    min_val, max_val = df[col].min(), df[col].max()
    
    color_col = {'population': 'pop', 'median_income': 'income', 
                 'median_age': 'age', 'housing_units': 'housing', 'density': 'density'}[col]
    
    df[f'{color_col}_color'] = df[col].apply(
        lambda x: get_strong_color(x, min_val, max_val, scheme)
    )
    
    print(f"   ✅ {col}: ${min_val:,.0f} → ${max_val:,.0f}" if col == 'median_income' 
          else f"   ✅ {col}: {min_val:,.0f} → {max_val:,.0f}")

# Create base map
center_lat = 40.1
center_lon = -74.9

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles='cartodbpositron',
    control_scale=True
)

print("\n🗺️  Creating LARGER polygons for better coverage...")

# LARGER polygon size - much better coverage
def create_large_polygon(lat, lon, size=0.04):
    """Create a LARGER polygon around zip center for better fill"""
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

# Create GeoJSON layers
demographics = {
    'population': ('📊 Population', 'pop_color'),
    'density': ('🏘️ Population Density', 'density_color'),
    'median_income': ('💰 Median Income', 'income_color'),
    'median_age': ('👥 Median Age', 'age_color'),
    'housing_units': ('🏠 Housing Units', 'housing_color')
}

layers = {}

for demo, (layer_name, color_col) in demographics.items():
    print(f"   Building {layer_name}...")
    
    features = []
    for idx, row in df.iterrows():
        poly = create_large_polygon(row['lat'], row['lon'], size=0.04)  # MUCH LARGER
        poly['properties'] = {
            'zip_code': row['zip_code'],
            'value': f"{row[demo]:,.0f}",
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
            'fillOpacity': 0.75  # Higher opacity for stronger colors
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['zip_code', 'value'],
            aliases=['ZIP:', f'{demo.replace("_", " ").title()}:'],
            localize=True
        )
    ).add_to(layer)
    
    layers[demo] = layer

print("   ✅ All layers created with enhanced visuals")

# Add business locations
print("\n🏢 Adding business location markers...")

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

for loc in current_locations:
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,
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

# Add all layers
current_layer.add_to(m)
prospect_layer.add_to(m)
for layer in layers.values():
    layer.add_to(m)

folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Enhanced title and legend
title_html = '''
<div style="position: fixed; 
     top: 10px; left: 50px; width: 550px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid grey; border-radius: 5px; padding: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
     <h4 style="margin:0;">NJ/DE/PA Business Locations + Demographics</h4>
     <p style="margin:5px 0 0 0; font-size:12px;">
     🟢 Green = Current | 🔵 Blue = Prospects | <b>Toggle heat maps for insights</b>
     </p>
</div>
'''

legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 340px; height: auto;
     background-color: white; z-index:9999; font-size:11px;
     border:2px solid grey; border-radius: 5px; padding: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
     <h5 style="margin:0 0 10px 0; font-size:13px;">Heat Map Color Scales</h5>
     <p style="font-size:10px; margin:0 0 8px 0; color:#666;"><b>Strong contrast for easy identification</b></p>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">💰 Income:</b> 
         <div style="flex:1; height:12px; background: linear-gradient(to right, #E8F5E9, #66BB6A, #1B5E20); border-radius:3px;"></div>
     </div>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">📊 Population:</b> 
         <div style="flex:1; height:12px; background: linear-gradient(to right, #E3F2FD, #42A5F5, #0D47A1); border-radius:3px;"></div>
     </div>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">🏘️ Density:</b> 
         <div style="flex:1; height:12px; background: linear-gradient(to right, #F3E5F5, #AB47BC, #4A148C); border-radius:3px;"></div>
     </div>
     <div style="margin-bottom:6px; display:flex; align-items:center;">
         <b style="width:90px;">👥 Age:</b> 
         <div style="flex:1; height:12px; background: linear-gradient(to right, #FFF3E0, #FF9800, #E65100); border-radius:3px;"></div>
     </div>
     <div style="display:flex; align-items:center;">
         <b style="width:90px;">🏠 Housing:</b> 
         <div style="flex:1; height:12px; background: linear-gradient(to right, #FFEBEE, #EF5350, #B71C1C); border-radius:3px;"></div>
     </div>
     <p style="font-size:9px; margin:8px 0 0 0; color:#888; text-align:center;">Light = Low | Dark = High</p>
</div>
'''

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

# Save
output_file = '/workspace/interactive-map-enhanced.html'
m.save(output_file)

print(f"\n✅ Enhanced choropleth map saved: {output_file}")
print(f"\n🎨 IMPROVEMENTS:")
print(f"   • 2.7x LARGER polygons (0.04 vs 0.015)")
print(f"   • STRONGER color gradients with 3-tier contrast")
print(f"   • 75% opacity for vibrant colors")
print(f"   • Enhanced legend with gradient bars")
print(f"   • Better visual differentiation between values")
print("\n" + "=" * 70)
