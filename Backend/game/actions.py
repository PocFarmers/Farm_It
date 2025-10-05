from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import Tile, Player


def buy_tile(tile_id: int, player: Player, db: Session) -> dict:
    """
    Buy a tile. Costs 1 shovel.

    Args:
        tile_id: ID of tile to buy
        player: Player object
        db: Database session

    Returns:
        dict with success status and message
    """
    # Get tile
    tile = db.query(Tile).filter(Tile.id == tile_id).first()
    if not tile:
        return {
            "success": False,
            "message": f"Tile {tile_id} not found"
        }

    # Validate tile is not already owned
    if tile.owner is not None:
        return {
            "success": False,
            "message": "Tile is already owned"
        }

    # Validate player has shovels
    if player.shovels <= 0:
        return {
            "success": False,
            "message": "Not enough shovels to buy tile"
        }

    # Execute purchase
    player.shovels -= 1
    tile.owner = "player"

    return {
        "success": True,
        "message": "Tile purchased successfully",
        "tile_id": tile_id,
        "shovels_remaining": player.shovels
    }


def plant_crop(tile_id: int, player: Player, crop_type: str, db: Session) -> dict:
    """
    Plant a crop on a tile. Tile must be owned and empty or field.

    Args:
        tile_id: ID of tile to plant on
        player: Player object
        crop_type: Type of crop to plant
        db: Database session

    Returns:
        dict with success status and message
    """
    # Get tile
    tile = db.query(Tile).filter(Tile.id == tile_id).first()
    if not tile:
        return {
            "success": False,
            "message": f"Tile {tile_id} not found"
        }

    # Validate tile is owned by player
    if tile.owner != "player":
        return {
            "success": False,
            "message": "Tile must be owned by player to plant crops"
        }

    # Validate tile type
    if tile.type not in ["empty", "field"]:
        return {
            "success": False,
            "message": f"Cannot plant on {tile.type} tile. Must be empty or field."
        }

    # Validate tile doesn't already have a crop
    if tile.tile_state is not None:
        return {
            "success": False,
            "message": "Tile already has a crop"
        }

    # Plant crop
    tile.type = "field"
    tile.tile_state = "seed"

    return {
        "success": True,
        "message": f"Crop planted successfully",
        "tile_id": tile_id,
        "crop_type": crop_type
    }


def build_water_reserve(tile_id: int, player: Player, db: Session) -> dict:
    """
    Build a water reserve on a tile. Costs 2 drops.
    Water reserves auto-irrigate adjacent tiles.

    Args:
        tile_id: ID of tile to build on
        player: Player object
        db: Database session

    Returns:
        dict with success status and message
    """
    # Get tile
    tile = db.query(Tile).filter(Tile.id == tile_id).first()
    if not tile:
        return {
            "success": False,
            "message": f"Tile {tile_id} not found"
        }

    # Validate tile is owned by player
    if tile.owner != "player":
        return {
            "success": False,
            "message": "Tile must be owned by player"
        }

    # Validate tile doesn't already have water reserve
    if tile.has_water_reserve:
        return {
            "success": False,
            "message": "Tile already has a water reserve"
        }

    # Validate player has enough drops
    if player.drops < 2:
        return {
            "success": False,
            "message": "Not enough water drops. Water reserve costs 2 drops."
        }

    # Build water reserve
    player.drops -= 2
    tile.has_water_reserve = True

    return {
        "success": True,
        "message": "Water reserve built successfully",
        "tile_id": tile_id,
        "drops_remaining": player.drops
    }


def build_firebreak(tile_id: int, player: Player, db: Session) -> dict:
    """
    Build a firebreak on a tile. Costs 1 shovel.
    Firebreaks protect against fire events.

    Args:
        tile_id: ID of tile to build on
        player: Player object
        db: Database session

    Returns:
        dict with success status and message
    """
    # Get tile
    tile = db.query(Tile).filter(Tile.id == tile_id).first()
    if not tile:
        return {
            "success": False,
            "message": f"Tile {tile_id} not found"
        }

    # Validate tile is owned by player
    if tile.owner != "player":
        return {
            "success": False,
            "message": "Tile must be owned by player"
        }

    # Validate tile doesn't already have firebreak
    if tile.has_firebreak:
        return {
            "success": False,
            "message": "Tile already has a firebreak"
        }

    # Validate player has enough shovels
    if player.shovels <= 0:
        return {
            "success": False,
            "message": "Not enough shovels. Firebreak costs 1 shovel."
        }

    # Build firebreak
    player.shovels -= 1
    tile.has_firebreak = True

    return {
        "success": True,
        "message": "Firebreak built successfully",
        "tile_id": tile_id,
        "shovels_remaining": player.shovels
    }


def set_forest_exploitation(tile_id: int, player: Player, mode: str, db: Session) -> dict:
    """
    Set forest exploitation mode.
    Conserve: Provides fertilizer bonus to adjacent fields
    Exploit: Generates resources but no bonus

    Args:
        tile_id: ID of forest tile
        player: Player object
        mode: "conserve" or "exploit"
        db: Database session

    Returns:
        dict with success status and message
    """
    # Get tile
    tile = db.query(Tile).filter(Tile.id == tile_id).first()
    if not tile:
        return {
            "success": False,
            "message": f"Tile {tile_id} not found"
        }

    # Validate tile is owned by player
    if tile.owner != "player":
        return {
            "success": False,
            "message": "Tile must be owned by player"
        }

    # Validate tile is a forest
    if tile.type != "forest":
        return {
            "success": False,
            "message": "Tile must be a forest"
        }

    # Validate mode
    if mode not in ["conserve", "exploit"]:
        return {
            "success": False,
            "message": "Mode must be 'conserve' or 'exploit'"
        }

    # Set exploitation mode
    tile.exploited = mode

    return {
        "success": True,
        "message": f"Forest exploitation set to {mode}",
        "tile_id": tile_id,
        "mode": mode
    }
