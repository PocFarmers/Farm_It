from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.session import get_db
from game.state import initialize_game, get_current_game_state, advance_to_next_step
from game.schemas import GameStateResponse
from get_map.get_map import get_map

router = APIRouter()


@router.get("/state", response_model=GameStateResponse)
async def get_game_state(db: Session = Depends(get_db)):
    """
    Get current game state including player resources and all tiles.
    """
    try:
        return get_current_game_state(db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving game state: {str(e)}")


@router.post("/start")
async def start_game(db: Session = Depends(get_db)):
    """
    Start a new game. Resets all game state and creates fresh map.
    """
    try:
        initialize_game(db)
        return {
            "success": True,
            "message": "Game started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting game: {str(e)}")


@router.post("/next-step")
async def next_step(db: Session = Depends(get_db)):
    """
    Advance to the next turn/step.
    Applies all game mechanics: weather updates, irrigation, crop growth, resource generation.
    """
    try:
        result = advance_to_next_step(db)
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to advance step"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error advancing step: {str(e)}")


@router.get("/map")
async def get_game_map(db: Session = Depends(get_db)):
    """
    Get current map matrix with environmental data.
    Returns format compatible with frontend MatrixGrid component.
    """
    try:
        # Generate map matrix
        matrix = get_map()

        return {
            "status": "success",
            "shape": list(matrix.shape),
            "data": matrix.tolist(),
            "layers": ["mask", "soil_moisture", "soil_temperature"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating map: {str(e)}")
