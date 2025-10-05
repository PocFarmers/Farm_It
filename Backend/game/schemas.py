from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class TileResponse(BaseModel):
    """Response model for tile data"""
    id: int
    grid_i: int
    grid_j: int
    zone_id: int
    type: Literal["forest", "field", "empty"]
    owner: Optional[str] = None
    tile_state: Optional[Literal["seed", "growing", "harvest"]] = None
    has_water_reserve: bool
    has_firebreak: bool
    temperature: float
    humidity: float
    last_irrigated_step: int
    irrigated_this_step: bool
    exploited: Literal["conserve", "exploit"]
    event: Optional[Literal["Drought", "Fire"]] = None

    class Config:
        from_attributes = True


class PlayerResponse(BaseModel):
    """Response model for player data"""
    shovels: int = Field(ge=0, description="Number of shovels owned")
    drops: int = Field(ge=0, description="Number of water drops owned")
    score: int = Field(ge=0, description="Current score")
    tiles_owned: List[int] = Field(default_factory=list, description="List of owned tile IDs")

    class Config:
        from_attributes = True


class GameStateResponse(BaseModel):
    """Complete game state response"""
    step: int = Field(ge=0, description="Current turn/step number")
    max_steps: int = Field(ge=1, description="Maximum number of steps in game")
    is_game_over: bool = Field(description="Whether game has ended")
    player: PlayerResponse
    tiles: List[TileResponse]
    map_shape: List[int] = Field(description="Map dimensions [rows, cols]")
    map_layers: List[str] = Field(default=["mask", "soil_moisture", "soil_temperature"], description="Layer names")


class TileActionRequest(BaseModel):
    """Request model for tile actions"""
    action: Literal["buy", "irrigate", "plant", "harvest", "build_water_reserve", "build_firebreak"]
    crop_type: Optional[str] = Field(default=None, description="Type of crop to plant (required for plant action)")

    class Config:
        json_schema_extra = {
            "examples": [
                {"action": "buy"},
                {"action": "plant", "crop_type": "wheat"},
                {"action": "irrigate"},
                {"action": "harvest"}
            ]
        }
