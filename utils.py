import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import streamlit as st

@st.cache_data
def get_center_coordinates():
    """Get coordinates for S DuSable Lake Shore Drive and E 87th Street, Chicago"""
    return (41.736679, -87.554874)  # Pre-calculated coordinates for the specified location

@st.cache_data
def process_data(df):
    """Process the hospital data"""
    try:
        # Basic data cleaning
        required_columns = ['Hospital Name', 'Total Beds on 10/1/23', 'Latitude', 'Longitude']
        
        # Check for required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
            return None
        
        # Clean and convert data types
        df['Total Beds on 10/1/23'] = pd.to_numeric(df['Total Beds on 10/1/23'], 
                                                   errors='coerce').fillna(0)
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Remove rows with invalid coordinates
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        return df
    
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None

def load_data(uploaded_file):
    """Load data from uploaded file"""
    try:
        if uploaded_file is None:
            return None
        
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        return process_data(df)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

@st.cache_data
def calculate_distances(df, center_coords):
    """Calculate distances from center point to each hospital"""
    def calculate_distance(row):
        hospital_coords = (row['Latitude'], row['Longitude'])
        return geodesic(center_coords, hospital_coords).miles
    
    df['distance_miles'] = df.apply(calculate_distance, axis=1)
    return df
