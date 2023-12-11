import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import pandas as pd
import altair as alt

# Sample data (replace with your actual data loading code)
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

# Streamlit app title
st.title("Network outages in Bangladesh")

# Sidebar for filtering options
selected_region = st.sidebar.selectbox("Select a Region", ['Overall'] + sorted_regions)
if selected_region != 'Overall':
    districts_in_selected_region = list(df[df['Region'] == selected_region]['District'].unique())
    selected_district = st.sidebar.selectbox("Select a District", ['Overall'] + districts_in_selected_region)
else:
    selected_district = st.sidebar.selectbox("Select a District", ['Overall'] + list(district_counts['District']))

selected_clients = st.sidebar.multiselect("Select Clients", list(client_counts['Client']))

# Date range selection
date_range = st.sidebar.date_input("Select Date Range", [df['Event Time'].min(), df['Event Time'].max()])

# Check if both elements of the date_range tuple are not None
if date_range[0] is not None and date_range[1] is not None:
    # Filter DataFrame based on selected region, district, date range, and clients
    filtered_df = df.copy()

    if selected_region != 'Overall':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]

    if selected_district != 'Overall':
        filtered_df = filtered_df[filtered_df['District'] == selected_district]

    filtered_df = filtered_df[(filtered_df['Event Time'] >= pd.to_datetime(date_range[0])) & (filtered_df['Event Time'] <= pd.to_datetime(date_range[1]))]

    if selected_clients:
        filtered_df = filtered_df[filtered_df['Client'].isin(selected_clients)]

    # Display total count based on the applied filters
    total_count = len(filtered_df)
    st.sidebar.markdown(f"Total Count: **{total_count}**")

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

    # Add some vertical space before the bar chart
    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive bar chart based on day_name
    day_count = filtered_df['Event Time'].dt.day_name().value_counts().reset_index()
    day_count.columns = ['Day', 'Count']

    # Create Altair bar chart with total count
    bar_chart = alt.Chart(day_count).mark_bar().encode(
        x='Day:O',
        y='Count:Q',
        tooltip=['Day', 'Count']
    ).properties(
        title='Incident Count by Day of the Week'
    )

    # Add text layer for total count on top of bars
    text = bar_chart.mark_text(
        align='center',
        color='blue',
        fontWeight='bold',  # This line sets the font weight to bold
        fontSize=15,
        baseline='bottom',
        dy=-5  # Adjust the vertical position of the text
    ).encode(
        text='Count:Q'
    )

    # Display the chart with total count
    st.altair_chart(bar_chart + text, use_container_width=True)
else:
    # Display a message when a date is not chosen
    st.sidebar.warning("Please enter a date.")
