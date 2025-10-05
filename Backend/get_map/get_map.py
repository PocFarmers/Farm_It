import numpy as np
import math
import random
import geopandas as gpd
from shapely.geometry import Polygon, Point
import rasterio
from skimage.transform import resize

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


def get_map():
    gdf, mask = generate_bean_gdf_and_mask(scale_range=(0.2,0.4))

    tif_files = {
        "temperature": "~/Farm_It/data/temperature/froide_MOD11A2.061_LST_Day_1km_doy2023361000000_aid0001.tif",
        "humidity": "~/Farm_It/data/humidite/tropicale_SPL3SMP_E.006_Soil_Moisture_Retrieval_Data_PM_soil_moisture_pm_doy2024132000000_aid0001.tif"
    }

    combined_matrix = add_tif_layers_to_mask(mask, gdf, tif_files)

    return combined_matrix
