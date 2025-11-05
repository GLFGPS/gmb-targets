#!/usr/bin/env python3
"""
Merged Customer & Demographics Analysis Map with Google Lead Growth
Optimized with single marker set and JavaScript filtering
"""

import folium
from folium.plugins import MarkerCluster, Geocoder
import pandas as pd
from branca.colormap import LinearColormap
import json

print("🗺️  Building Complete Analysis Map with Google Leads...")
print("=" * 70)

# Load census tract data
print("📊 Loading census tract demographics...")
df_census = pd.read_csv('/workspace/complete_census_all_nj_with_cities.csv', dtype={'geoid': str})
df_census = df_census[df_census['geometry'].notna()]
print(f"   Census tracts: {len(df_census):,}")

# Load customer data
print("📊 Loading customer data...")
df_customers = pd.read_csv('/workspace/customer_locations.csv', dtype={'Postal Code': str})
df_customers.columns = df_customers.columns.str.strip()
df_customers['Latitude'] = pd.to_numeric(df_customers['Latitude'], errors='coerce')
df_customers['Longitude'] = pd.to_numeric(df_customers['Longitude'], errors='coerce')
df_customers['Customer Status'] = pd.to_numeric(df_customers['Customer Status'], errors='coerce')
df_customers = df_customers.dropna(subset=['Latitude', 'Longitude'])
df_customers['Customer Since'] = pd.to_datetime(df_customers['Customer Since'], errors='coerce')

# Extract Google leads
df_google = df_customers[df_customers['Customer Source (GreenLawn)'].str.contains('Google', case=False, na=False)].copy()
df_google = df_google.dropna(subset=['Customer Since'])
df_google['Year'] = df_google['Customer Since'].dt.year

df_active = df_customers[df_customers['Customer Status'] == 9.0].copy()

print(f"   Customers: {len(df_customers):,} total, {len(df_active):,} active")
print(f"   Google leads: {len(df_google):,}")

# Create map
m = folium.Map(location=[40.0, -75.5], zoom_start=9, tiles='cartodbpositron', control_scale=True)

# CENSUS TRACTS
print("\n🎨 Census tract demographics...")
demographics_config = {
    'median_income': ('💰 Median Income', 'income'),
    'population': ('📊 Population', 'population'),
    'density': ('🏘️ Population Density', 'density'),
    'median_home_value': ('🏡 Median Home Value', 'homevalue')
}

exclude_counties = ['Hudson', 'Bergen', 'Essex', 'Union', 'Philadelphia', 'Passaic', 'Cape May']
beach_cities = {
    'Atlantic': ['Atlantic', 'Atlantic City', 'Ventnor', 'Margate', 'Longport', 'Brigantine', 
                 'Ocean City', 'Sea Isle City', 'Avalon', 'Stone Harbor'],
    'Monmouth': ['Long Branch', 'Asbury Park', 'Ocean Grove', 'Bradley Beach', 
                 'Avon-by-the-Sea', 'Belmar', 'Spring Lake', 'Sea Girt', 'Manasquan',
                 'Sea Bright', 'Monmouth Beach', 'Rumson', 'Fair Haven'],
    'Ocean': ['Point Pleasant Beach', 'Bay Head', 'Mantoloking',
              'Seaside Heights', 'Seaside Park', 'Island Heights', 'Lavallette',
              'Beach Haven', 'Long Beach', 'Barnegat Light']
}

for demo, (layer_name, demo_type) in demographics_config.items():
    features = []
    for idx, row in df_census.iterrows():
        if pd.notna(row['geometry']):
            county = row.get('county_name', '')
            city = row.get('city', '')
            if demo in ['density', 'median_home_value']:
                if county in exclude_counties:
                    continue
                if county in beach_cities:
                    is_coastal = False
                    for beach_city in beach_cities[county]:
                        if beach_city.lower() in city.lower():
                            is_coastal = True
                            break
                    if is_coastal:
                        continue
            try:
                geometry_data = json.loads(row['geometry'])
                value = row[demo] if pd.notna(row[demo]) else 0
                feature = {
                    "type": "Feature",
                    "geometry": geometry_data,
                    "properties": {
                        "geoid": row['geoid'],
                        "city": row.get('city', 'Unknown'),
                        "county": row.get('county_name', 'Unknown'),
                        "value": float(value) if value else 0,
                        "demo": demo
                    }
                }
                features.append(feature)
            except:
                pass
    
    if len(features) == 0:
        continue
    
    feature_collection = {"type": "FeatureCollection", "features": features}
    min_val = df_census[demo].min()
    max_val = df_census[demo].max()
    
    if demo == 'density':
        max_val = min(max_val, 8000)
    if demo == 'median_home_value':
        max_val = min(max_val, 1000000)
    
    colormap = LinearColormap(
        colors=['#F7FFF7', '#00AA00', '#004D00'] if demo == 'median_income' 
        else ['#F0F8FF', '#0066CC', '#00008B'] if demo == 'population'
        else ['#FDF5FF', '#7B2D9E', '#2E0854'] if demo == 'density'
        else ['#FFF5E6', '#FF8C00', '#CC5500'],
        vmin=min_val,
        vmax=max_val
    )
    
    def style_function(feature, colormap=colormap, demo=demo, max_val=max_val):
        value = feature['properties']['value']
        if demo in ['density', 'median_home_value'] and value > max_val:
            value = max_val
        return {
            'fillColor': colormap(value),
            'color': colormap(value),
            'weight': 0.5,
            'fillOpacity': 0.7
        }
    
    layer = folium.FeatureGroup(name=f'📊 {layer_name}', show=False)
    folium.GeoJson(
        feature_collection,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['city', 'geoid', 'value'],
            aliases=['City:', 'Tract:', f'{layer_name}:'],
            localize=True
        )
    ).add_to(layer)
    layer.add_to(m)
    print(f"   ✅ {layer_name}: {len(features)} tracts")

# CUSTOMER CLUSTERS
print("\n🎯 Customer clusters...")
active_cluster = MarkerCluster(
    name='🎯 Active Customer Clusters',
    show=False,
    icon_create_function="""
    function(cluster) {
        var count = cluster.getChildCount();
        var color, borderColor = '#000', borderWidth = '3px', boxShadow = '0 3px 10px rgba(0,0,0,0.4)', size;
        if (count < 50) { color = '#E6F9E6'; size = 'small';
        } else if (count < 100) { color = '#90EE90'; size = 'small';
        } else if (count < 250) { color = '#FFFF00'; size = 'medium';
        } else if (count < 500) { color = '#FFD700'; size = 'medium';
        } else if (count < 750) { color = '#FF8C00'; size = 'medium';
        } else if (count < 1000) { color = '#FF6347'; size = 'large';
        } else if (count < 2000) { color = '#FF4500'; size = 'large';
        } else if (count < 3000) { color = '#DC143C'; size = 'large';
        } else { color = '#FFFFFF'; borderColor = '#FFD700'; borderWidth = '6px'; 
                 boxShadow = '0 0 20px rgba(255,215,0,0.8), 0 0 40px rgba(255,215,0,0.5), 0 4px 15px rgba(0,0,0,0.5)'; size = 'xlarge'; }
        var iconSize = size === 'xlarge' ? 60 : size === 'large' ? 52 : size === 'medium' ? 42 : 35;
        var fontSize = size === 'xlarge' ? '16px' : '14px';
        var fontWeight = size === 'xlarge' ? '900' : 'bold';
        return L.divIcon({
            html: '<div style="background-color:' + color + '; width:' + iconSize + 'px; height:' + iconSize + 'px; border-radius:50%; border: ' + borderWidth + ' solid ' + borderColor + '; display:flex; align-items:center; justify-content:center; font-weight:' + fontWeight + '; font-size:' + fontSize + '; color:#000; box-shadow: ' + boxShadow + ';">' + count + '</div>',
            className: 'custom-cluster-icon',
            iconSize: L.point(iconSize, iconSize)
        });
    }
    """
)
for _, row in df_active.iterrows():
    folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=3, color='#FF6600', fill=True, fillColor='#FF6600', fillOpacity=0.7).add_to(active_cluster)
active_cluster.add_to(m)

all_cluster = MarkerCluster(
    name='🎯 All Customer Clusters',
    show=False,
    icon_create_function="""
    function(cluster) {
        var count = cluster.getChildCount();
        var color, borderColor = '#000', borderWidth = '3px', boxShadow = '0 3px 10px rgba(0,0,0,0.4)', textColor = '#FFF', size;
        if (count < 50) { color = '#E6F5FF'; size = 'small';
        } else if (count < 100) { color = '#ADD8E6'; size = 'small';
        } else if (count < 300) { color = '#87CEEB'; size = 'medium';
        } else if (count < 700) { color = '#4DA6FF'; size = 'medium';
        } else if (count < 1500) { color = '#0066CC'; size = 'medium';
        } else if (count < 2500) { color = '#0047AB'; size = 'large';
        } else if (count < 4000) { color = '#002366'; size = 'large';
        } else if (count < 6000) { color = '#001A4D'; size = 'large';
        } else { color = '#FFFFFF'; borderColor = '#FFD700'; borderWidth = '6px';
                 boxShadow = '0 0 20px rgba(255,215,0,0.8), 0 0 40px rgba(255,215,0,0.5), 0 4px 15px rgba(0,0,0,0.5)'; textColor = '#000'; size = 'xlarge'; }
        var iconSize = size === 'xlarge' ? 60 : size === 'large' ? 52 : size === 'medium' ? 42 : 35;
        var fontSize = size === 'xlarge' ? '16px' : '14px';
        var fontWeight = size === 'xlarge' ? '900' : 'bold';
        return L.divIcon({
            html: '<div style="background-color:' + color + '; width:' + iconSize + 'px; height:' + iconSize + 'px; border-radius:50%; border: ' + borderWidth + ' solid ' + borderColor + '; display:flex; align-items:center; justify-content:center; font-weight:' + fontWeight + '; font-size:' + fontSize + '; color:' + textColor + '; box-shadow: ' + boxShadow + ';">' + count + '</div>',
            className: 'custom-cluster-icon',
            iconSize: L.point(iconSize, iconSize)
        });
    }
    """
)
for _, row in df_customers.iterrows():
    folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=3, color='#4DA6FF', fill=True, fillColor='#4DA6FF', fillOpacity=0.7).add_to(all_cluster)
all_cluster.add_to(m)
print(f"   ✅ Active: {len(df_active):,}, All: {len(df_customers):,}")

# GOOGLE LEADS (Simple single layer - ALL Google leads)
print("\n⭐ Google leads (all-time)...")
google_layer = folium.FeatureGroup(name='⭐ Google Leads (All)', show=False)
for _, row in df_google.iterrows():
    # Large visible gold circles
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=8,
        color='#000000',
        weight=3,
        fill=True,
        fillColor='#FFD700',
        fillOpacity=1.0,
        popup=f"⭐ <b>Google Lead</b><br>{row['Customer Source (GreenLawn)']}<br>{row['Customer Since'].strftime('%m/%d/%Y')}",
        tooltip="⭐ Google Lead"
    ).add_to(google_layer)
google_layer.add_to(m)
print(f"   ✅ {len(df_google):,} Google lead markers")

# GMB LOCATIONS
print("\n🏢 GMB locations...")
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

current_layer = folium.FeatureGroup(name='🟢 Current GMB Locations', show=True)
for loc in current_locations:
    folium.CircleMarker(location=[loc['lat'], loc['lon']], radius=22, color='#FFFFFF', fillColor='#FFFFFF', fillOpacity=0.9, weight=0).add_to(current_layer)
    icon_html = f'<div style="width:36px;height:36px;background-color:#FFFF00;border:5px solid #000000;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:bold;box-shadow:0 0 15px rgba(0,0,0,0.8), 0 0 30px rgba(255,255,0,0.6);cursor:pointer;">🟢</div>'
    folium.Marker(location=[loc['lat'], loc['lon']], icon=folium.DivIcon(html=icon_html), popup=f"<b style='font-size:16px;'>{loc['name']}</b><br><b>CURRENT LOCATION</b>", tooltip=f"<b>{loc['name']}</b>").add_to(current_layer)
current_layer.add_to(m)

prospect_layer = folium.FeatureGroup(name='🔵 Prospect GMB Locations', show=True)
for loc in prospect_locations:
    folium.CircleMarker(location=[loc['lat'], loc['lon']], radius=21, color='#FFFFFF', fillColor='#FFFFFF', fillOpacity=0.9, weight=0).add_to(prospect_layer)
    icon_html = f'<div style="width:34px;height:34px;background-color:#FF6600;border:5px solid #000000;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:bold;box-shadow:0 0 15px rgba(0,0,0,0.8), 0 0 30px rgba(255,102,0,0.6);cursor:pointer;">🔵</div>'
    folium.Marker(location=[loc['lat'], loc['lon']], icon=folium.DivIcon(html=icon_html), popup=f"<b style='font-size:16px;'>{loc['name']}</b><br><b>PROSPECT LOCATION</b>", tooltip=f"<b>{loc['name']}</b>").add_to(prospect_layer)
prospect_layer.add_to(m)
print(f"   ✅ Current: {len(current_locations)}, Prospects: {len(prospect_locations)}")

# Add controls
Geocoder(collapsed=False, position='topleft', placeholder='Search address, city, or zip code...', add_marker=False).add_to(m)
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Title
title_html = '<div style="position:fixed;top:10px;left:50px;width:380px;height:auto;background-color:white;z-index:9999;font-size:14px;border:2px solid #333;border-radius:8px;padding:12px;box-shadow:0 4px 12px rgba(0,0,0,0.15);"><h4 style="margin:0;color:#333;font-size:16px;">Customer & Demographics Analysis</h4></div>'
m.get_root().html.add_child(folium.Element(title_html))

m.save('/workspace/interactive-map.html')

print("\n✅ Complete! Map saved to interactive-map.html")
print("=" * 70)
print("\n📋 Layers:")
print("   - Census tract demographics (4 layers)")
print("   - Customer clusters (Active & All)")
print("   - Google Leads (All) - Single layer in top-right control")
print("   - GMB locations (always on top)")
