from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.session import get_db
from database.models import Tile, Player, GameState
from game.actions import buy_tile, plant_crop, build_water_reserve, build_firebreak
from game.mechanics import irrigate_tile, harvest_tile
from game.schemas import TileActionRequest

router = APIRouter()


@router.post("/{tile_id}/buy")
async def buy_tile_endpoint(tile_id: int, db: Session = Depends(get_db)):
    """
    Buy a tile. Costs 1 shovel.
    """
    try:
        player = db.query(Player).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found. Initialize game first.")

        result = buy_tile(tile_id, player, db)
        db.commit()

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error buying tile: {str(e)}")


@router.post("/{tile_id}/plant")
async def plant_crop_endpoint(
    tile_id: int,
    request: TileActionRequest,
    db: Session = Depends(get_db)
):
    """
    Plant a crop on a tile. Tile must be owned.
    """
    try:
        if request.action != "plant":
            raise HTTPException(status_code=400, detail="Invalid action. Expected 'plant'.")

        if not request.crop_type:
            raise HTTPException(status_code=400, detail="crop_type is required for planting")

        player = db.query(Player).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        result = plant_crop(tile_id, player, request.crop_type, db)
        db.commit()

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error planting crop: {str(e)}")


@router.post("/{tile_id}/irrigate")
async def irrigate_tile_endpoint(tile_id: int, db: Session = Depends(get_db)):
    """
    Manually irrigate a tile. Costs 1 drop.
    """
    try:
        tile = db.query(Tile).filter(Tile.id == tile_id).first()
        if not tile:
            raise HTTPException(status_code=404, detail=f"Tile {tile_id} not found")

        player = db.query(Player).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        game_state = db.query(GameState).first()
        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")

        result = irrigate_tile(tile, player, game_state.current_step, db)
        db.commit()

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error irrigating tile: {str(e)}")


@router.post("/{tile_id}/harvest")
async def harvest_tile_endpoint(tile_id: int, db: Session = Depends(get_db)):
    """
    Harvest a crop from a tile. Tile must be in harvest state.
    """
    try:
        tile = db.query(Tile).filter(Tile.id == tile_id).first()
        if not tile:
            raise HTTPException(status_code=404, detail=f"Tile {tile_id} not found")

        player = db.query(Player).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        result = harvest_tile(tile, player, db)
        db.commit()

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error harvesting tile: {str(e)}")


@router.post("/{tile_id}/build-water-reserve")
async def build_water_reserve_endpoint(tile_id: int, db: Session = Depends(get_db)):
    """
    Build a water reserve on a tile. Costs 2 drops.
    Water reserves auto-irrigate adjacent tiles each turn.
    """
    try:
        player = db.query(Player).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        result = build_water_reserve(tile_id, player, db)
        db.commit()

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error building water reserve: {str(e)}")


@router.post("/{tile_id}/build-firebreak")
async def build_firebreak_endpoint(tile_id: int, db: Session = Depends(get_db)):
    """
    Build a firebreak on a tile. Costs 1 shovel.
    Firebreaks protect against fire events.
    """
    try:
        player = db.query(Player).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        result = build_firebreak(tile_id, player, db)
        db.commit()

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error building firebreak: {str(e)}")
