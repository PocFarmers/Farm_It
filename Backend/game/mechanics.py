from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import Tile, Player
from game.adjacency import count_adjacent_conserved_forests, get_tiles_adjacent_to_water_reserves


# Humidity thresholds for crop death by zone
HUMIDITY_THRESHOLDS = {
    1: 0.15,  # Cold zone
    2: 0.10,  # Arid zone
    3: 0.20,  # Tropical zone
    4: 0.18,  # Temperate zone
}


def advance_crop_state(tile: Tile, db: Session) -> None:
    """
    Advance crop growth state: seed → growing → harvest.
    Harvest state remains until manually harvested.

    Args:
        tile: Tile with a crop
        db: Database session
    """
    if tile.tile_state == "seed":
        tile.tile_state = "growing"
    elif tile.tile_state == "growing":
        tile.tile_state = "harvest"
    # If harvest, stay at harvest until player harvests


def check_crop_death(tile: Tile, current_step: int, db: Session) -> bool:
    """
    Check if crop dies due to lack of irrigation.
    Crop dies if humidity < threshold AND not irrigated this step.

    Args:
        tile: Tile to check
        current_step: Current game step
        db: Database session

    Returns:
        True if crop died, False otherwise
    """
    # Only check tiles with crops
    if tile.tile_state not in ["seed", "growing", "harvest"]:
        return False

    # Get humidity threshold for this zone
    threshold = HUMIDITY_THRESHOLDS.get(tile.zone_id, 0.15)

    # Check if crop should die
    if tile.humidity < threshold and not tile.irrigated_this_step:
        # Crop dies
        tile.tile_state = None
        tile.type = "empty"
        return True

    return False


def harvest_tile(tile: Tile, player: Player, db: Session) -> dict:
    """
    Harvest a tile that is ready for harvest.
    Rewards: +1 shovel, +10 score base, +5 score per adjacent conserved forest.

    Args:
        tile: Tile to harvest
        player: Player object
        db: Database session

    Returns:
        dict with rewards and status
    """
    # Validate tile state
    if tile.tile_state != "harvest":
        return {
            "success": False,
            "message": "Tile is not ready for harvest"
        }

    # Calculate rewards
    base_score = 10
    shovel_reward = 1

    # Check for fertilizer bonus from adjacent conserved forests
    adjacent_forests = count_adjacent_conserved_forests(tile, db)
    fertilizer_bonus = adjacent_forests * 5

    total_score = base_score + fertilizer_bonus

    # Update player resources
    player.shovels += shovel_reward
    player.score += total_score

    # Reset tile
    tile.tile_state = None
    tile.type = "field"  # Remains a field, can be replanted

    return {
        "success": True,
        "shovels_gained": shovel_reward,
        "score_gained": total_score,
        "base_score": base_score,
        "fertilizer_bonus": fertilizer_bonus,
        "adjacent_forests": adjacent_forests
    }


def reset_irrigation_flags(db: Session) -> None:
    """
    Reset irrigated_this_step flag for all tiles.
    Called at the start of each turn.

    Args:
        db: Database session
    """
    tiles = db.query(Tile).all()
    for tile in tiles:
        tile.irrigated_this_step = False


def irrigate_tile(tile: Tile, player: Player, current_step: int, db: Session) -> dict:
    """
    Manually irrigate a tile.
    Costs 1 drop.

    Args:
        tile: Tile to irrigate
        player: Player object
        current_step: Current game step
        db: Database session

    Returns:
        dict with success status and message
    """
    # Validate player has drops
    if player.drops <= 0:
        return {
            "success": False,
            "message": "Not enough water drops"
        }

    # Validate tile is owned by player
    if tile.owner != "player":
        return {
            "success": False,
            "message": "Tile not owned by player"
        }

    # Validate tile has a crop
    if tile.type != "field" or tile.tile_state not in ["seed", "growing", "harvest"]:
        return {
            "success": False,
            "message": "Tile does not have a crop to irrigate"
        }

    # Perform irrigation
    player.drops -= 1
    tile.irrigated_this_step = True
    tile.last_irrigated_step = current_step

    return {
        "success": True,
        "message": "Tile irrigated successfully"
    }


def apply_water_reserve_auto_irrigation(db: Session, current_step: int) -> int:
    """
    Apply automatic irrigation to tiles adjacent to water reserves.
    Called at the start of each turn.

    Args:
        db: Database session
        current_step: Current game step

    Returns:
        Number of tiles auto-irrigated
    """
    # Get tiles adjacent to water reserves
    adjacent_tiles = get_tiles_adjacent_to_water_reserves(db)

    auto_irrigated_count = 0

    for tile in adjacent_tiles:
        # Only irrigate fields with crops
        if tile.type == "field" and tile.tile_state in ["seed", "growing", "harvest"]:
            tile.irrigated_this_step = True
            tile.last_irrigated_step = current_step
            auto_irrigated_count += 1

    return auto_irrigated_count
