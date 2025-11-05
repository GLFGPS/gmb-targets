#!/usr/bin/env python3
"""
Option A: Marker Clusters for Customer Visualization
"""

import folium
from folium.plugins import MarkerCluster
import pandas as pd

print("🗺️  Building Option A: Marker Clusters Map...")
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

# Create map
m = folium.Map(location=[40.0, -75.5], zoom_start=9, tiles='cartodbpositron', control_scale=True)

# Active Customer Clusters with Color Gradient
active_cluster = MarkerCluster(
    name='🎯 Active Customer Clusters',
    show=True,
    icon_create_function="""
    function(cluster) {
        var count = cluster.getChildCount();
        var color;
        var borderColor = '#000';
        var borderWidth = '3px';
        var boxShadow = '0 3px 10px rgba(0,0,0,0.4)';
        var size;
        
        // Enhanced 9-tier color gradient for active customers
        if (count < 50) {
            color = '#E6F9E6';  // Very light green
            size = 'small';
        } else if (count < 100) {
            color = '#90EE90';  // Light green
            size = 'small';
        } else if (count < 200) {
            color = '#9ACD32';  // Yellow-green
            size = 'medium';
        } else if (count < 400) {
            color = '#FFD700';  // Gold
            size = 'medium';
        } else if (count < 700) {
            color = '#FF8C00';  // Orange
            size = 'medium';
        } else if (count < 1000) {
            color = '#FF6347';  // Red-orange
            size = 'large';
        } else if (count < 2000) {
            color = '#FF4500';  // Orange-red
            size = 'large';
        } else if (count < 4000) {
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
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        color='#FF6600',
        fill=True,
        fillColor='#FF6600',
        fillOpacity=0.7
    ).add_to(active_cluster)
active_cluster.add_to(m)
print(f"   ✅ Active clusters: {len(df_active):,} points with color gradient")

# All Customer Clusters with Color Gradient
all_cluster = MarkerCluster(
    name='🎯 All Customer Clusters',
    show=False,
    icon_create_function="""
    function(cluster) {
        var count = cluster.getChildCount();
        var color;
        var borderColor = '#000';
        var borderWidth = '3px';
        var boxShadow = '0 3px 10px rgba(0,0,0,0.4)';
        var textColor = '#FFF';
        var size;
        
        // Enhanced 9-tier color gradient for all customers
        if (count < 50) {
            color = '#E6F5FF';  // Very light blue
            size = 'small';
        } else if (count < 100) {
            color = '#ADD8E6';  // Light blue
            size = 'small';
        } else if (count < 300) {
            color = '#87CEEB';  // Sky blue
            size = 'medium';
        } else if (count < 700) {
            color = '#4DA6FF';  // Medium blue
            size = 'medium';
        } else if (count < 1500) {
            color = '#0066CC';  // Blue
            size = 'medium';
        } else if (count < 2500) {
            color = '#0047AB';  // Dark blue
            size = 'large';
        } else if (count < 4000) {
            color = '#002366';  // Navy
            size = 'large';
        } else if (count < 6000) {
            color = '#001A4D';  // Deep navy
            size = 'large';
        } else {
            // PREMIUM TIER: White with thick gold border and glow!
            color = '#FFFFFF';
            borderColor = '#FFD700';
            borderWidth = '6px';
            boxShadow = '0 0 20px rgba(255,215,0,0.8), 0 0 40px rgba(255,215,0,0.5), 0 4px 15px rgba(0,0,0,0.5)';
            textColor = '#000';
            size = 'xlarge';
        }
        
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

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        color='#4DA6FF',
        fill=True,
        fillColor='#4DA6FF',
        fillOpacity=0.7
    ).add_to(all_cluster)
all_cluster.add_to(m)
print(f"   ✅ All clusters: {len(df):,} points with color gradient")

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

title_html = '''<div style="position: fixed; top: 10px; left: 50px; width: 600px; background-color: white; z-index:9999; font-size:14px; border:2px solid #333; border-radius: 8px; padding: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
<h4 style="margin:0; color:#333; font-size:16px;">Customer Cluster Analysis</h4>
<p style="margin:6px 0 0 0; font-size:13px; color:#666;">
<span style="display:inline-block; width:14px; height:14px; background:#FFFF00; border-radius:50%; border:4px solid #000; margin-right:6px;"></span><b>Current</b> |
<span style="display:inline-block; width:14px; height:14px; background:#FF6600; border-radius:50%; border:4px solid #000; margin:0 6px 0 12px;"></span><b>Prospects</b> |
<span style="margin-left:12px;">🟢→🟡→🟠→🔴 = More customers</span>
</p></div>'''
m.get_root().html.add_child(folium.Element(title_html))

m.save('/workspace/interactive-map.html')
print("✅ Customer Cluster Analysis Map saved!")
