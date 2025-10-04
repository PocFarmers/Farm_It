# Generate a bean-shaped (kidney-like) GeoJSON polygon near the Congo River,
# keeping overall scale similar to ~60 km across, compatible with NASA AppEEARS (WGS84).
import json, math
from pathlib import Path


def get_geojson(lon_c : float, lat_c : float):
    # Basic geodesic approximations (sufficient for small shapes)
    km_per_deg_lat = 111.32
    km_per_deg_lon = km_per_deg_lat * math.cos(math.radians(lat_c))

    # Target overall scale: ~60 km long axis
    R_km = 30.0  # base radius scale in km (~half of the long axis)

    # Bean (kidney) shape in polar coords, then convert to local km, then to degrees
    # r(θ) = R * (1 + e*sinθ) with a vertical squash and slight x-offset to accentuate the "bean"
    e = 0.35        # asymmetry (controls the bulge)
    squash = 0.75   # vertical squash to get a bean/kidney profile
    x_offset_km = 4.5  # small shift in x to emphasize the indentation (~4.5 km)

    N = 240
    theta = [i * 2*math.pi/(N) for i in range(N)]

    coords = []
    for t in theta:
        r = R_km * (1 + e*math.sin(t))
        x_km = r * math.cos(t) + x_offset_km
        y_km = squash * r * math.sin(t)
        # convert local km -> degrees around (lat_c, lon_c)
        lon = lon_c + x_km / km_per_deg_lon
        lat = lat_c + y_km / km_per_deg_lat
        coords.append([lon, lat])

    # Close polygon
    coords.append(coords[0])

    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "name": "FarmIt Congo Bean Polygon (~60 km scale)",
                "note": "Bean-shaped polygon near the Congo River. WGS84 (EPSG:4326)."
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }]
    }

    return geojson

