from pydantic import BaseModel
from typing import List, Optional

class ParcelBase(BaseModel):
    lat: float
    lng: float
    zone_id: str
    parcel_type: str
    owned: bool = False
    crop_type: Optional[str] = None
    crop_stage: Optional[str] = None
    crop_stage_counter: int = 0
    has_water_reserve: bool = False
    has_firebreak: bool = False
    is_forest_preserved: bool = True

class ParcelCreate(ParcelBase):
    pass

class Parcel(ParcelBase):
    id: int
    game_state_id: int

    class Config:
        from_attributes = True

class GameStateBase(BaseModel):
    current_stage: int = 0
    shovels: int = 10
    water_drops: int = 10
    score: int = 0

class GameStateCreate(GameStateBase):
    pass

class GameState(GameStateBase):
    id: int
    parcels: List[Parcel] = []

    class Config:
        from_attributes = True

class ActionRequest(BaseModel):
    parcel_id: int
    action: str  # "buy_parcel", "plant_crop", "irrigate", "fertilize", "buy_water_reserve", "buy_firebreak"
    crop_type: Optional[str] = None  # for plant_crop action

class ActionResponse(BaseModel):
    success: bool
    message: str
    game_state: Optional[GameState] = None

class StageProgressResponse(BaseModel):
    new_stage: int
    events: List[dict]
    crop_updates: List[dict]
    score_change: int
    game_state: GameState
