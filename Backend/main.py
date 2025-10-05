from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Ajouter le dossier Backend au path pour les imports
sys.path.append(os.path.dirname(__file__))

from get_map.get_map import get_map
from get_map.get_history_info import get_history_info
from in_game.get_event import get_event

app = FastAPI(title="Farm It API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EventRequest(BaseModel):
    temperature: float
    soil_moisture: float

@app.get("/")
async def root():
    return {"message": "Farm It API", "version": "1.0.0"}

@app.get("/get_map")
async def api_get_map():
    """
    Génère une carte 3D avec les couches :
    - Couche 0 : présence de l'île (mask)
    - Couche 1 : humidité du sol (soil_moisture)
    - Couche 2 : température du sol (soil_temperature)
    """
    try:
        combined_matrix = get_map()

        # Convertir le numpy array en liste pour la sérialisation JSON
        return {
            "status": "success",
            "shape": combined_matrix.shape,
            "data": combined_matrix.tolist(),
            "layers": ["mask", "soil_moisture", "soil_temperature"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_event")
async def api_get_event(request: EventRequest):
    """
    Détermine l'événement basé sur la température et l'humidité du sol
    """
    try:
        event = get_event(request.temperature, request.soil_moisture)

        return {
            "status": "success",
            "event": event,
            "inputs": {
                "temperature": request.temperature,
                "soil_moisture": request.soil_moisture
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
