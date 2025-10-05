import numpy as np
import math
import random
import geopandas as gpd
from shapely.geometry import Polygon, Point

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

gdf, mask = generate_bean_gdf_and_mask(scale_range=(0.2,0.4))

# Sauvegarder le GeoDataFrame dans un TXT
gdf.to_csv("bean_gdf.txt", index=False)

gdf.to_csv("bean.txt", index=False)

np.savetxt("k.txt", mask, fmt="%d")
