import os
import glob
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from PIL import Image
import io
from fastapi.responses import StreamingResponse

# Map zone IDs to TIF directories
ZONE_TIF_DIRS = {
    "cold": "froide_siberie",
    "arid": "aride_sahara",
    "tropical": "tropicale_congo",
    "temperate": "temperee_allemagne"
}

def get_tif_files_for_zone(zone_id: str):
    """Get all TIF files for a given zone"""
    zone_dir = ZONE_TIF_DIRS.get(zone_id)
    if not zone_dir:
        return []

    # Path to TIF files (LST - Land Surface Temperature)
    downloads_path = os.path.join(os.path.dirname(__file__), "..", "downloads")
    tif_pattern = os.path.join(downloads_path, zone_dir, "LST", "**", "*LST_Day_1km*.tif")

    tif_files = glob.glob(tif_pattern, recursive=True)
    tif_files.sort()  # Sort by filename (which includes date)

    return tif_files

def get_tif_for_stage(zone_id: str, stage: int):
    """Get the TIF file corresponding to a game stage (1-50)"""
    tif_files = get_tif_files_for_zone(zone_id)

    if not tif_files:
        return None

    # Map stage (1-50) to TIF index
    # Each stage = 8 days, 50 stages = 400 days ≈ 1 year
    # TIF files are every 8 days (MOD11A2 is 8-day composite)
    tif_index = min(stage - 1, len(tif_files) - 1)

    return tif_files[tif_index] if tif_index < len(tif_files) else tif_files[-1]

def tif_to_png_bytes(tif_path: str, colormap='hot'):
    """Convert TIF to PNG bytes with color mapping"""
    try:
        with rasterio.open(tif_path) as src:
            # Read the first band (LST data)
            data = src.read(1)

            # Get valid data (non-nodata values)
            if src.nodata is not None:
                valid_mask = data != src.nodata
                data = np.where(valid_mask, data, np.nan)

            # Scale to 0-255 for visualization
            # LST values are in Kelvin * 50 (MODIS LST format)
            # Convert to Celsius: (value * 0.02) - 273.15
            data_celsius = (data * 0.02) - 273.15

            # Normalize to 0-255 for color mapping
            valid_data = data_celsius[~np.isnan(data_celsius)]
            if len(valid_data) == 0:
                # Return empty image if no valid data
                img = Image.new('RGBA', (src.width, src.height), (0, 0, 0, 0))
            else:
                vmin, vmax = np.percentile(valid_data, [2, 98])  # Use 2nd-98th percentile
                data_normalized = np.clip((data_celsius - vmin) / (vmax - vmin), 0, 1)
                data_normalized = (data_normalized * 255).astype(np.uint8)

                # Apply colormap (hot = red/yellow for temperature)
                if colormap == 'hot':
                    # Red-yellow-white colormap
                    from matplotlib import cm
                    cmap = cm.get_cmap('hot')
                    colored = cmap(data_normalized / 255.0)
                    colored = (colored[:, :, :3] * 255).astype(np.uint8)

                    # Add alpha channel (transparency for nodata)
                    alpha = np.where(np.isnan(data_celsius), 0, 180).astype(np.uint8)
                    rgba = np.dstack([colored, alpha])

                    img = Image.fromarray(rgba, mode='RGBA')
                else:
                    img = Image.fromarray(data_normalized, mode='L')

            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            return img_bytes

    except Exception as e:
        print(f"Error processing TIF {tif_path}: {e}")
        return None

def get_tif_bounds(tif_path: str):
    """Get geographic bounds of TIF file"""
    try:
        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            return {
                "south": bounds.bottom,
                "west": bounds.left,
                "north": bounds.top,
                "east": bounds.right
            }
    except Exception as e:
        print(f"Error getting bounds for {tif_path}: {e}")
        return None

def get_tif_bounds_for_zone(zone_prefix: str):
    """Get bounds from temperature TIF for a zone"""
    tif_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "temperature",
        f"{zone_prefix}_MOD11A2.061_LST_Day_1km_doy2023361000000_aid0001.tif"
    )

    if not os.path.exists(tif_path):
        return None

    return get_tif_bounds(tif_path)

def extract_tif_value_at_point(tif_path: str, lat: float, lng: float):
    """Extract TIF value at a specific geographic point (lat, lng)"""
    try:
        with rasterio.open(tif_path) as src:
            # Convert lat/lng to pixel coordinates
            row, col = src.index(lng, lat)

            # Check if point is within bounds
            if row < 0 or row >= src.height or col < 0 or col >= src.width:
                return None

            # Read value at this pixel
            data = src.read(1)
            value = data[row, col]

            # Check for nodata
            if src.nodata is not None and value == src.nodata:
                return None

            return float(value)
    except Exception as e:
        print(f"Error extracting value from {tif_path} at ({lat}, {lng}): {e}")
        return None

def get_temperature_at_point(zone_prefix: str, lat: float, lng: float) -> float:
    """
    Get temperature in Celsius at a specific point for a zone
    zone_prefix: 'aride', 'froide', 'tempere', 'tropicale'
    """
    tif_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "temperature",
        f"{zone_prefix}_MOD11A2.061_LST_Day_1km_doy2023361000000_aid0001.tif"
    )

    if not os.path.exists(tif_path):
        print(f"Temperature TIF not found: {tif_path}")
        return None

    raw_value = extract_tif_value_at_point(tif_path, lat, lng)
    if raw_value is None:
        return None

    # Convert MODIS LST to Celsius: (value * 0.02) - 273.15
    temp_celsius = (raw_value * 0.02) - 273.15
    return temp_celsius

def get_soil_moisture_at_point(zone_prefix: str, lat: float, lng: float) -> float:
    """
    Get soil moisture (0-1 scale) at a specific point for a zone
    zone_prefix: 'aride', 'froide', 'tempere', 'tropicale'
    """
    # Handle the special case for temperate zone file name
    filename = f"{zone_prefix}_SPL3SMP_E.006_Soil_Moisture_Retrieval_Data_PM_soil_moisture_pm_doy2024132000000_aid0001.tif"
    if zone_prefix == 'tempere':
        filename = "tempere_SPL3SMP_E.006_Soil_Moisture_Retrieval_Data_PM_soil_moisture_pm_doy2024132000000_aid0001 copy.tif"

    tif_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "humidite",
        filename
    )

    if not os.path.exists(tif_path):
        print(f"Soil moisture TIF not found: {tif_path}")
        return None

    raw_value = extract_tif_value_at_point(tif_path, lat, lng)
    if raw_value is None:
        return None

    # Soil moisture is typically already in 0-1 range or needs specific scaling
    # Adjust this based on actual data format
    return raw_value / 100.0 if raw_value > 1 else raw_value
