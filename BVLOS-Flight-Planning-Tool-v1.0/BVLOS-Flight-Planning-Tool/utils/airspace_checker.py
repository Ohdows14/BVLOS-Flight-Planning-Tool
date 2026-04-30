"""
Airspace conflict detection utilities
"""

import geopandas as gpd
from shapely.geometry import LineString, Point
from typing import List, Dict, Tuple
import pandas as pd


class AirspaceAnalyzer:
    """Analyze flight paths for airspace conflicts"""
    
    def __init__(self, airspace_data: gpd.GeoDataFrame):
        """
        Initialize analyzer with airspace data
        
        Args:
            airspace_data: GeoDataFrame containing airspace boundaries
        """
        self.airspace = airspace_data
        
    def check_conflicts(self, flight_path: gpd.GeoDataFrame) -> List[Dict]:
        """
        Check if flight path intersects with restricted airspace
        
        Args:
            flight_path: GeoDataFrame containing flight path geometry
            
        Returns:
            List of conflict dictionaries with details
        """
        conflicts = []
        
        # Ensure same CRS
        if self.airspace.crs != flight_path.crs:
            flight_path = flight_path.to_crs(self.airspace.crs)
        
        # Check each segment of flight path
        for idx, path_row in flight_path.iterrows():
            path_geom = path_row.geometry
            
            # Find intersecting airspace zones
            intersects = self.airspace[self.airspace.intersects(path_geom)]
            
            for _, airspace_row in intersects.iterrows():
                conflict = {
                    'waypoint_id': idx,
                    'airspace_name': airspace_row.get('name', 'Unknown'),
                    'airspace_type': airspace_row.get('type', 'Unknown'),
                    'geometry': airspace_row.geometry
                }
                conflicts.append(conflict)
        
        return conflicts
    
    def get_clearances_needed(self, conflicts: List[Dict]) -> pd.DataFrame:
        """
        Generate list of required clearances/authorizations
        
        Args:
            conflicts: List of airspace conflicts
            
        Returns:
            DataFrame with clearance requirements
        """
        if not conflicts:
            return pd.DataFrame()
        
        df = pd.DataFrame(conflicts)
        summary = df.groupby(['airspace_name', 'airspace_type']).size().reset_index(name='intersection_count')
        summary['clearance_required'] = summary['airspace_type'].apply(
            lambda x: 'SFOC Required' if x in ['CYA', 'CYR'] else 'Contact NAV Canada'
        )
        
        return summary
    
    def calculate_buffer_zone(self, flight_path: gpd.GeoDataFrame, buffer_km: float = 1.0) -> gpd.GeoDataFrame:
        """
        Create buffer zone around flight path
        
        Args:
            flight_path: Flight path geometry
            buffer_km: Buffer distance in kilometers
            
        Returns:
            GeoDataFrame with buffered geometry
        """
        # Convert to metric CRS for accurate buffer
        if flight_path.crs.is_geographic:
            projected = flight_path.to_crs('EPSG:3857')  # Web Mercator
            buffered = projected.buffer(buffer_km * 1000)  # Convert km to meters
            result = gpd.GeoDataFrame(geometry=buffered, crs='EPSG:3857')
            result = result.to_crs(flight_path.crs)  # Convert back
        else:
            buffered = flight_path.buffer(buffer_km * 1000)
            result = gpd.GeoDataFrame(geometry=buffered, crs=flight_path.crs)
        
        return result
    
    def check_altitude_compliance(self, flight_path: gpd.GeoDataFrame, airspace_data: gpd.GeoDataFrame) -> List[Dict]:
        """
        Check if flight altitude complies with airspace restrictions
        
        Args:
            flight_path: Flight path with altitude data
            airspace_data: Airspace with floor/ceiling altitudes
            
        Returns:
            List of altitude conflicts
        """
        altitude_conflicts = []
        
        # This assumes flight_path has altitude attribute and airspace has floor/ceiling
        for idx, path_row in flight_path.iterrows():
            if 'altitude' not in path_row:
                continue
                
            flight_alt = path_row['altitude']
            
            # Find overlapping airspace
            overlapping = airspace_data[airspace_data.intersects(path_row.geometry)]
            
            for _, airspace_row in overlapping.iterrows():
                floor_alt = airspace_row.get('floor_altitude', 0)
                ceiling_alt = airspace_row.get('ceiling_altitude', float('inf'))
                
                if floor_alt <= flight_alt <= ceiling_alt:
                    conflict = {
                        'waypoint_id': idx,
                        'flight_altitude': flight_alt,
                        'airspace_floor': floor_alt,
                        'airspace_ceiling': ceiling_alt,
                        'airspace_name': airspace_row.get('name', 'Unknown')
                    }
                    altitude_conflicts.append(conflict)
        
        return altitude_conflicts
