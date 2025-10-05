from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

import models
import schemas
import crud
from database import engine, get_db
import tif_handler

load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Farm_It API", version="1.0.0")

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Farm_It API", "version": "1.0.0"}

@app.post("/api/game", response_model=schemas.GameState)
def create_game(db: Session = Depends(get_db)):
    """Create a new game"""
    game = crud.create_game_state(db)
    return game

@app.get("/api/game/{game_id}", response_model=schemas.GameState)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get game state by ID"""
    game = crud.get_game_state(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.get("/api/parcels/{game_id}", response_model=list[schemas.Parcel])
def get_parcels(game_id: int, db: Session = Depends(get_db)):
    """Get all parcels for a game"""
    game = crud.get_game_state(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return crud.get_parcels(db, game_id)

@app.post("/api/game/{game_id}/action", response_model=schemas.ActionResponse)
def execute_action(game_id: int, action: schemas.ActionRequest, db: Session = Depends(get_db)):
    """Execute a game action"""
    result = crud.execute_action(db, game_id, action)

    if not result.get("success"):
        return schemas.ActionResponse(
            success=False,
            message=result.get("message", "Action failed"),
            game_state=None
        )

    # Get updated game state
    game = crud.get_game_state(db, game_id)

    return schemas.ActionResponse(
        success=True,
        message=result.get("message", "Action executed"),
        game_state=game
    )

@app.post("/api/game/{game_id}/next-stage", response_model=schemas.StageProgressResponse)
def next_stage(game_id: int, db: Session = Depends(get_db)):
    """Progress to next stage"""
    result = crud.progress_stage(db, game_id)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Cannot progress stage"))

    # Get updated game state
    game = crud.get_game_state(db, game_id)

    return schemas.StageProgressResponse(
        new_stage=result["new_stage"],
        events=result["events"],
        crop_updates=result["crop_updates"],
        score_change=result["score_change"],
        game_state=game
    )

@app.get("/api/tif/{zone_id}/{stage}")
def get_tif_image(zone_id: str, stage: int):
    """Get TIF visualization as PNG for a zone and stage"""
    if zone_id not in tif_handler.ZONE_TIF_DIRS:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")

    if stage < 1 or stage > 50:
        raise HTTPException(status_code=400, detail="Stage must be between 1 and 50")

    tif_path = tif_handler.get_tif_for_stage(zone_id, stage)

    if not tif_path or not os.path.exists(tif_path):
        raise HTTPException(status_code=404, detail=f"No TIF data for zone {zone_id} at stage {stage}")

    png_bytes = tif_handler.tif_to_png_bytes(tif_path)

    if not png_bytes:
        raise HTTPException(status_code=500, detail="Error processing TIF file")

    return StreamingResponse(png_bytes, media_type="image/png")

@app.get("/api/tif/{zone_id}/{stage}/bounds")
def get_tif_bounds_endpoint(zone_id: str, stage: int):
    """Get geographic bounds of TIF for a zone and stage"""
    if zone_id not in tif_handler.ZONE_TIF_DIRS:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")

    if stage < 1 or stage > 50:
        raise HTTPException(status_code=400, detail="Stage must be between 1 and 50")

    tif_path = tif_handler.get_tif_for_stage(zone_id, stage)

    if not tif_path or not os.path.exists(tif_path):
        raise HTTPException(status_code=404, detail=f"No TIF data for zone {zone_id} at stage {stage}")

    bounds = tif_handler.get_tif_bounds(tif_path)

    if not bounds:
        raise HTTPException(status_code=500, detail="Error reading TIF bounds")

    return bounds

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
