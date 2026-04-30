"""
BVLOS Flight Planning Tool
Main Streamlit application for flight path planning with airspace and population analysis
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from pathlib import Path
import json
from typing import Optional, List, Dict
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="BVLOS Flight Planning Tool",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
ALBERTA_CENTER = [53.9333, -116.5765]  # Edmonton
DEFAULT_ZOOM = 7
DATA_DIR = Path("data")

class FlightPlanningTool:
    """Main application class for flight planning"""
    
    def __init__(self):
        self.airspace_data = None
        self.parks_data = None
        self.population_data = None
        self.flight_path = None
        
    def load_geojson_data(self, filepath: Path) -> Optional[gpd.GeoDataFrame]:
        """Load GeoJSON data safely"""
        try:
            if filepath.exists():
                gdf = gpd.read_file(filepath)
                st.sidebar.success(f"✓ Loaded {filepath.name}")
                return gdf
            else:
                st.sidebar.warning(f"⚠ File not found: {filepath.name}")
                return None
        except Exception as e:
            st.sidebar.error(f"❌ Error loading {filepath.name}: {str(e)}")
            return None
    
    def create_base_map(self) -> folium.Map:
        """Create the base Folium map centered on Alberta"""
        m = folium.Map(
            location=ALBERTA_CENTER,
            zoom_start=DEFAULT_ZOOM,
            tiles='OpenStreetMap',
            control_scale=True
        )
        return m
    
    def add_airspace_layer(self, m: folium.Map, data: gpd.GeoDataFrame):
        """Add airspace boundaries to map"""
        if data is None:
            return
        
        folium.GeoJson(
            data,
            name="Airspace",
            style_function=lambda x: {
                'fillColor': 'red',
                'color': 'darkred',
                'weight': 2,
                'fillOpacity': 0.2
            },
            tooltip=folium.GeoJsonTooltip(fields=['name'] if 'name' in data.columns else [])
        ).add_to(m)
    
    def add_parks_layer(self, m: folium.Map, data: gpd.GeoDataFrame):
        """Add parks boundaries to map"""
        if data is None:
            return
        
        folium.GeoJson(
            data,
            name="Parks",
            style_function=lambda x: {
                'fillColor': 'green',
                'color': 'darkgreen',
                'weight': 1,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(fields=['name'] if 'name' in data.columns else [])
        ).add_to(m)
    
    def add_population_layer(self, m: folium.Map, data: gpd.GeoDataFrame):
        """Add population density to map"""
        if data is None:
            return
        
        folium.GeoJson(
            data,
            name="Population Density",
            style_function=lambda x: {
                'fillColor': 'blue',
                'color': 'navy',
                'weight': 1,
                'fillOpacity': 0.2
            }
        ).add_to(m)
    
    def parse_kml(self, uploaded_file) -> Optional[gpd.GeoDataFrame]:
        """Parse uploaded KML/KMZ file"""
        try:
            # Save uploaded file temporarily
            temp_path = Path(f"/tmp/{uploaded_file.name}")
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Read with GeoPandas (supports KML via fiona)
            gdf = gpd.read_file(temp_path)
            st.success(f"✓ Loaded flight plan: {uploaded_file.name}")
            return gdf
        except Exception as e:
            st.error(f"❌ Error parsing KML: {str(e)}")
            return None
    
    def add_flight_path(self, m: folium.Map, data: gpd.GeoDataFrame):
        """Add flight path to map"""
        if data is None:
            return
        
        folium.GeoJson(
            data,
            name="Flight Path",
            style_function=lambda x: {
                'color': 'yellow',
                'weight': 4,
                'opacity': 0.8
            },
            tooltip=folium.GeoJsonTooltip(fields=list(data.columns)[:5])
        ).add_to(m)
        
        # Add markers for waypoints
        for idx, row in data.iterrows():
            if row.geometry.geom_type == 'Point':
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=f"Waypoint {idx}",
                    icon=folium.Icon(color='orange', icon='plane', prefix='fa')
                ).add_to(m)

def main():
    """Main application entry point"""
    
    # Header
    st.title("✈️ BVLOS Flight Planning Tool")
    st.markdown("**Plan and analyze Beyond Visual Line of Sight (BVLOS) drone operations**")
    st.markdown("---")
    
    # Initialize tool
    tool = FlightPlanningTool()
    
    # Sidebar - Controls
    st.sidebar.header("🎛️ Controls")
    
    # Layer toggles
    st.sidebar.subheader("Map Layers")
    show_airspace = st.sidebar.checkbox("Show Airspace", value=True)
    show_parks = st.sidebar.checkbox("Show Parks", value=False)
    show_population = st.sidebar.checkbox("Show Population Density", value=False)
    
    st.sidebar.markdown("---")
    
    # File upload
    st.sidebar.subheader("📁 Upload Flight Plan")
    uploaded_kml = st.sidebar.file_uploader(
        "Upload KML/KMZ file",
        type=['kml', 'kmz'],
        help="Upload your mission plan from QGroundControl or Mission Planner"
    )
    
    st.sidebar.markdown("---")
    
    # Data loading status
    st.sidebar.subheader("📊 Data Status")
    
    # Load data layers
    airspace_path = DATA_DIR / "airspace" / "canadian_airspace.geojson"
    parks_path = DATA_DIR / "parks" / "alberta_parks.geojson"
    
    if show_airspace:
        tool.airspace_data = tool.load_geojson_data(airspace_path)
    
    if show_parks:
        tool.parks_data = tool.load_geojson_data(parks_path)
    
    # Parse uploaded flight plan
    if uploaded_kml:
        tool.flight_path = tool.parse_kml(uploaded_kml)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🗺️ Flight Planning Map")
        
        # Create map
        m = tool.create_base_map()
        
        # Add layers based on toggles
        if show_airspace and tool.airspace_data is not None:
            tool.add_airspace_layer(m, tool.airspace_data)
        
        if show_parks and tool.parks_data is not None:
            tool.add_parks_layer(m, tool.parks_data)
        
        if show_population and tool.population_data is not None:
            tool.add_population_layer(m, tool.population_data)
        
        # Add flight path if uploaded
        if tool.flight_path is not None:
            tool.add_flight_path(m, tool.flight_path)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Display map
        st_folium(m, width=1200, height=600)
    
    with col2:
        st.subheader("📋 Analysis")
        
        if tool.flight_path is not None:
            st.success("✓ Flight plan loaded")
            
            # Basic stats
            st.metric("Waypoints", len(tool.flight_path))
            
            # Airspace analysis placeholder
            st.markdown("### Airspace Check")
            if tool.airspace_data is not None:
                st.info("🔍 Analyzing airspace conflicts...")
                # TODO: Implement spatial intersection check
                st.warning("⚠️ Analysis in progress")
            else:
                st.error("❌ Airspace data not loaded")
            
            # Population analysis placeholder
            st.markdown("### Population Analysis")
            if tool.population_data is not None:
                st.info("🔍 Analyzing population exposure...")
            else:
                st.warning("⚠️ Population data not loaded")
        else:
            st.info("👆 Upload a KML file to begin analysis")
            
            st.markdown("### Instructions")
            st.markdown("""
            1. Toggle map layers in the sidebar
            2. Upload your flight plan (KML/KMZ)
            3. Review airspace conflicts
            4. Analyze population exposure
            5. Generate SFOC documentation
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("**BVLOS Flight Planning Tool** | Built for Canadian RPAS operators")

if __name__ == "__main__":
    main()
