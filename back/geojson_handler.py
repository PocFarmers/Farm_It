import json
import os
from typing import Dict, List, Tuple
from shapely.geometry import shape, Point
from shapely.ops import unary_union
import numpy as np

# Mapping zone names to their GeoJSON files and characteristics
# Note: GeoJSON files are for visualization, but parcels are generated from TIF bounds
ZONE_CONFIGS = {
    'paris': {
        'geojson': 'farmit_paris_bean.geojson',
        'zone_id': 'temperate',
        'name': 'Paris (Temperate)',
        'tif_prefix': 'tempere',
        'use_tif_bounds': True  # Use TIF file bounds instead of GeoJSON
    },
    'amazon': {
        'geojson': 'farmit_amazon_central_bean.geojson',
        'zone_id': 'tropical',
        'name': 'Amazon Central (Tropical)',
        'tif_prefix': 'tropicale',
        'use_tif_bounds': True
    },
    'biskra': {
        'geojson': 'farmit_north_africa_arid_biskra_bean.geojson',
        'zone_id': 'arid',
        'name': 'North Africa Biskra (Arid)',
        'tif_prefix': 'aride',
        'use_tif_bounds': True
    },
    'kinshasa': {
        'geojson': 'farmit_kinshasa_brazzaville_bean.geojson',
        'zone_id': 'tropical',
        'name': 'Kinshasa-Brazzaville (Tropical)',
        'tif_prefix': 'tropicale',
        'use_tif_bounds': True
    }
}

def load_geojson(zone_key: str) -> Dict:
    """Load GeoJSON file for a given zone"""
    if zone_key not in ZONE_CONFIGS:
        raise ValueError(f"Unknown zone: {zone_key}")

    config = ZONE_CONFIGS[zone_key]
    geojson_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "masks",
        config['geojson']
    )

    with open(geojson_path, 'r') as f:
        return json.load(f)

def get_polygon_bounds(geojson_data: Dict) -> Tuple[float, float, float, float]:
    """Extract bounding box from GeoJSON (min_lat, max_lat, min_lng, max_lng)"""
    if not geojson_data or 'features' not in geojson_data:
        raise ValueError("Invalid GeoJSON data")

    geometry = geojson_data['features'][0]['geometry']
    polygon = shape(geometry)
    bounds = polygon.bounds  # (minx, miny, maxx, maxy)

    return bounds[1], bounds[3], bounds[0], bounds[2]  # (min_lat, max_lat, min_lng, max_lng)

def create_grid_in_polygon(geojson_data: Dict, grid_size: float = 0.01) -> List[Dict]:
    """
    Create a grid of points within the GeoJSON polygon
    Returns list of {lat, lng} coordinates
    """
    geometry = geojson_data['features'][0]['geometry']
    polygon = shape(geometry)

    min_lat, max_lat, min_lng, max_lng = get_polygon_bounds(geojson_data)

    grid_points = []

    # Generate grid points
    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            point = Point(lng, lat)
            if polygon.contains(point):
                grid_points.append({
                    'lat': lat,
                    'lng': lng
                })
            lng += grid_size
        lat += grid_size

    return grid_points

def get_center_point(geojson_data: Dict) -> Tuple[float, float]:
    """Get the center point of the polygon (lat, lng)"""
    geometry = geojson_data['features'][0]['geometry']
    polygon = shape(geometry)
    centroid = polygon.centroid

    return centroid.y, centroid.x  # (lat, lng)

def get_zone_info(zone_key: str) -> Dict:
    """Get zone configuration information"""
    if zone_key not in ZONE_CONFIGS:
        raise ValueError(f"Unknown zone: {zone_key}")

    return ZONE_CONFIGS[zone_key]

def get_available_zones() -> List[str]:
    """Get list of available zone keys"""
    return list(ZONE_CONFIGS.keys())

def create_grid_from_bounds(min_lat: float, max_lat: float, min_lng: float, max_lng: float, grid_size: float = 0.01) -> List[Dict]:
    """
    Create a simple rectangular grid within bounds
    Returns list of {lat, lng} coordinates
    """
    grid_points = []

    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            grid_points.append({
                'lat': lat,
                'lng': lng
            })
            lng += grid_size
        lat += grid_size

    return grid_points
