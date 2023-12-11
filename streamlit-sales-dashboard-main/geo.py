import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster, HeatMap
from folium.features import GeoJson
import pandas as pd
import json
import altair as alt

# Sample data (replace with your actual data loading code)
# Example: df = pd.read_csv('your_data.csv')
# Ensure that your DataFrame has columns like 'Region', 'District', 'Event Time', 'Client'
df = pd.read_csv('output_updated.csv')

# Convert 'Event Time' column to datetime
df['Event Time'] = pd.to_datetime(df['Event Time'])

# Count the frequency of each district
district_counts = df['District'].value_counts().reset_index()
district_counts.columns = ['District', 'Count']

# Count the frequency of each region
region_counts = df['Region'].value_counts().reset_index()
region_counts.columns = ['Region', 'Count']

client_counts = df['Client'].value_counts().reset_index()
client_counts.columns = ['Client', 'Count']

# Define the custom order for regions
custom_region_order = ['RIO-1', 'RIO-2', 'RIO-3', 'RIO-4']

# Sort the regions based on the custom order
sorted_regions = sorted(region_counts['Region'].unique(), key=lambda x: custom_region_order.index(x) if x in custom_region_order else float('inf'))

@st.cache_data
def get_districts_in_region(data, selected_region):
    if selected_region != 'Overall':
        return list(data[data['Region'] == selected_region]['District'].unique())
    return list(data['District'].unique())


def filter_by_region(data, selected_region):
    if selected_region != 'Overall':
        return data[data['Region'] == selected_region]
    return data

def filter_by_district(data, selected_district):
    if selected_district != 'Overall':
        return data[data['District'] == selected_district]
    return data

def filter_by_date_range(data, date_range):
    if date_range[0] is not None and date_range[1] is not None:
        return data[(data['Event Time'].dt.date >= pd.to_datetime(date_range[0]).date()) & (data['Event Time'].dt.date <= pd.to_datetime(date_range[1]).date())]
    return data

def filter_by_clients(data, selected_clients):
    if selected_clients:
        return data[data['Client'].isin(selected_clients)]
    return data

def create_folium_map(data, geo_json_path='bd_jeoson.json'):
    m = folium.Map(location=[23.6850, 90.3563], zoom_start=6)

    # Load GeoJSON data
    geo_json_data = json.load(open(geo_json_path, 'r'))

    # Create GeoJson layer with style_function for key_on
    geojson = GeoJson(
        geo_json_data,
        name="geojson",
        style_function=lambda x: {
            'fillColor': 'blue',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.3
        }
    )

    # Add GeoJson layer to map
    geojson.add_to(m)

    # Extract GeoJSON features and create a list of (latitude, longitude) for heatmap
    heat_data = []
    for feature in geo_json_data['features']:
        geometry = feature['geometry']
        if geometry['type'] == 'Polygon':
            coordinates = geometry['coordinates'][0]  # Extract coordinates for the first ring
            heat_data.extend(coordinates)
        elif geometry['type'] == 'MultiPolygon':
            for polygon_coordinates in geometry['coordinates']:
                heat_data.extend(polygon_coordinates[0])

    # Add HeatMap layer with the GeoJSON geometry data
    HeatMap(heat_data).add_to(m)

    # Add Marker Cluster layer
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for each incident
    for _, row in data.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    return m

def display_total_count(filtered_df):
    total_count = len(filtered_df)
    st.sidebar.markdown(f"<p style='font-size:16px'>Total Count: <strong>{total_count}</strong></p>", unsafe_allow_html=True)

def display_heatmap_legend():
    st.markdown("""
        **Heatmap Legend:**
        - Intensity of red color represents incident density
    """)

import altair as alt

def display_date_bar_chart(filtered_df):
    date_count = filtered_df['Event Time'].dt.date.value_counts().reset_index()
    date_count.columns = ['Date', 'Count']

    # Filter out dates with zero count
    date_count_filtered = date_count[date_count['Count'] > 0]

    # Filter data to include only dates with count > 1
    date_count_filtered_labels = date_count_filtered[date_count_filtered['Count'] > 1]

    # Stacked Bar Chart
    stacked_bar_chart = alt.Chart(date_count_filtered).mark_bar().encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%d-%m-%y', labelOverlap=True)),
        y='Count:Q',
        color='Date:T',
        tooltip=['Date', 'Count']
    ).properties(
        title='Stacked Incident Count by Date'
    )

    # Create a separate DataFrame for labels
    labels = date_count_filtered_labels.copy()
    labels['label'] = labels['Count']

    # Add text marks for labels
    text = alt.Chart(labels).mark_text(
        align='center',
        baseline='top',
        dy=-5,
        color='black'
    ).encode(
        x='Date:T',
        y='Count:Q',
        text='label:Q'
    )

    st.altair_chart(stacked_bar_chart + text, use_container_width=True)









# Streamlit app title
st.title("Network Outages in Bangladesh")

# Sidebar for filtering options
selected_region = st.sidebar.selectbox("Select a Region", ['Overall'] + sorted_regions)
districts_in_selected_region = get_districts_in_region(df, selected_region)
selected_district = st.sidebar.selectbox("Select a District", ['Overall'] + districts_in_selected_region)
selected_clients = st.sidebar.multiselect("Select Clients", list(client_counts['Client']))
date_range = st.sidebar.date_input("Select Date Range", [df['Event Time'].min(), df['Event Time'].max()], key="daterange")

# Apply filters
filtered_data = filter_by_region(df, selected_region)
filtered_data = filter_by_district(filtered_data, selected_district)
filtered_data = filter_by_date_range(filtered_data, date_range)
filtered_data = filter_by_clients(filtered_data, selected_clients)

# Display total count based on the applied filters
display_total_count(filtered_data)

# Create and display Folium map
folium_static(create_folium_map(filtered_data))


# Display heatmap legend
display_heatmap_legend()

# Add some vertical space before the bar chart
st.markdown("<br>", unsafe_allow_html=True)

# Display interactive bar chart based on date
display_date_bar_chart(filtered_data)
