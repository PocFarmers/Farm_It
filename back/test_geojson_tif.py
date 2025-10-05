#!/usr/bin/env python3
"""Test script to verify GeoJSON and TIF integration"""

import geojson_handler
import tif_handler

def test_geojson_loading():
    """Test loading GeoJSON files"""
    print("=" * 60)
    print("Testing GeoJSON Loading")
    print("=" * 60)

    zones = geojson_handler.get_available_zones()
    print(f"Available zones: {zones}\n")

    for zone in zones:
        try:
            print(f"Loading zone: {zone}")
            geojson_data = geojson_handler.load_geojson(zone)
            zone_info = geojson_handler.get_zone_info(zone)

            print(f"  Zone ID: {zone_info['zone_id']}")
            print(f"  Name: {zone_info['name']}")
            print(f"  TIF prefix: {zone_info['tif_prefix']}")

            # Get bounds
            min_lat, max_lat, min_lng, max_lng = geojson_handler.get_polygon_bounds(geojson_data)
            print(f"  Bounds: lat [{min_lat:.4f}, {max_lat:.4f}], lng [{min_lng:.4f}, {max_lng:.4f}]")

            # Get center
            center_lat, center_lng = geojson_handler.get_center_point(geojson_data)
            print(f"  Center: ({center_lat:.4f}, {center_lng:.4f})")

            # Generate grid
            grid_points = geojson_handler.create_grid_in_polygon(geojson_data, grid_size=0.01)
            print(f"  Grid points generated: {len(grid_points)}")

            print()
        except Exception as e:
            print(f"  ERROR: {e}\n")

def test_tif_extraction():
    """Test TIF data extraction"""
    print("=" * 60)
    print("Testing TIF Data Extraction")
    print("=" * 60)

    # Test coordinates for Paris (temperate zone)
    test_points = {
        'paris_tempere': {'lat': 48.8566, 'lng': 2.3522, 'prefix': 'tempere'},
        'amazon_tropicale': {'lat': -3.1190, 'lng': -60.0217, 'prefix': 'tropicale'},
        'biskra_aride': {'lat': 34.85, 'lng': 5.73, 'prefix': 'aride'},
    }

    for name, point in test_points.items():
        print(f"\nTesting {name}:")
        print(f"  Location: ({point['lat']:.4f}, {point['lng']:.4f})")

        # Test temperature
        temp = tif_handler.get_temperature_at_point(point['prefix'], point['lat'], point['lng'])
        if temp is not None:
            print(f"  Temperature: {temp:.2f}°C")
        else:
            print(f"  Temperature: Not available")

        # Test soil moisture
        moisture = tif_handler.get_soil_moisture_at_point(point['prefix'], point['lat'], point['lng'])
        if moisture is not None:
            print(f"  Soil Moisture: {moisture:.4f}")
        else:
            print(f"  Soil Moisture: Not available")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GEOJSON AND TIF INTEGRATION TEST")
    print("=" * 60 + "\n")

    test_geojson_loading()
    test_tif_extraction()

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
