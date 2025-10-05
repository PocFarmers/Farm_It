from sqlalchemy.orm import Session
from typing import Optional, List
import random
import models
import schemas
import game_logic

def create_game_state(db: Session) -> models.GameState:
    """Create a new game with initial parcels"""
    game = models.GameState(
        current_stage=0,
        shovels=10,
        water_drops=10,
        score=0
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    # Generate 50 parcels around a random starting point
    # Using France as base (around lat 46.6, lng 1.9)
    base_lat = 46.6 + (random.random() - 0.5) * 2
    base_lng = 1.9 + (random.random() - 0.5) * 2
    tile_size = 0.01  # Approximately 1km

    zones = ['cold', 'arid', 'tropical', 'temperate']

    for i in range(50):
        # Grid-based placement
        row = i // 10
        col = i % 10

        lat = base_lat + (row - 2.5) * tile_size
        lng = base_lng + (col - 2.5) * tile_size

        # Random zone assignment
        zone = random.choice(zones)

        # 70% field, 30% forest
        parcel_type = 'field' if random.random() < 0.7 else 'forest'

        # First 3 parcels are owned
        owned = i < 3

        parcel = models.Parcel(
            game_state_id=game.id,
            lat=lat,
            lng=lng,
            zone_id=zone,
            parcel_type=parcel_type,
            owned=owned
        )
        db.add(parcel)

    db.commit()
    db.refresh(game)
    return game

def get_game_state(db: Session, game_id: int) -> Optional[models.GameState]:
    """Get game state by ID"""
    return db.query(models.GameState).filter(models.GameState.id == game_id).first()

def get_parcels(db: Session, game_id: int) -> List[models.Parcel]:
    """Get all parcels for a game"""
    return db.query(models.Parcel).filter(models.Parcel.game_state_id == game_id).all()

def get_parcel(db: Session, parcel_id: int) -> Optional[models.Parcel]:
    """Get parcel by ID"""
    return db.query(models.Parcel).filter(models.Parcel.id == parcel_id).first()

def execute_action(db: Session, game_id: int, action_req: schemas.ActionRequest) -> dict:
    """Execute a game action"""
    game = get_game_state(db, game_id)
    if not game:
        return {"success": False, "message": "Game not found"}

    parcel = get_parcel(db, action_req.parcel_id)
    if not parcel or parcel.game_state_id != game_id:
        return {"success": False, "message": "Parcel not found"}

    action = action_req.action

    if action == "buy_parcel":
        if parcel.owned:
            return {"success": False, "message": "Parcel already owned"}
        if game.shovels < 2:
            return {"success": False, "message": "Not enough shovels"}

        parcel.owned = True
        game.shovels -= 2
        db.commit()
        return {"success": True, "message": "Parcel purchased"}

    elif action == "plant_crop":
        if not parcel.owned:
            return {"success": False, "message": "Must own parcel to plant"}
        if parcel.parcel_type != "field":
            return {"success": False, "message": "Can only plant on fields"}
        if parcel.crop_type:
            return {"success": False, "message": "Field already has crop"}
        if not action_req.crop_type:
            return {"success": False, "message": "Must specify crop type"}

        crop_type = action_req.crop_type.lower()
        if crop_type not in ['banana', 'potato', 'sorghum']:
            return {"success": False, "message": "Invalid crop type"}

        parcel.crop_type = crop_type
        parcel.crop_stage = 'seed'
        parcel.crop_stage_counter = 0
        db.commit()
        return {"success": True, "message": f"{crop_type.capitalize()} planted"}

    elif action == "irrigate":
        if not parcel.owned:
            return {"success": False, "message": "Must own parcel to irrigate"}
        if game.water_drops < 1:
            return {"success": False, "message": "Not enough water drops"}

        game.water_drops -= 1
        db.commit()
        # Irrigation effect is immediate but temporary
        return {"success": True, "message": "Parcel irrigated"}

    elif action == "fertilize":
        if not parcel.owned:
            return {"success": False, "message": "Must own parcel to fertilize"}
        if game.shovels < 1:
            return {"success": False, "message": "Not enough shovels"}

        game.shovels -= 1
        db.commit()
        return {"success": True, "message": "Parcel fertilized"}

    elif action == "buy_water_reserve":
        if not parcel.owned:
            return {"success": False, "message": "Must own parcel"}
        if parcel.parcel_type != "field":
            return {"success": False, "message": "Can only place on fields"}
        if parcel.crop_type:
            return {"success": False, "message": "Field must be empty"}
        if parcel.has_water_reserve:
            return {"success": False, "message": "Already has water reserve"}
        if game.shovels < 3:
            return {"success": False, "message": "Not enough shovels"}

        parcel.has_water_reserve = True
        game.shovels -= 3
        db.commit()
        return {"success": True, "message": "Water reserve built"}

    elif action == "buy_firebreak":
        if not parcel.owned:
            return {"success": False, "message": "Must own parcel"}
        if parcel.has_firebreak:
            return {"success": False, "message": "Already has firebreak"}
        if game.shovels < 3:
            return {"success": False, "message": "Not enough shovels"}

        parcel.has_firebreak = True
        game.shovels -= 3
        db.commit()
        return {"success": True, "message": "Firebreak built"}

    else:
        return {"success": False, "message": "Unknown action"}

def progress_stage(db: Session, game_id: int) -> dict:
    """Progress game to next stage"""
    game = get_game_state(db, game_id)
    if not game:
        return {"success": False, "message": "Game not found"}

    if game.current_stage >= 50:
        return {"success": False, "message": "Game completed"}

    # Increment stage
    old_score = game.score
    game.current_stage += 1

    # Add resources per stage
    game.shovels += 1
    game.water_drops += 1

    # Process all parcels
    crop_updates = []
    for parcel in game.parcels:
        if parcel.crop_type:
            # Get climate data for this zone
            climate = game_logic.ZONE_DATA.get(parcel.zone_id, {'temp': 20, 'moisture': 0.5})
            result = game_logic.progress_crop_stage(parcel, climate['temp'], climate['moisture'])

            crop_updates.append({
                "parcel_id": parcel.id,
                "result": result
            })

            # Add score for harvests
            if result.get("status") == "harvested":
                game.score += result.get("score", 10)

        # Apply forest fertilizer bonus
        if parcel.parcel_type == 'forest' and parcel.is_forest_preserved and parcel.owned:
            bonus = game_logic.apply_forest_fertilizer(parcel, game.parcels)
            if bonus > 0:
                game.score += bonus

    # Trigger events
    events = game_logic.trigger_events(game.parcels)

    # Add forest preservation bonus
    forest_bonus = game_logic.calculate_score(game)
    game.score += forest_bonus

    score_change = game.score - old_score

    db.commit()
    db.refresh(game)

    return {
        "success": True,
        "new_stage": game.current_stage,
        "events": events,
        "crop_updates": crop_updates,
        "score_change": score_change
    }
