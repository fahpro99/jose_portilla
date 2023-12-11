import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import pandas as pd
import altair as alt

# Sample data (replace with your actual data loading code)
df = pd.read_csv('output.csv')

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

# Streamlit app title
st.title("Network outages in Bangladesh")

# Sidebar for filtering options
selected_region = st.sidebar.selectbox("Select a Region", ['Overall'] + list(region_counts['Region']))
selected_clients = st.sidebar.multiselect("Select Clients", list(client_counts['Client']))

# Filter DataFrame based on selected region and clients
filtered_df = df.copy()

if selected_region != 'Overall':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    # Create a new dataframe for district counts based on the selected region
    district_counts = filtered_df['District'].value_counts().reset_index()
    district_counts.columns = ['District', 'Count']

# Update the list of districts based on the selected region
selected_districts = st.sidebar.selectbox("Select Districts", ['Overall'] + list(district_counts['District']))

if selected_districts != 'Overall':
    filtered_df = filtered_df[filtered_df['District'] == selected_districts]

if selected_clients:
    filtered_df = filtered_df[filtered_df['Client'].isin(selected_clients)]

# Create a Folium map centered on Bangladesh
m = folium.Map(location=[23.6850, 90.3563], zoom_start=6)

# Add HeatMap layer with the frequency data
heat_data = filtered_df[['Latitude', 'Longitude']].values
HeatMap(heat_data).add_to(m)

# Add layer control to the map
folium.LayerControl().add_to(m)

# Display legend inside Streamlit
st.markdown("""
    **Heatmap Legend:**
    - Intensity of red color represents incident density
""")

# Streamlit map display
folium_static(m)  # Use folium_static to embed the Folium map in Streamlit

# Interactive bar chart based on day_name
day_count = filtered_df['Event Time'].dt.day_name().value_counts().reset_index()
day_count.columns = ['Day', 'Count']

# Create Altair bar chart
bar_chart = alt.Chart(day_count).mark_bar().encode(
    x='Day:O',
    y='Count:Q',
    tooltip=['Day', 'Count']
).properties(
    title='Incident Count by Day of the Week'
)

# Display the chart
st.altair_chart(bar_chart, use_container_width=True)
