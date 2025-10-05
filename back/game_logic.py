import pandas as pd
import os
from typing import List, Dict, Optional
from models import Parcel, GameState

# Import existing event detection logic
import sys
sys.path.append(os.path.dirname(__file__))
from in_game.get_event import get_event

# Load crop phenology data
def load_crop_phenology() -> Dict:
    """Load crop growth requirements from CSV"""
    csv_path = os.path.join(os.path.dirname(__file__), "data", "crop_phenology_thresholds.csv")
    df = pd.read_csv(csv_path)

    crop_data = {}
    for crop_name in df['Crop'].unique():
        crop_df = df[df['Crop'] == crop_name]
        crop_data[crop_name.lower()] = {}

        for _, row in crop_df.iterrows():
            stage = row['Stage'].lower().replace('_', ' ')
            # Map stage names
            if 'germ' in stage:
                stage = 'seed'
            elif 'growth' in stage:
                stage = 'growing'
            elif 'fruit' in stage or 'bulk' in stage or 'fill' in stage:
                stage = 'harvest'
            elif 'senes' in stage:
                continue  # Skip senescence stage

            crop_data[crop_name.lower()][stage] = {
                'temp_min': row['Temperature_Min'],
                'temp_max': row['Temperature_Max'],
                'moisture_min': row['Soil_Moisture_Min'],
                'moisture_max': row['Soil_Moisture_Max']
            }

    return crop_data

# Global crop thresholds
CROP_THRESHOLDS = load_crop_phenology()

# Zone climate data (hardcoded for MVP)
ZONE_DATA = {
    'cold': {'temp': 5, 'moisture': 0.4},
    'arid': {'temp': 35, 'moisture': 0.15},
    'tropical': {'temp': 28, 'moisture': 0.7},
    'temperate': {'temp': 18, 'moisture': 0.5}
}

def check_crop_health(parcel: Parcel, temperature: float, moisture: float) -> bool:
    """Check if crop can survive in current conditions"""
    if not parcel.crop_type or not parcel.crop_stage:
        return True

    crop_type = parcel.crop_type.lower()
    crop_stage = parcel.crop_stage.lower()

    if crop_type not in CROP_THRESHOLDS:
        return True

    if crop_stage not in CROP_THRESHOLDS[crop_type]:
        return True

    thresholds = CROP_THRESHOLDS[crop_type][crop_stage]

    temp_ok = thresholds['temp_min'] <= temperature <= thresholds['temp_max']
    moisture_ok = thresholds['moisture_min'] <= moisture <= thresholds['moisture_max']

    return temp_ok and moisture_ok

def progress_crop_stage(parcel: Parcel, temperature: float, moisture: float) -> Dict:
    """
    Advance crop to next stage or kill if conditions are bad
    Returns dict with status and details
    """
    if not parcel.crop_type or not parcel.crop_stage:
        return {"status": "none"}

    # Check if crop survives
    if not check_crop_health(parcel, temperature, moisture):
        old_crop = parcel.crop_type
        parcel.crop_type = None
        parcel.crop_stage = None
        parcel.crop_stage_counter = 0
        return {
            "status": "died",
            "crop": old_crop,
            "reason": "environmental_conditions"
        }

    # Increment stage counter
    parcel.crop_stage_counter += 1

    # Advance stage every 4 game stages
    if parcel.crop_stage_counter >= 4:
        parcel.crop_stage_counter = 0
        stage_order = ['seed', 'growing', 'harvest']

        try:
            current_index = stage_order.index(parcel.crop_stage)
        except ValueError:
            return {"status": "error", "message": "Invalid crop stage"}

        if current_index == len(stage_order) - 1:
            # Harvest complete
            harvested_crop = parcel.crop_type
            parcel.crop_type = None
            parcel.crop_stage = None
            parcel.crop_stage_counter = 0
            return {
                "status": "harvested",
                "crop": harvested_crop,
                "score": 10
            }
        else:
            # Advance to next stage
            parcel.crop_stage = stage_order[current_index + 1]
            return {
                "status": "advanced",
                "crop": parcel.crop_type,
                "new_stage": parcel.crop_stage
            }

    return {
        "status": "growing",
        "crop": parcel.crop_type,
        "stage": parcel.crop_stage,
        "counter": parcel.crop_stage_counter
    }

def calculate_adjacent_parcels(parcel: Parcel, all_parcels: List[Parcel], threshold: float = 0.001) -> List[Parcel]:
    """Find adjacent parcels (simple distance-based check)"""
    adjacent = []
    for p in all_parcels:
        if p.id == parcel.id:
            continue
        # Simple adjacency check based on distance
        lat_diff = abs(p.lat - parcel.lat)
        lng_diff = abs(p.lng - parcel.lng)

        # Adjacent if close in one dimension and aligned in the other
        if (lat_diff < threshold and lng_diff < threshold * 2) or \
           (lng_diff < threshold and lat_diff < threshold * 2):
            adjacent.append(p)

    return adjacent

def trigger_events(parcels: List[Parcel]) -> List[Dict]:
    """Check for environmental events using existing get_event logic"""
    events = []

    for parcel in parcels:
        zone_climate = ZONE_DATA.get(parcel.zone_id, {'temp': 20, 'moisture': 0.5})
        temp = zone_climate['temp']
        moisture = zone_climate['moisture']

        # Use existing get_event function
        event_type = get_event(temp, moisture)

        if event_type:
            events.append({
                "type": event_type,
                "parcel_id": parcel.id,
                "temperature": temp,
                "moisture": moisture,
                "severity": "high" if event_type == "Fire" else "medium"
            })

    return events

def apply_water_reserve_bonus(parcel: Parcel, all_parcels: List[Parcel]):
    """Water reserves irrigate adjacent fields"""
    if not parcel.has_water_reserve or parcel.parcel_type != 'field':
        return

    adjacent = calculate_adjacent_parcels(parcel, all_parcels)
    # Water reserve effect is passive - tracked in crop health checks
    # In a full implementation, we'd modify moisture values for adjacent parcels

def apply_forest_fertilizer(parcel: Parcel, all_parcels: List[Parcel]) -> int:
    """Forests provide fertilizer to adjacent fields"""
    if parcel.parcel_type != 'forest' or not parcel.is_forest_preserved:
        return 0

    adjacent_fields = [p for p in calculate_adjacent_parcels(parcel, all_parcels)
                       if p.parcel_type == 'field' and p.owned]

    # Each forest gives 1 fertilizer per adjacent field per stage
    return len(adjacent_fields)

def calculate_score(game_state: GameState) -> int:
    """Calculate bonus score from preserved forests"""
    forest_bonus = 0
    for parcel in game_state.parcels:
        if parcel.parcel_type == 'forest' and parcel.is_forest_preserved and parcel.owned:
            forest_bonus += 2  # 2 points per preserved forest per stage

    return forest_bonus
