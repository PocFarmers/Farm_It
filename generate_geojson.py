# We'll generate four bean-shaped GeoJSON polygons using the user's shape function,
# centered on: Kinshasa–Brazzaville, central Amazon, Paris, and an arid-but-cultivable
# North Africa location (Biskra, Algeria oasis region).

import json, math
from pathlib import Path

def make_bean_geojson(lon_c: float, lat_c: float, name: str, filename: str):
    # Basic geodesic approximations (good enough for ~60 km footprint)
    km_per_deg_lat = 111.32
    km_per_deg_lon = km_per_deg_lat * math.cos(math.radians(lat_c))

    # Target overall scale: ~60 km long axis
    R_km = 30.0  # half of long axis

    # Bean (kidney) shape parameters
    e = 0.35        # asymmetry (bulge)
    squash = 0.75   # vertical squash
    x_offset_km = 4.5  # small shift in x to emphasize indentation

    N = 240
    theta = [i * 2*math.pi/N for i in range(N)]

    coords = []
    for t in theta:
        r = R_km * (1 + e * math.sin(t))
        x_km = r * math.cos(t) + x_offset_km
        y_km = squash * r * math.sin(t)
        lon = lon_c + x_km / km_per_deg_lon
        lat = lat_c + y_km / km_per_deg_lat
        coords.append([lon, lat])
    coords.append(coords[0])  # close polygon

    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "name": name,
                "note": "Bean-shaped polygon (~60 km scale). WGS84 (EPSG:4326)."
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }]
    }

    out_path = Path(f"./{filename}")
    out_path.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out_path)

outputs = {}

# 1) Kinshasa–Brazzaville
outputs["kinshasa"] = make_bean_geojson(
    lon_c=15.30, lat_c=-4.30,
    name="FarmIt Congo Bean Polygon (~60 km) – Kinshasa–Brazzaville",
    filename="farmit_kinshasa_brazzaville_bean.geojson"
)

# 2) Central Amazon (remote region west of Manaus)
outputs["amazon"] = make_bean_geojson(
    lon_c=-63.0, lat_c=-4.0,
    name="FarmIt Amazon Bean Polygon (~60 km) – Central Amazon",
    filename="farmit_amazon_central_bean.geojson"
)

# 3) Paris region (Île-de-France)
outputs["paris"] = make_bean_geojson(
    lon_c=2.3522, lat_c=48.8566,
    name="FarmIt Paris Bean Polygon (~60 km) – Île-de-France",
    filename="farmit_paris_bean.geojson"
)

# 4) North Africa arid but cultivable (Biskra, Algeria oasis belt)
outputs["north_africa_arid"] = make_bean_geojson(
    lon_c=5.73, lat_c=34.85,
    name="FarmIt North Africa Arid Bean (~60 km) – Biskra Oasis (Algeria)",
    filename="farmit_north_africa_arid_biskra_bean.geojson"
)

outputs
