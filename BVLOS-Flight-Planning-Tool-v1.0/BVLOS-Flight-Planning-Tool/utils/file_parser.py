"""
Flight plan file parsing utilities (KML, KMZ, Mission Planner formats)
"""

import geopandas as gpd
from pathlib import Path
from typing import Optional, List, Tuple
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import tempfile
import json


class FlightPlanParser:
    """Parse various flight plan file formats"""
    
    @staticmethod
    def parse_kml(filepath: Path) -> Optional[gpd.GeoDataFrame]:
        """
        Parse KML file to GeoDataFrame
        
        Args:
            filepath: Path to KML file
            
        Returns:
            GeoDataFrame with flight path geometry
        """
        try:
            gdf = gpd.read_file(filepath, driver='KML')
            return gdf
        except Exception as e:
            print(f"Error parsing KML: {e}")
            return None
    
    @staticmethod
    def parse_kmz(filepath: Path) -> Optional[gpd.GeoDataFrame]:
        """
        Parse KMZ (zipped KML) file
        
        Args:
            filepath: Path to KMZ file
            
        Returns:
            GeoDataFrame with flight path geometry
        """
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                
                # Find KML file in extracted contents
                kml_files = list(Path(tmpdir).glob('*.kml'))
                if not kml_files:
                    kml_files = list(Path(tmpdir).glob('**/*.kml'))
                
                if kml_files:
                    return FlightPlanParser.parse_kml(kml_files[0])
            
            return None
        except Exception as e:
            print(f"Error parsing KMZ: {e}")
            return None
    
    @staticmethod
    def parse_waypoint_file(filepath: Path) -> Optional[gpd.GeoDataFrame]:
        """
        Parse QGroundControl or Mission Planner waypoint file
        
        Args:
            filepath: Path to waypoint file
            
        Returns:
            GeoDataFrame with waypoints
        """
        try:
            # QGC format is JSON-based
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            waypoints = []
            if 'mission' in data:
                for item in data['mission'].get('items', []):
                    if 'coordinate' in item:
                        coord = item['coordinate']
                        waypoints.append({
                            'latitude': coord[0],
                            'longitude': coord[1],
                            'altitude': coord[2] if len(coord) > 2 else 0,
                            'command': item.get('command', 'WAYPOINT')
                        })
            
            if not waypoints:
                return None
            
            # Convert to GeoDataFrame
            from shapely.geometry import Point
            geometry = [Point(wp['longitude'], wp['latitude']) for wp in waypoints]
            gdf = gpd.GeoDataFrame(waypoints, geometry=geometry, crs='EPSG:4326')
            
            return gdf
            
        except Exception as e:
            print(f"Error parsing waypoint file: {e}")
            return None
    
    @staticmethod
    def extract_waypoints(gdf: gpd.GeoDataFrame) -> List[Tuple[float, float, float]]:
        """
        Extract waypoint coordinates from GeoDataFrame
        
        Args:
            gdf: GeoDataFrame with geometry
            
        Returns:
            List of (lat, lon, alt) tuples
        """
        waypoints = []
        
        for idx, row in gdf.iterrows():
            geom = row.geometry
            
            if geom.geom_type == 'Point':
                lat = geom.y
                lon = geom.x
                alt = row.get('altitude', 0)
                waypoints.append((lat, lon, alt))
            
            elif geom.geom_type == 'LineString':
                for coord in geom.coords:
                    lon, lat = coord[0], coord[1]
                    alt = coord[2] if len(coord) > 2 else 0
                    waypoints.append((lat, lon, alt))
        
        return waypoints
    
    @staticmethod
    def calculate_path_length(gdf: gpd.GeoDataFrame) -> float:
        """
        Calculate total path length in kilometers
        
        Args:
            gdf: GeoDataFrame with flight path
            
        Returns:
            Total length in kilometers
        """
        # Convert to metric projection
        projected = gdf.to_crs('EPSG:3857')
        total_length = projected.geometry.length.sum()
        
        # Convert meters to kilometers
        return total_length / 1000.0
    
    @staticmethod
    def get_bounding_box(gdf: gpd.GeoDataFrame) -> Tuple[float, float, float, float]:
        """
        Get bounding box of flight path
        
        Args:
            gdf: GeoDataFrame with geometry
            
        Returns:
            Tuple of (min_lon, min_lat, max_lon, max_lat)
        """
        bounds = gdf.total_bounds
        return tuple(bounds)
