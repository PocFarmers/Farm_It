from chatbot import ChatRequest, ChatResponse, build_input_blocks
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Ajouter le dossier Backend au path pour les imports
sys.path.append(os.path.dirname(__file__))

from get_map.get_map import get_map
from in_game.get_event import get_event
from database.models import Base
from database.session import engine
from routers import game, tile

app = FastAPI(
    title="Farm It API",
    version="1.0.0",
    description="Backend API for Farm It - A turn-based farming game with resource management"
)

# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """Create database tables on application startup"""
    Base.metadata.create_all(bind=engine)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game.router, prefix="/game", tags=["game"])
app.include_router(tile.router, prefix="/tile", tags=["tile"])

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
        print(f"combined_matrix.shape: {combined_matrix.shape}")
        return {
            "status": "success",
            "shape": combined_matrix.shape,
            "data": combined_matrix.tolist(),
            "layers": ["mask", "soil_moisture", "soil_temperature"]
        }
    except Exception as e:
        import traceback
        print(f"ERROR in /get_map: {e}")
        print(traceback.format_exc())
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

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not client.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY manquant dans l'environnement.")

    try:
        input_blocks = build_input_blocks(
            system=req.system,
            history=req.history,
            user_message=req.message,
            context=req.context
        )

        resp = client.responses.create(
            model=req.model,
            input=input_blocks,
        )

        text = ""
        if resp.output:
            for block in resp.output:
                if block.type == "message":
                    for part in block.content:
                        if part.type == "output_text":
                            text += part.text
        text = text.strip()

        usage_in = getattr(resp, "usage", None).input_tokens if getattr(resp, "usage", None) else None
        usage_out = getattr(resp, "usage", None).output_tokens if getattr(resp, "usage", None) else None

        return ChatResponse(
            text=text,
            model=req.model,
            usage_input_tokens=usage_in,
            usage_output_tokens=usage_out
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OpenAI: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
