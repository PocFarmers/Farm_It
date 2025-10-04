import numpy as np
import random
import math
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
import json

# Création de la carte
carte = np.zeros((100, 100), dtype=int)

def generer_ile(nb_terres=400, num_ile=1):
    while True:
        cx = random.randint(10, 89)
        cy = random.randint(10, 89)
        if np.all(carte[max(0, cx-5):cx+6, max(0, cy-5):cy+6] == 0):
            break

    rayon = int(math.sqrt(nb_terres / math.pi))
    
    x_grid, y_grid = np.ogrid[-rayon:rayon+1, -rayon:rayon+1]
    mask = x_grid**2 + y_grid**2 <= rayon**2

    x_start = max(0, cx - rayon)
    y_start = max(0, cy - rayon)
    x_end = min(100, cx + rayon + 1)
    y_end = min(100, cy + rayon + 1)

    carte_slice = carte[x_start:x_end, y_start:y_end]
    mask_slice = mask[:x_end-x_start, :y_end-y_start]

    carte_slice[mask_slice] = num_ile

# Génération des îles
for i in range(1, 5):
    generer_ile(nb_terres=400, num_ile=i)

# Fonction pour convertir numpy.int64 en int
def convert_coords(geom):
    if geom['type'] == 'Polygon':
        geom['coordinates'] = [
            [(int(x), int(y)) for x, y in ring] for ring in geom['coordinates']
        ]
    return geom

# Création de la liste de polygones pour GeoJSON
liste_polygones = []

for ile_id in np.unique(carte):
    if ile_id == 0:
        continue
    cellules = []
    for x in range(carte.shape[0]):
        for y in range(carte.shape[1]):
            if carte[x, y] == ile_id:
                cellules.append(Polygon([(x, y), (x+1, y), (x+1, y+1), (x, y+1)]))
    polygone_fusionne = unary_union(cellules)
    geom_json = convert_coords(mapping(polygone_fusionne))
    liste_polygones.append({
        'type': 'Feature',
        'properties': {'ile': int(ile_id)},
        'geometry': geom_json
    })

# Création du GeoJSON
geojson = {
    'type': 'FeatureCollection',
    'features': liste_polygones
}

# Sauvegarde
with open("Backend/get_map/iles.geojson", "w") as f:
    json.dump(geojson, f)
