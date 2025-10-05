from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.session import get_db
from game.state import initialize_game, get_current_game_state, advance_to_next_step
from game.schemas import GameStateResponse

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


@router.post("/start", response_model=GameStateResponse)
async def start_game(db: Session = Depends(get_db)):
    """
    Start a new game. Resets all game state and creates fresh map.
    Returns the complete game state including map structure.
    """
    try:
        print("🚀 [POST /game/start] Received request to start new game")
        initialize_game(db)
        print("🚀 [POST /game/start] Game initialized, fetching game state")
        game_state = get_current_game_state(db)
        print(f"🚀 [POST /game/start] Returning game state with {len(game_state.tiles)} tiles")
        return game_state
    except Exception as e:
        print(f"❌ [POST /game/start] Error: {str(e)}")
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
