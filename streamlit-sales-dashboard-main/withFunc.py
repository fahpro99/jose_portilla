import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import pandas as pd
import altair as alt

# Sample data (replace with your actual data loading code)
# Example: df = pd.read_csv('your_data.csv')
# Ensure that your DataFrame has columns like 'Region', 'District', 'Event Time', 'Latitude', 'Longitude', 'Client'
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

def create_folium_map(data):
    m = folium.Map(location=[23.6850, 90.3563], zoom_start=6)
    heat_data = data[['Latitude', 'Longitude']].values
    HeatMap(heat_data).add_to(m)
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

def display_date_bar_chart(filtered_df):
    date_count = filtered_df['Event Time'].dt.date.value_counts().reset_index()
    date_count.columns = ['Date', 'Count']

    bar_chart = alt.Chart(date_count).mark_bar().encode(
        x=alt.X('Date', title='Date', axis=alt.Axis(format='%Y-%m-%d')),
        y='Count:Q',
        tooltip=['Date', 'Count']
    ).properties(
        title='Incident Count by Date'
    )

    text = bar_chart.mark_text(
        align='center',
        color='blue',
        fontWeight='bold',
        fontSize=15,
        baseline='bottom',
        dy=-5
    ).encode(
        text='Count:Q'
    )

    st.altair_chart(bar_chart + text, use_container_width=True)

# Streamlit app title
st.title("Network outages in Bangladesh")

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
m = create_folium_map(filtered_data)
folium_static(m)

# Display heatmap legend
display_heatmap_legend()

# Add some vertical space before the bar chart
st.markdown("<br>", unsafe_allow_html=True)

# Display interactive bar chart based on date
display_date_bar_chart(filtered_data)
