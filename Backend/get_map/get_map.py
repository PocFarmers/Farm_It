import os
from get_history_info import get_history_info
import numpy as np
import math
import random
import geopandas as gpd
from shapely.geometry import Polygon, Point
import rasterio
from skimage.transform import resize
import matplotlib.pyplot as plt

def generate_bean_gdf_and_mask(grid_size=(200,200), scale_range=(0.2,0.5),
                               R_km=30.0, e=0.35, squash=0.75, x_offset_km=4.5, N=240):
    ny, nx = grid_size

    # 1️⃣ Haricot original
    theta = np.linspace(0, 2*math.pi, N, endpoint=False)
    r = R_km * (1 + e*np.sin(theta))
    x = r * np.cos(theta) + x_offset_km
    y = squash * r * np.sin(theta)
    coords = list(zip(x,y))
    coords.append(coords[0])
    poly = Polygon(coords)

    # 2️⃣ Normaliser dans [0,1] pour tenir dans la grille
    minx, miny, maxx, maxy = poly.bounds
    poly_norm = Polygon([((px - minx)/(maxx - minx), (py - miny)/(maxy - miny)) for px, py in poly.exterior.coords])

    # 3️⃣ Choisir taille aléatoire et position aléatoire
    scale_factor = random.uniform(*scale_range)
    # Plage pour que le polygone reste dans [0,1]
    max_offset = 1 - scale_factor
    cx = random.uniform(0, max_offset)
    cy = random.uniform(0, max_offset)

    poly_trans = Polygon([((px*scale_factor + cx), (py*scale_factor + cy)) for px, py in poly_norm.exterior.coords])

    # 4️⃣ GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=[poly_trans])

    # 5️⃣ Rasterisation en mask 0/1
    xs = np.linspace(0,1,nx)
    ys = np.linspace(0,1,ny)
    xx, yy = np.meshgrid(xs, ys[::-1])
    mask = np.zeros((ny,nx), dtype=int)

    for i in range(ny):
        for j in range(nx):
            if poly_trans.contains(Point(xx[i,j], yy[i,j])):
                mask[i,j] = 1

    return gdf, mask


def add_tif_layers_to_mask(mask, gdf, tif_files):
    """
    mask: np.array (ny, nx) de l'île
    gdf: GeoDataFrame contenant le polygone
    tif_files: dict { "temperature": "temperature.tif", "humidity": "humidity.tif", ... }
    
    Retourne : np.array (ny, nx, N+1) avec N = nombre de tif_files + 1 pour la couche mask
    """
    ny, nx = mask.shape
    combined_matrix = mask[..., np.newaxis]  # couche 0 = présence de l'île

    for key, file in tif_files.items():
        with rasterio.open(file) as src:
            data = src.read(1)  # lire la première bande
            transform = src.transform

            # On peut créer un masque pour le polygone si besoin
            # mais ici on rééchantillonne simplement la donnée sur la taille de mask
            data_resized = resize(data, (ny, nx), order=1, preserve_range=True)

            # Ne garder les valeurs que sur l'île
            data_resized *= mask

            combined_matrix = np.concatenate([combined_matrix, data_resized[..., np.newaxis]], axis=-1)

    return combined_matrix

def save_combined_matrix_txt(combined_matrix, filename="combined_matrix.txt", layer_names=None):
    """
    Enregistre la matrice combinée dans un fichier txt.
    Chaque ligne = une cellule de la grille
    Colonnes = couche(s)
    """
    ny, nx, n_layers = combined_matrix.shape

    if layer_names is None:
        layer_names = [f"layer_{i}" for i in range(n_layers)]

    # Crée l'en-tête
    header = "i,j," + ",".join(layer_names)

    # Ouvre le fichier
    with open(filename, "w") as f:
        f.write(header + "\n")
        for i in range(ny):
            for j in range(nx):
                values = combined_matrix[i,j,:]
                line = f"{i},{j}," + ",".join(map(str, values))
                f.write(line + "\n")

    print(f"Matrice sauvegardée dans {filename}")
    
def get_map():
    gdf, mask = generate_bean_gdf_and_mask(scale_range=(0.2,0.4))

    history_info=get_history_info(0.943227, 20.000000)
    
    temp = history_info["soil_moisture_0_to_7cm_mean"][0]
    hum = history_info["soil_temperature_28_to_100cm_mean"][0]

    ny, nx = mask.shape
    combined_matrix = np.zeros((ny, nx, 3))

    # Couche 0 : présence de l’île
    combined_matrix[:, :, 0] = mask

    # Couche 1 et 2 : valeurs météo uniquement sur l’île
    combined_matrix[:, :, 1] = mask * temp
    combined_matrix[:, :, 2] = mask * hum
    print(combined_matrix.shape)
    return combined_matrix

get_map()