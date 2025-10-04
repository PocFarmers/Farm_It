import numpy as np
import random
import math
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
import json

# --- Paramètres ---
GRID_SIZE = 100          # Taille de la grille (100x100)
NB_TERRES_PAR_ILE = 400  # Taille moyenne d'une île (en cellules)
MAX_ISLAND_SIZE_KM = 200 # Taille max cible en km
KM_PAR_CELL = 10         # 1 cellule = 10 km
REDUCTION_FACTOR = 5.0   # Réduction supplémentaire (plus grand = plus petit)

# --- Initialisation de la carte ---
carte = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

# --- Fonction pour générer une seule île ---
def generer_ile(nb_terres=400, num_ile=1):
    while True:
        cx = random.randint(10, GRID_SIZE - 11)
        cy = random.randint(10, GRID_SIZE - 11)
        if np.all(carte[max(0, cx-5):cx+6, max(0, cy-5):cy+6] == 0):
            break

    rayon = int(math.sqrt(nb_terres / math.pi))
    
    x_grid, y_grid = np.ogrid[-rayon:rayon+1, -rayon:rayon+1]
    mask = x_grid**2 + y_grid**2 <= rayon**2

    x_start = max(0, cx - rayon)
    y_start = max(0, cy - rayon)
    x_end = min(GRID_SIZE, cx + rayon + 1)
    y_end = min(GRID_SIZE, cy + rayon + 1)

    carte_slice = carte[x_start:x_end, y_start:y_end]
    mask_slice = mask[:x_end-x_start, :y_end-y_start]

    carte_slice[mask_slice] = num_ile

# --- Générer une seule île ---
generer_ile(nb_terres=NB_TERRES_PAR_ILE, num_ile=1)

# --- Conversion des coordonnées ---
def convert_coords(geom):
    if geom['type'] == 'Polygon':
        geom['coordinates'] = [
            [(float(x), float(y)) for x, y in ring]
            for ring in geom['coordinates']
        ]
    return geom

# --- Mesure de la taille ---
def get_bbox_size(geom):
    xs, ys = zip(*geom['coordinates'][0])
    return max(xs) - min(xs), max(ys) - min(ys)

# --- Mise à l’échelle ---
def scale_geometry(geom, factor):
    geom['coordinates'] = [
        [(x / factor, y / factor) for x, y in ring]
        for ring in geom['coordinates']
    ]
    return geom

# --- Construction du polygone fusionné ---
cellules = []
for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        if carte[x, y] == 1:
            cellules.append(Polygon([(x, y), (x+1, y), (x+1, y+1), (x, y+1)]))

polygone_fusionne = unary_union(cellules)
geom_json = convert_coords(mapping(polygone_fusionne))

# --- Calcul du facteur d’échelle ---
w, h = get_bbox_size(geom_json)
max_size = max(w, h)
current_size_km = max_size * KM_PAR_CELL
SCALE_FACTOR = (current_size_km / MAX_ISLAND_SIZE_KM) * REDUCTION_FACTOR

# --- Réduction ---
geom_json = scale_geometry(geom_json, SCALE_FACTOR)

# --- Création du GeoJSON ---
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"ile": 1},
            "geometry": geom_json
        }
    ]
}

# --- Sauvegarde ---
with open("Backend/get_map/iles.geojson", "w") as f:
    json.dump(geojson, f, indent=2)

print("✅ Fichier 'iles.geojson' généré avec 1 seule île.")
print(f"   Taille max estimée : {MAX_ISLAND_SIZE_KM} km")
print(f"   Facteur total appliqué : {SCALE_FACTOR:.2f}")
