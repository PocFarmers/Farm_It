from sqlalchemy.orm import Session
import sys
import os
import numpy as np

# Add Backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import GameState, Player, Tile
from game.schemas import GameStateResponse, PlayerResponse, TileResponse
from get_map.get_map import get_map
from get_map.get_history_info import get_history_info


def initialize_game(db: Session) -> None:
    """
    Initialize new game with default state.
    Creates GameState, Player, and Tiles from map generation.
    """
    print("🎮 [initialize_game] Starting game initialization")

    # Clean up old game if exists
    existing_state = db.query(GameState).first()
    if existing_state:
        print("🎮 [initialize_game] Cleaning up existing game")
        db.query(Tile).delete()
        db.query(Player).delete()
        db.query(GameState).delete()
        db.commit()

    # Generate initial map ONCE
    print("🎮 [initialize_game] Calling get_map() to generate new map")
    matrix = get_map()  # Returns (ny, nx, 3) array
    ny, nx = matrix.shape[0], matrix.shape[1]
    print(f"🎮 [initialize_game] Received map with dimensions {ny}x{nx}")

    # Create new game state with map dimensions
    game_state = GameState(
        current_step=0,
        max_steps=10,
        is_game_over=False,
        map_rows=ny,
        map_cols=nx
    )
    player = Player(shovels=3, drops=3, score=0)

    # Create tiles from matrix
    tiles = []
    tile_id = 1
    island_cells = 0
    water_cells = 0

    for i in range(ny):
        for j in range(nx):
            if matrix[i, j, 0] == 1:  # Island mask - only create tiles for island
                tile = Tile(
                    id=tile_id,
                    grid_i=i,
                    grid_j=j,
                    zone_id=1,  # Default zone, could be determined by location
                    type="empty",
                    owner=None,
                    temperature=float(matrix[i, j, 2]),
                    humidity=float(matrix[i, j, 1]),
                    last_irrigated_step=-1,
                    irrigated_this_step=False,
                    exploited="conserve"
                )
                tiles.append(tile)
                tile_id += 1
                island_cells += 1
            else:
                water_cells += 1

    # Add all objects and commit once
    db.add(game_state)
    db.add(player)
    db.add_all(tiles)
    db.commit()

    print(f"🎮 [initialize_game] Game initialized successfully")
    print(f"🎮 [initialize_game] Map dimensions: {ny}x{nx} = {ny*nx} total cells")
    print(f"🎮 [initialize_game] Island tiles created: {island_cells}")
    print(f"🎮 [initialize_game] Water cells: {water_cells}")
    print(f"🎮 [initialize_game] Verification: {island_cells + water_cells} = {ny*nx} ✓")


def get_map_from_tiles(db: Session) -> np.ndarray:
    """
    Reconstruct map matrix from stored tiles.
    Returns (ny, nx, 3) array where:
    - Layer 0: mask (0 = water, 1 = land)
    - Layer 1: soil moisture (humidity)
    - Layer 2: temperature
    """
    game_state = db.query(GameState).first()
    if not game_state:
        raise ValueError("Game not initialized")

    ny, nx = game_state.map_rows, game_state.map_cols
    matrix = np.zeros((ny, nx, 3))

    # Get all tiles
    tiles = db.query(Tile).all()

    print(f"🗺️ [get_map_from_tiles] Reconstructing map from {len(tiles)} tiles")
    print(f"🗺️ [get_map_from_tiles] Map dimensions: {ny}x{nx}")

    # Fill matrix from tiles
    for tile in tiles:
        i, j = tile.grid_i, tile.grid_j
        matrix[i, j, 0] = 1  # mask - tile exists (island)
        matrix[i, j, 1] = tile.humidity
        matrix[i, j, 2] = tile.temperature

    # Count island vs water cells
    island_cells = np.sum(matrix[:, :, 0] == 1)
    water_cells = (ny * nx) - island_cells

    print(f"🗺️ [get_map_from_tiles] Island cells: {island_cells}, Water cells: {water_cells}")

    return matrix


def get_current_game_state(db: Session) -> GameStateResponse:
    """
    Retrieve complete game state.
    Returns a Pydantic GameStateResponse with all game data.
    """
    game_state = db.query(GameState).first()
    player = db.query(Player).first()
    tiles = db.query(Tile).all()

    if not game_state or not player:
        raise ValueError("Game not initialized. Call initialize_game() first.")

    print(f"🔍 [get_current_game_state] GameState attributes: {dir(game_state)}")
    print(f"🔍 [get_current_game_state] Has map_rows: {hasattr(game_state, 'map_rows')}")
    print(f"🔍 [get_current_game_state] Has map_cols: {hasattr(game_state, 'map_cols')}")

    # Calculate tiles_owned
    tiles_owned = [t.id for t in tiles if t.owner == "player"]

    # Create Pydantic response models
    player_response = PlayerResponse(
        shovels=player.shovels,
        drops=player.drops,
        score=player.score,
        tiles_owned=tiles_owned
    )

    tile_responses = [TileResponse.model_validate(t) for t in tiles]

    print(f"🔍 [get_current_game_state] map_rows={game_state.map_rows}, map_cols={game_state.map_cols}")

    return GameStateResponse(
        step=game_state.current_step,
        max_steps=game_state.max_steps,
        is_game_over=game_state.is_game_over,
        player=player_response,
        tiles=tile_responses,
        map_shape=[game_state.map_rows, game_state.map_cols],
        map_layers=["mask", "soil_moisture", "soil_temperature"]
    )


def load_next_step_data(step: int, db: Session) -> dict:
    """
    Load weather data for the next step.
    Updates tile temperatures and humidities based on new data.
    Each step = 1 week, so we advance by 7 days in the historical data.

    Args:
        step: The step number to load data for
        db: Database session

    Returns:
        dict with update statistics
    """
    try:
        # Get historical data (using a default location for now)
        history_data = get_history_info(0.943227, 20.000000)

        # Each step = 1 week = 7 days
        day_index = step * 7

        if day_index < len(history_data.get("soil_moisture_0_to_7cm_mean", [])):
            humidity = history_data["soil_moisture_0_to_7cm_mean"][day_index]
            temperature = history_data["soil_temperature_28_to_100cm_mean"][day_index]
        else:
            # Use last available data if step exceeds available data
            humidity = history_data["soil_moisture_0_to_7cm_mean"].iloc[-1]
            temperature = history_data["soil_temperature_28_to_100cm_mean"].iloc[-1]

        # Update all tiles with new weather data
        tiles = db.query(Tile).all()
        updated_count = 0

        for tile in tiles:
            tile.humidity = float(humidity)
            tile.temperature = float(temperature)
            updated_count += 1

        db.commit()

        print(f"🌦️ [load_next_step_data] Step {step} -> Day {day_index}: temp={temperature:.1f}°C, humidity={humidity:.3f}")

        return {
            "step": step,
            "day_index": day_index,
            "tiles_updated": updated_count,
            "humidity": float(humidity),
            "temperature": float(temperature)
        }

    except Exception as e:
        print(f"❌ [load_next_step_data] Error loading weather data: {e}")
        return {
            "step": step,
            "tiles_updated": 0,
            "error": str(e)
        }


def advance_to_next_step(db: Session) -> dict:
    """
    Progress game to next turn with all mechanics.
    This is the main turn progression function that:
    1. Increments step
    2. Checks for game over
    3. Loads new weather data
    4. Resets irrigation flags
    5. Applies water reserve auto-irrigation
    6. Checks for crop deaths
    7. Advances crop states
    8. Generates resources

    Args:
        db: Database session

    Returns:
        dict with turn summary
    """
    from game.mechanics import (
        reset_irrigation_flags,
        apply_water_reserve_auto_irrigation,
        check_crop_death,
        advance_crop_state
    )

    print("\n🎯 [advance_to_next_step] ========== START TURN ADVANCE ==========")

    game_state = db.query(GameState).first()
    player = db.query(Player).first()

    if not game_state or not player:
        print("❌ [advance_to_next_step] Game not initialized")
        return {
            "success": False,
            "message": "Game not initialized"
        }

    print(f"📊 [advance_to_next_step] Current step: {game_state.current_step}")

    # Increment step
    game_state.current_step += 1
    print(f"📊 [advance_to_next_step] New step: {game_state.current_step}")

    # Check game over
    if game_state.current_step >= game_state.max_steps:
        game_state.is_game_over = True
        db.commit()
        print(f"🏁 [advance_to_next_step] Game Over! Final score: {player.score}")
        return {
            "success": True,
            "message": "Game Over!",
            "step": game_state.current_step,
            "final_score": player.score,
            "is_game_over": True
        }

    # Load new weather data
    print(f"🌦️ [advance_to_next_step] Loading weather for step {game_state.current_step}")
    weather_update = load_next_step_data(game_state.current_step, db)
    print(f"🌦️ [advance_to_next_step] Weather loaded: temp={weather_update.get('temperature')}°C, humidity={weather_update.get('humidity')}")

    # Reset irrigation flags (start of turn)
    reset_irrigation_flags(db)

    # Apply water reserve auto-irrigation
    auto_irrigated = apply_water_reserve_auto_irrigation(db, game_state.current_step)

    # Check crop deaths
    tiles_with_crops = db.query(Tile).filter(Tile.tile_state.isnot(None)).all()
    crops_died = 0
    for tile in tiles_with_crops:
        if check_crop_death(tile, game_state.current_step, db):
            crops_died += 1

    # Advance crop states for surviving crops
    surviving_crops = db.query(Tile).filter(Tile.tile_state.isnot(None)).all()
    crops_advanced = 0
    for tile in surviving_crops:
        advance_crop_state(tile, db)
        crops_advanced += 1

    # Generate resources per step (from INITAL.md specifications)
    player.shovels += 1  # +1 shovel per step
    player.drops += 1    # +1 drop per step
    player.score += 10   # +10 score per step

    # Calculate score bonuses from maintained crops
    harvest_ready = db.query(Tile).filter(Tile.tile_state == "harvest").count()

    # Commit all changes together
    db.commit()

    result = {
        "success": True,
        "step": game_state.current_step,
        "auto_irrigated_tiles": auto_irrigated,
        "crops_died": crops_died,
        "crops_advanced": crops_advanced,
        "harvest_ready": harvest_ready,
        "weather": {
            "humidity": weather_update.get("humidity", 0),
            "temperature": weather_update.get("temperature", 0)
        },
        "player_resources": {
            "shovels": player.shovels,
            "drops": player.drops,
            "score": player.score
        },
        "is_game_over": game_state.is_game_over
    }

    print(f"✅ [advance_to_next_step] Turn complete. Result: {result}")
    print("🎯 [advance_to_next_step] ========== END TURN ADVANCE ==========\n")

    return result
