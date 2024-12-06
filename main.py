import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from utils import load_data, calculate_distances, get_center_coordinates

# Page configuration
st.set_page_config(
    page_title="Illinois Hospitals Map",
    page_icon="🏥",
    layout="wide"
)

# Title and description
st.title("Illinois Hospitals Interactive Map")
st.markdown("Displaying hospitals within 5 miles of S DuSable Lake Shore Drive and E 87th Street, Chicago")

# Center coordinates (S DuSable Lake Shore Drive and E 87th Street, Chicago, IL)
CENTER_COORDS = get_center_coordinates()
# Add radius slider
RADIUS_MILES = st.slider(
    "Select radius (miles)",
    min_value=1,
    max_value=20,
    value=5,
    step=1,
    help="Adjust the radius to show hospitals within the selected distance"
)

# File uploader
uploaded_file = st.file_uploader("Upload hospital data file (XLSX or CSV)", 
                               type=['xlsx', 'csv'])

# Load and process data
try:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Calculate distances from center point
        df = calculate_distances(df, CENTER_COORDS)
        
        # Filter hospitals within radius
        df_filtered = df[df['distance_miles'] <= RADIUS_MILES].copy()
        
        # Create map centered at the specified location
        m = folium.Map(
            location=CENTER_COORDS,
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add circle showing 5-mile radius
        folium.Circle(
            radius=RADIUS_MILES * 1609.34,  # Convert miles to meters
            location=CENTER_COORDS,
            color='red',
            fill=True,
            opacity=0.2
        ).add_to(m)
        
        # Add markers for each hospital
        for idx, row in df_filtered.iterrows():
            html = f"""
                <div style="font-family: Arial; min-width: 180px;">
                    <h4 style="margin-bottom: 10px;">{row['Hospital Name']}</h4>
                    <p><strong>Total Beds:</strong> {row['Total Beds on 10/1/23']}</p>
                </div>
            """
            
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(html, max_width=300),
                tooltip=row['Hospital Name'],
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Display the map
        st_data = folium_static(m, width=1000, height=600)
        
        # Display statistics
        st.subheader("Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Hospitals Shown", len(df_filtered))
        with col2:
            st.metric("Total Beds Available", df_filtered['Total Beds on 10/1/23'].sum())
        with col3:
            st.metric("Average Beds per Hospital", 
                     round(df_filtered['Total Beds on 10/1/23'].mean(), 1))
        
        # Display data table
        st.subheader("Hospital Details")
        st.dataframe(
            df_filtered[['Hospital Name', 'Total Beds on 10/1/23', 'distance_miles']]
            .sort_values('distance_miles')
            .rename(columns={'distance_miles': 'Distance (miles)'})
            .reset_index(drop=True)
        )
        
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please ensure your data file is in the correct format (XLSX or CSV) and contains the required columns.")
