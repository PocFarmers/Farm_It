import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
import random
import math

# --- Paramètres ---
GRID_SIZE = 100           # Taille de la grille
NB_TERRES_PAR_ILE = 400   # Taille moyenne de l'île (en cellules)
KM_PAR_CELL = 10          # 1 cellule = 10 km
MAX_ISLAND_SIZE_KM = 200  # Taille cible max
REDUCTION_FACTOR = 2.0    # Plus grand = île plus petite

# --- Génération d'un centre d'île aléatoire ---
cx = random.randint(10, GRID_SIZE - 11)
cy = random.randint(10, GRID_SIZE - 11)

# Rayon approximatif en cellules
rayon = int(math.sqrt(NB_TERRES_PAR_ILE / math.pi))

# --- Création des cellules de l'île ---
cellules = []
for dx in range(-rayon, rayon + 1):
    for dy in range(-rayon, rayon + 1):
        if dx**2 + dy**2 <= rayon**2:
            x, y = cx + dx, cy + dy
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                cellules.append(Polygon([(x, y), (x+1, y), (x+1, y+1), (x, y+1)]))

# --- Fusion en un seul polygone ---
polygone_fusionne = unary_union(cellules)

# --- Mise à l'échelle automatique ---
minx, miny, maxx, maxy = polygone_fusionne.bounds
current_size_km = max(maxx - minx, maxy - miny) * KM_PAR_CELL
scale_factor = (current_size_km / MAX_ISLAND_SIZE_KM) * REDUCTION_FACTOR

# Réduction des coordonnées
scaled_polygon = affinity.scale(polygone_fusionne, xfact=1/scale_factor, yfact=1/scale_factor, origin=(0, 0))

# --- Création d'un GeoDataFrame ---
gdf = gpd.GeoDataFrame([{"ile": 1, "geometry": scaled_polygon}], crs="EPSG:3857")

# --- Sauvegarde GeoJSON ---
output_path = "Backend/get_map/ile.geojson"
gdf.to_file(output_path, driver="GeoJSON")

print(f"✅ Fichier GeoJSON généré : {output_path}")
print(f"   Facteur total appliqué : {scale_factor:.2f}")
