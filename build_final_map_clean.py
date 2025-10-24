#!/usr/bin/env python3
"""
Final clean build - markers on top, extreme contrast
"""

import folium
import pandas as pd

print("🗺️  Building final map with extreme contrast + markers on top...")
print("=" * 70)

df = pd.read_csv('/workspace/complete_demographic_data.csv', dtype={'zip_code': str})
print(f"📊 Loaded {len(df)} zip codes")

# Create map
m = folium.Map(location=[40.1, -74.9], zoom_start=9, tiles='cartodbpositron', control_scale=True)

# Color interpolation function
def interpolate_color(val, c_low, c_high):
    r_low = int(c_low[1:3], 16)
    g_low = int(c_low[3:5], 16)
    b_low = int(c_low[5:7], 16)
    r_high = int(c_high[1:3], 16)
    g_high = int(c_high[3:5], 16)
    b_high = int(c_high[5:7], 16)
    r = int(r_low + (r_high - r_low) * val)
    g = int(g_low + (g_high - g_low) * val)
    b = int(b_low + (b_high - b_low) * val)
    return f'#{r:02x}{g:02x}{b:02x}'

# Demographics with EXTREME contrast
demographics_config = {
    'median_income': ('💰 Median Income', '#F7FFF7', '#004D00'),
    'population': ('📊 Population', '#F0F8FF', '#00008B'),
    'density': ('🏘️ Population Density', '#FDF5FF', '#2E0854'),
    'median_age': ('👥 Median Age', '#FFFBF0', '#B34400'),
    'housing_units': ('🏠 Housing Units', '#FFF5F5', '#8B0000')
}

demo_layers = {}

print("🎨 Creating heat map layers...")
for demo, (layer_name, color_low, color_high) in demographics_config.items():
    layer = folium.FeatureGroup(name=layer_name, show=False)
    min_val, max_val = df[demo].min(), df[demo].max()
    
    for idx, row in df.iterrows():
        norm = (row[demo] - min_val) / (max_val - min_val)
        color = interpolate_color(norm, color_low, color_high)
        
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=3000,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=0,
            tooltip=f"<b>{row.get('city', 'Unknown')}</b><br>ZIP: {row['zip_code']}<br>{layer_name}: ${row[demo]:,.0f}" if demo == 'median_income' else f"<b>{row.get('city', 'Unknown')}</b><br>ZIP: {row['zip_code']}<br>{layer_name}: {row[demo]:,.0f}"
        ).add_to(layer)
    
    demo_layers[demo] = layer
    print(f"   ✅ {layer_name}")

# Business locations
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

print("🏢 Creating BOLD business markers...")

current_layer = folium.FeatureGroup(name='🟢 Current Locations', show=True)
prospect_layer = folium.FeatureGroup(name='🔵 Prospective Locations', show=True)

# Current locations - Bold markers ONLY (no outer rings)
for loc in current_locations:
    # White halo for contrast
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=22,
        color='#FFFFFF',
        fillColor='#FFFFFF',
        fillOpacity=0.9,
        weight=0
    ).add_to(current_layer)
    
    # Custom icon marker - ALWAYS renders on top
    icon_html = f"""
    <div style="
        width: 36px;
        height: 36px;
        background-color: #FFFF00;
        border: 5px solid #000000;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(0,0,0,0.8), 0 0 30px rgba(255,255,0,0.6);
        cursor: pointer;
    ">🟢</div>
    """
    
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        icon=folium.DivIcon(html=icon_html),
        popup=f"<b style='font-size:16px;'>{loc['name']}</b><br><b>CURRENT LOCATION</b>",
        tooltip=f"<b>{loc['name']}</b>"
    ).add_to(current_layer)

# Prospects - Use Marker with custom DivIcon (renders in markerPane - ALWAYS on top)
for loc in prospect_locations:
    # 5-mile radius ring
    folium.Circle(
        location=[loc['lat'], loc['lon']],
        radius=8046.72,
        color='#FF6600',
        fill=False,
        weight=3.5
    ).add_to(prospect_layer)
    
    # White halo for contrast
    folium.CircleMarker(
        location=[loc['lat'], loc['lon']],
        radius=21,
        color='#FFFFFF',
        fillColor='#FFFFFF',
        fillOpacity=0.9,
        weight=0
    ).add_to(prospect_layer)
    
    # Custom icon marker - ALWAYS renders on top
    icon_html = f"""
    <div style="
        width: 34px;
        height: 34px;
        background-color: #FF6600;
        border: 5px solid #000000;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(0,0,0,0.8), 0 0 30px rgba(255,102,0,0.6);
        cursor: pointer;
    ">🔵</div>
    """
    
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        icon=folium.DivIcon(html=icon_html),
        popup=f"<b style='font-size:16px;'>{loc['name']}</b><br><b>PROSPECT LOCATION</b>",
        tooltip=f"<b>{loc['name']}</b>"
    ).add_to(prospect_layer)

print("   ✅ Ultra-bold markers created")

# LAYER ORDERING - CRITICAL!
print("\n📐 Adding layers in correct order...")

# STEP 1: Add demographic layers FIRST (bottom)
for dlayer in demo_layers.values():
    dlayer.add_to(m)
print("   ✅ Heat maps added (bottom layer)")

# STEP 2: Add business markers LAST (top - always visible)
current_layer.add_to(m)
prospect_layer.add_to(m)
print("   ✅ Business markers added (TOP LAYER - always shine through)")

folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Title and legend
title_html = '''
<div style="position: fixed; top: 10px; left: 50px; width: 600px; height: auto;
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid #333; border-radius: 8px; padding: 14px; 
     box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
     <h4 style="margin:0; color:#333; font-size:16px;">NJ/DE/PA Market Demographics</h4>
     <p style="margin:6px 0 0 0; font-size:13px; color:#666;">
     <span style="display:inline-block; width:14px; height:14px; background:#FFFF00; border-radius:50%; border:4px solid #000; margin-right:6px;"></span><b>Current</b> |
     <span style="display:inline-block; width:14px; height:14px; background:#FF6600; border-radius:50%; border:4px solid #000; margin:0 6px 0 12px;"></span><b>Prospects</b>
     </p>
</div>
'''

legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 360px; height: auto;
     background-color: white; z-index:9999; font-size:11px;
     border:2px solid #333; border-radius: 8px; padding: 14px; 
     box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
     <h5 style="margin:0 0 12px 0; font-size:14px; color:#333; font-weight:600;">Demographic Heat Maps</h5>
     <p style="font-size:10px; margin:0 0 10px 0; color:#666;"><b>Hover to see city + data</b></p>
     <div style="margin-bottom:8px;">
         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
             <b style="font-size:12px;">💰 Income</b>
             <span style="font-size:9px; color:#888;">Low → High</span>
         </div>
         <div style="height:18px; background: linear-gradient(to right, #F7FFF7, #008000, #004D00); 
                     border-radius:4px; border:1px solid #ddd;"></div>
     </div>
     <div style="margin-bottom:8px;">
         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
             <b style="font-size:12px;">📊 Population</b>
             <span style="font-size:9px; color:#888;">Low → High</span>
         </div>
         <div style="height:18px; background: linear-gradient(to right, #F0F8FF, #0066CC, #00008B); 
                     border-radius:4px; border:1px solid #ddd;"></div>
     </div>
     <div style="margin-bottom:8px;">
         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
             <b style="font-size:12px;">🏘️ Density</b>
             <span style="font-size:9px; color:#888;">Low → High</span>
         </div>
         <div style="height:18px; background: linear-gradient(to right, #FDF5FF, #7B2D9E, #2E0854); 
                     border-radius:4px; border:1px solid #ddd;"></div>
     </div>
     <div style="margin-bottom:8px;">
         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
             <b style="font-size:12px;">👥 Age</b>
             <span style="font-size:9px; color:#888;">Low → High</span>
         </div>
         <div style="height:18px; background: linear-gradient(to right, #FFFBF0, #FF8C00, #B34400); 
                     border-radius:4px; border:1px solid #ddd;"></div>
     </div>
     <div>
         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
             <b style="font-size:12px;">🏠 Housing</b>
             <span style="font-size:9px; color:#888;">Low → High</span>
         </div>
         <div style="height:18px; background: linear-gradient(to right, #FFF5F5, #DC143C, #8B0000); 
                     border-radius:4px; border:1px solid #ddd;"></div>
     </div>
</div>
'''

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

m.save('/workspace/interactive-map-final-clean.html')

print("\n✅ Map saved with:")
print("   • Heat maps underneath")
print("   • Markers on top (always visible)")
print("   • Extreme contrast colors")
print("   • Yellow current, orange prospects")
print("=" * 70)
