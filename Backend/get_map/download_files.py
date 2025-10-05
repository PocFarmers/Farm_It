import math
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point
import numpy as np

# --- Génération GeoJSON directement dans le script ---

# --- NASA POWER pour un point ---
def get_nasa_power_point(lat, lon, start="20230101", end="20231231"):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,RH2M,PRECTOT",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }
    r = requests.get(url, params=params)
    data = r.json()
    if "properties" not in data or "parameter" not in data["properties"]:
        print("⚠️ Réponse inattendue :", data.get("messages", data))
        return None
    df = pd.DataFrame(data["properties"]["parameter"])
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df

# --- Échantillonnage de points dans le polygone ---
def sample_points_in_polygon(polygon, n_points_x=10, n_points_y=10):
    minx, miny, maxx, maxy = polygon.bounds
    xs = np.linspace(minx, maxx, n_points_x)
    ys = np.linspace(miny, maxy, n_points_y)
    points = []
    for x in xs:
        for y in ys:
            p = Point(x, y)
            if polygon.contains(p):
                points.append(p)
    return points

# --- Récupération des données pour tous les points ---
def get_nasa_power_all_points_geo(gdf, year=2023, n_points_x=10, n_points_y=10):
    polygon = gdf.geometry.iloc[0]
    points = sample_points_in_polygon(polygon, n_points_x, n_points_y)
    print(f"📌 {len(points)} points échantillonnés dans le polygone")

    all_points_data = []

    for i, p in enumerate(points):
        print(f"📡 Point {i+1}/{len(points)} : ({p.y:.4f}, {p.x:.4f})")
        df = get_nasa_power_point(p.y, p.x, start=f"{year}0101", end=f"{year}1231")
        if df is not None:
            df["lat"] = p.y
            df["lon"] = p.x
            all_points_data.append(df)

    if not all_points_data:
        print("❌ Aucun point valide récupéré")
        return None

    df_all = pd.concat(all_points_data)
    df_all.reset_index(inplace=True)
    df_all.rename(columns={"index": "date"}, inplace=True)
    return df_all

def generate_grid_histories_25(lon, lat, n_points=25, spacing_km=2):
    """
    Génère 25 points autour d'un point central (lon, lat), espacés d'environ spacing_km,
    et récupère l'historique pour chacun.
    """
    histories = []

    # Rayon de la Terre en km
    R = 6371.0

    # Générer une grille 5x5
    n_cols = 5
    n_rows = 5
    idx = 0

    for i in range(n_rows):
        for j in range(n_cols):
            if idx >= n_points:
                break

            # Décalage en km
            dx = j * spacing_km
            dy = i * spacing_km

            # Conversion km -> degrés
            dlat = dy / R * (180 / math.pi)
            dlon = dx / R * (180 / math.pi) / math.cos(lat * math.pi / 180)

            lat_i = lat + dlat
            lon_i = lon + dlon

            # Récupérer l'historique
            history_info = get_nasa_power_point(lat_i, lon_i)
            histories.append(history_info)

            idx += 1

    return histories
