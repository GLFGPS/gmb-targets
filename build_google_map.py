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

# Load close rate data
print("📊 Loading close rate data...")
df_close = pd.read_csv('/workspace/close-rate-by-zip.csv', dtype={'Postal Code': str})
df_close['Postal Code'] = df_close['Postal Code'].str.strip()

# Roll up by zip code
df_close_rollup = df_close.groupby('Postal Code').agg({
    'Deal Count': 'sum',
    'Closed Won Count': 'sum'
}).reset_index()
df_close_rollup['Close Rate'] = (df_close_rollup['Closed Won Count'] / df_close_rollup['Deal Count'] * 100).round(1)

# Fix postal codes - pad with leading zero if needed (NJ zips)
df_customers['Postal Code'] = df_customers['Postal Code'].str.zfill(5)

# Get zip coordinates from customer data
zip_coords = df_customers.groupby('Postal Code').agg({
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()

# Merge close rates with coordinates
df_close_map = df_close_rollup.merge(zip_coords, on='Postal Code', how='inner')
df_close_map = df_close_map.dropna(subset=['Latitude', 'Longitude'])

print(f"   Close rate data: {len(df_close_map):,} zip codes with {df_close_rollup['Deal Count'].sum():,} total deals")

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

# GOOGLE LEADS CLUSTER (using proven cluster technology with same color scale as customers)
print("\n⭐ Google lead clusters...")
google_cluster = MarkerCluster(
    name='⭐ Google Lead Clusters',
    show=False,
    icon_create_function="""
    function(cluster) {
        var count = cluster.getChildCount();
        var color;
        var borderColor = '#000';
        var borderWidth = '3px';
        var boxShadow = '0 3px 10px rgba(0,0,0,0.4)';
        var size;
        
        // Same 9-tier gradient as Active Customer Clusters
        if (count < 50) {
            color = '#E6F9E6';  // Very light green
            size = 'small';
        } else if (count < 100) {
            color = '#90EE90';  // Light green
            size = 'small';
        } else if (count < 250) {
            color = '#FFFF00';  // Yellow
            size = 'medium';
        } else if (count < 500) {
            color = '#FFD700';  // Gold
            size = 'medium';
        } else if (count < 750) {
            color = '#FF8C00';  // Orange
            size = 'medium';
        } else if (count < 1000) {
            color = '#FF6347';  // Red-orange
            size = 'large';
        } else if (count < 2000) {
            color = '#FF4500';  // Orange-red
            size = 'large';
        } else if (count < 3000) {
            color = '#DC143C';  // Crimson red
            size = 'large';
        } else {
            // PREMIUM TIER: White with thick gold border and glow!
            color = '#FFFFFF';
            borderColor = '#FFD700';
            borderWidth = '6px';
            boxShadow = '0 0 20px rgba(255,215,0,0.8), 0 0 40px rgba(255,215,0,0.5), 0 4px 15px rgba(0,0,0,0.5)';
            size = 'xlarge';
        }
        
        var iconSize = size === 'xlarge' ? 70 : size === 'large' ? 60 : size === 'medium' ? 50 : 42;
        var fontSize = size === 'xlarge' ? '17px' : size === 'large' ? '15px' : '13px';
        var fontWeight = size === 'xlarge' ? '900' : 'bold';
        
        return L.divIcon({
            html: '<div style="background-color:' + color + '; width:' + iconSize + 'px; height:' + iconSize + 'px; border-radius:50%; border: ' + borderWidth + ' solid ' + borderColor + '; display:flex; align-items:center; justify-content:center; gap:2px; font-weight:' + fontWeight + '; font-size:' + fontSize + '; color:#000; box-shadow: ' + boxShadow + ';">⭐' + count + '</div>',
            className: 'google-cluster-icon',
            iconSize: L.point(iconSize, iconSize)
        });
    }
    """
)

for _, row in df_google.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5,
        color='#FFD700',
        fill=True,
        fillColor='#FFD700',
        fillOpacity=1.0,
        popup=f"⭐ <b>Google Lead</b><br>{row['Customer Source (GreenLawn)']}<br>{row['Customer Since'].strftime('%m/%d/%Y')}",
        tooltip="⭐ Google Lead"
    ).add_to(google_cluster)

google_cluster.add_to(m)
print(f"   ✅ Google clusters (All): {len(df_google):,} leads")

# CLOSE RATE MARKERS (sized by deal volume, colored by performance)
print("\n💰 Close rate by zip...")
close_rate_layer = folium.FeatureGroup(name='💰 Close Rate by Zip', show=False)

for _, row in df_close_map.iterrows():
    deals = int(row['Deal Count'])
    rate = row['Close Rate']
    
    # Color by performance
    if rate < 30: color = '#8B0000'
    elif rate < 40: color = '#DC143C'
    elif rate < 50: color = '#FF6347'
    elif rate < 60: color = '#FFD700'
    elif rate < 70: color = '#ADFF2F'
    elif rate < 80: color = '#7FFF00'
    elif rate < 90: color = '#00C957'
    else: color = '#006400'
    
    # Size by volume
    if deals < 20: size, font = 35, '11px'
    elif deals < 50: size, font = 45, '12px'
    elif deals < 100: size, font = 55, '13px'
    elif deals < 200: size, font = 65, '14px'
    else: size, font = 75, '16px'
    
    marker_html = f'<div style="background-color:{color};width:{size}px;height:{size}px;border-radius:50%;border:3px solid #000;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:bold;font-size:{font};color:#FFF;text-shadow:1px 1px 2px #000;box-shadow:0 3px 10px rgba(0,0,0,0.5);"><div>💰{deals}</div><div style="font-size:11px;">{rate:.0f}%</div></div>'
    
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        icon=folium.DivIcon(html=marker_html, icon_size=(size, size)),
        popup=f"<b>Zip {row['Postal Code']}</b><br>{deals} deals<br>{int(row['Closed Won Count'])} won<br>{rate:.1f}% close",
        tooltip=f"{row['Postal Code']}: {deals} deals, {rate:.0f}%"
    ).add_to(close_rate_layer)

close_rate_layer.add_to(m)
print(f"   ✅ Close rate markers: {len(df_close_map):,} zips")

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
print("   - Google Lead Clusters - 15K leads (2003-2025)")
print("   - Close Rate by Zip - 25K deals, 404 zips")
print("   - GMB locations (always on top)")
print("\n💡 Close Rate Color Scale:")
print("   🔴 Red (0-50%): Below/At Average")
print("   🟡 Gold (50-60%): Average")
print("   🟢 Green (60-100%): Above Average to Outstanding")
