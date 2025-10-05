name: "Farm It - Complete Game Backend Implementation"
description: |
  Implement a complete turn-based farming game backend with FastAPI, including game state management,
  player actions, crop cycles, resource management, and geospatial data integration.

---

## Goal
Build a production-ready FastAPI backend that manages the complete Farm It game logic, including:
- Turn-based progression through historical weather data (GeoJSON steps)
- Player resource management (shovels, drops, score)
- Tile ownership and state management
- Crop lifecycle (seed → growing → harvest)
- Local effects (forests, water reserves, irrigation)
- Persistence layer with SQLite
- RESTful API for all game actions

## Why
- **Business value**: Enable a playable farming game with strategic resource management
- **User experience**: Provide responsive game state updates and clear feedback on actions
- **Integration**: Works seamlessly with existing React frontend that visualizes the map
- **Problems solved**: Complete game loop from map generation to player actions to scoring

## What
Implement backend game engine with:
- Game state persistence (current step, player resources, tile states)
- Turn progression system that loads next GeoJSON weather data
- Player action endpoints (buy tile, plant crop, irrigate, etc.)
- Automated game mechanics (crop growth, death checks, resource generation)
- Adjacency-based local effects (forest bonuses, water reserve auto-irrigation)
- Score calculation and game end detection

### Success Criteria
- [ ] Player can start a new game and view initial map with resources
- [ ] Player can buy tiles and plant crops
- [ ] Turn progression updates crop states (seed → growing → harvest)
- [ ] Harvesting generates resources (shovels, score)
- [ ] Water reserves auto-irrigate adjacent tiles
- [ ] Conserved forests give fertilizer bonus to adjacent fields
- [ ] Crops die if not irrigated when needed
- [ ] Game state persists across server restarts
- [ ] Game ends when no more GeoJSON steps available

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window

- url: https://fastapi.tiangolo.com/tutorial/sql-databases/
  why: Official FastAPI SQLite integration pattern with dependency injection
  critical: Use yield pattern for session management, create tables on startup

- url: https://docs.pydantic.dev/latest/
  why: Pydantic v2 model definitions, validators, and serialization
  critical: Project uses pydantic==2.5.0, use v2 syntax (model_dump, model_validate)

- url: https://docs.sqlalchemy.org/en/20/orm/
  why: SQLAlchemy 2.0 ORM patterns for defining database models
  critical: Use declarative_base and proper relationship definitions

- pattern: Event-sourcing pattern for turn-based games
  why: Each turn generates events (crop growth, resource generation, etc.)
  source: https://gameprogrammingpatterns.com/state.html
  critical: State transitions should be deterministic and reproducible

- file: Backend/main.py
  why: Existing FastAPI setup with CORS, shows current API structure
  critical: Already has /get_map endpoint for 3D matrix, keep compatible

- file: Backend/get_map/get_map.py
  why: Shows how GeoJSON mask generation and TIF layer integration works
  critical: Function generates (ny, nx, 3) matrix with mask, humidity, temperature

- file: Backend/get_map/get_history_info.py
  why: Fetches historical weather data for coordinates
  critical: Returns soil_moisture and soil_temperature arrays

- file: Backend/in_game/get_event.py
  why: Event detection based on temperature/humidity thresholds
  critical: Uses nasa_event_thresholds.csv to determine events

- file: INITAL.md
  why: Complete game specification with entities, rules, and mechanics
  critical: Defines Tile and Player schemas, game rules, and turn logic

- file: frontend/src/App.jsx
  why: Frontend expects specific API response format
  critical: Must return compatible data structure for matrix visualization
```

### Current Codebase Tree
```bash
Backend/
├── main.py                    # FastAPI app with /get_map, /get_event, /health
├── requirements.txt           # FastAPI 0.104.1, pydantic 2.5.0, SQLAlchemy needed
├── get_map/
│   ├── get_map.py            # Generates 3D matrix (mask, humidity, temp)
│   ├── get_history_info.py  # Fetches historical weather data
│   ├── download_files.py     # Downloads NASA data
│   └── data/
│       ├── masks/            # 4 GeoJSON bean-shaped masks
│       ├── temperature/      # 4 TIF files (aride, froide, tempere, tropicale)
│       └── humidite/         # 4 TIF files
├── in_game/
│   └── get_event.py          # Event detection from temp/humidity
├── database/                  # EMPTY - needs implementation
├── routers/                   # EMPTY - needs implementation
└── game/                      # EMPTY - needs implementation

frontend/
├── src/
│   ├── App.jsx               # Main UI, expects { status, shape, data, layers }
│   ├── components/
│   │   ├── MatrixGrid.jsx    # Displays the 3D matrix
│   │   └── MatrixCell.jsx    # Individual cell rendering
│   └── hooks/
│       └── useMatrixData.js  # Fetches from /get_map endpoint

data/
├── masks/                     # 4 GeoJSON files (paris, amazon, kinshasa, biskra)
├── temperature/               # 4 TIF files per climate zone
└── humidite/                  # 4 TIF files per climate zone
```

### Desired Codebase Tree with New Files
```bash
Backend/
├── main.py                           # [MODIFY] Add new routers, startup event
├── requirements.txt                  # [MODIFY] Add SQLAlchemy, python-dotenv
├── database/
│   ├── __init__.py                  # [CREATE] Database connection setup
│   ├── models.py                    # [CREATE] SQLAlchemy ORM models
│   └── session.py                   # [CREATE] Session dependency with yield
├── routers/
│   ├── __init__.py                  # [CREATE] Router exports
│   ├── game.py                      # [CREATE] /game/* endpoints
│   └── tile.py                      # [CREATE] /tile/* endpoints
├── game/
│   ├── __init__.py                  # [CREATE] Game logic exports
│   ├── schemas.py                   # [CREATE] Pydantic models for API
│   ├── state.py                     # [CREATE] Game state management
│   ├── actions.py                   # [CREATE] Player action handlers
│   ├── mechanics.py                 # [CREATE] Crop cycles, irrigation logic
│   ├── adjacency.py                 # [CREATE] 8-neighbor effects
│   └── scoring.py                   # [CREATE] Resource and score calculation
├── tests/                            # [CREATE] Test directory
│   ├── __init__.py
│   ├── test_game_state.py
│   ├── test_actions.py
│   └── test_mechanics.py
└── .env.example                      # [CREATE] Environment variables template
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: SQLite threading in FastAPI
# SQLite default behavior restricts connections to the creating thread
# MUST use: connect_args={"check_same_thread": False}

# CRITICAL: Pydantic v2 breaking changes from v1
# Use model_dump() instead of dict()
# Use model_validate() instead of parse_obj()
# Field validation syntax: Field(gt=0, lt=1000) not Field(..., gt=0)

# CRITICAL: FastAPI dependency injection with yield
# Code before yield runs before request
# Code after yield runs after response (cleanup)
# Use for database session management

# CRITICAL: NumPy array JSON serialization
# NumPy arrays must be converted to lists via .tolist()
# Already handled in existing /get_map endpoint

# CRITICAL: GeoJSON coordinate order is [longitude, latitude]
# Not [lat, lon] - this is a common mistake!

# CRITICAL: Adjacency logic must handle grid boundaries
# Check i-1, i+1, j-1, j+1 are within [0, ny) and [0, nx)

# CRITICAL: Game state must persist in database, NOT in memory
# Static class variables will cause issues in production
# Each request must load state from DB

# CRITICAL: Turn progression is sequential
# Step N corresponds to data/geojson_{N}.json or historical data point N
# Game lasts as many steps as available data points

# CRITICAL: Crop death conditions
# Crop dies if not irrigated when soil_moisture < threshold
# Check on each turn, before applying new growth state
```

## Implementation Blueprint

### Data Models and Structure

#### 1. Database Models (SQLAlchemy ORM)
Create `Backend/database/models.py`:
```python
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class GameState(Base):
    """Singleton table for game state"""
    __tablename__ = "game_state"
    id = Column(Integer, primary_key=True, default=1)
    current_step = Column(Integer, default=0)
    max_steps = Column(Integer, default=10)  # Based on available data
    is_game_over = Column(Boolean, default=False)

class Player(Base):
    """Player resources and state"""
    __tablename__ = "player"
    id = Column(Integer, primary_key=True, default=1)
    shovels = Column(Integer, default=3)
    drops = Column(Integer, default=3)
    score = Column(Integer, default=0)

class Tile(Base):
    """Individual tile state"""
    __tablename__ = "tiles"
    id = Column(Integer, primary_key=True)
    grid_i = Column(Integer, nullable=False)  # Row index
    grid_j = Column(Integer, nullable=False)  # Column index
    zone_id = Column(Integer, nullable=False)  # 1=cold, 2=arid, 3=tropical, 4=temperate
    type = Column(String, default="empty")  # "forest", "field", "empty"
    owner = Column(String, nullable=True)  # null or "player"
    tile_state = Column(String, nullable=True)  # "seed", "growing", "harvest"
    has_water_reserve = Column(Boolean, default=False)
    has_firebreak = Column(Boolean, default=False)
    temperature = Column(Float, default=0.0)
    humidity = Column(Float, default=0.0)
    last_irrigated_step = Column(Integer, default=-1)
    irrigated_this_step = Column(Boolean, default=False)
    exploited = Column(String, default="conserve")  # "conserve" or "exploit"
```

#### 2. Pydantic Schemas (API Models)
Create `Backend/game/schemas.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class TileResponse(BaseModel):
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

    class Config:
        from_attributes = True  # Pydantic v2 for ORM mode

class PlayerResponse(BaseModel):
    shovels: int
    drops: int
    score: int
    tiles_owned: List[int]

    class Config:
        from_attributes = True

class GameStateResponse(BaseModel):
    step: int
    max_steps: int
    is_game_over: bool
    player: PlayerResponse
    tiles: List[TileResponse]

class TileActionRequest(BaseModel):
    action: Literal["buy", "irrigate", "plant", "harvest", "build_water_reserve", "build_firebreak"]
    crop_type: Optional[str] = None  # For plant action
```

### List of Tasks in Implementation Order

```yaml
Task 1: Database Infrastructure Setup
  PRIORITY: CRITICAL - Foundation for all other tasks

  CREATE Backend/database/__init__.py:
    - Empty __init__ to make it a package

  CREATE Backend/database/session.py:
    - Import create_engine, sessionmaker from sqlalchemy
    - Create engine with sqlite:///./farm_it.db
    - CRITICAL: Use connect_args={"check_same_thread": False}
    - Create SessionLocal with autocommit=False, autoflush=False
    - Define get_db() dependency with yield pattern
    - Pattern: try/yield/finally block for session cleanup

  CREATE Backend/database/models.py:
    - Define Base = declarative_base()
    - Create GameState, Player, Tile models as specified above
    - Add __repr__ methods for debugging

  MODIFY Backend/main.py:
    - Import Base, engine from database.models and database.session
    - Add @app.on_event("startup") handler
    - Create all tables: Base.metadata.create_all(bind=engine)
    - Initialize default game state if not exists

  MODIFY Backend/requirements.txt:
    - Add: sqlalchemy==2.0.23
    - Add: python-dotenv==1.0.0

  VALIDATION:
    - Run: pip install -r Backend/requirements.txt
    - Run: python Backend/main.py (server starts)
    - Check: farm_it.db file created in root
    - Check: Tables exist: sqlite3 farm_it.db ".tables"

Task 2: Pydantic Schema Definitions
  PRIORITY: HIGH - Required for API endpoints

  CREATE Backend/game/__init__.py:
    - Empty __init__ to make it a package

  CREATE Backend/game/schemas.py:
    - Define all Pydantic models as specified above
    - TileResponse, PlayerResponse, GameStateResponse
    - TileActionRequest with action validation
    - Add validators for business rules (e.g., shovels >= 0)

  VALIDATION:
    - Run: python -c "from Backend.game.schemas import *"
    - Check: No import errors
    - Test: Create instance of each model with valid data

Task 3: Game State Management Core
  PRIORITY: CRITICAL - Core game engine

  CREATE Backend/game/state.py:
    - Function: initialize_game(db: Session) -> None
      - Create default GameState (step=0, max_steps=10)
      - Create default Player (shovels=3, drops=3, score=0)
      - Generate initial tiles from get_map()
      - Save all to database

    - Function: get_current_game_state(db: Session) -> GameStateResponse
      - Query GameState, Player, all Tiles
      - Calculate tiles_owned from Tile.owner == "player"
      - Return Pydantic GameStateResponse

    - Function: load_next_step_data(step: int) -> tuple[np.ndarray, dict]
      - Call get_history_info() for step N
      - Generate matrix with get_map() pattern
      - Return matrix and metadata

  VALIDATION:
    - Unit test: test_initialize_game()
    - Unit test: test_get_current_game_state()
    - Unit test: test_load_next_step_data()

Task 4: Adjacency Logic Implementation
  PRIORITY: HIGH - Required for local effects

  CREATE Backend/game/adjacency.py:
    - Function: get_neighbors(grid_i: int, grid_j: int, ny: int, nx: int) -> List[Tuple[int, int]]
      - Return 8-neighbor coordinates (N, NE, E, SE, S, SW, W, NW)
      - Handle boundary conditions (edges and corners)
      - Skip invalid coordinates

    - Function: get_adjacent_tiles(tile_id: int, db: Session) -> List[Tile]
      - Get tile's grid_i, grid_j
      - Get matrix dimensions from GameState
      - Query tiles at neighbor coordinates
      - Return list of Tile objects

    - Function: count_adjacent_conserved_forests(tile_id: int, db: Session) -> int
      - Get adjacent tiles
      - Count where type="forest" AND exploited="conserve"

    - Function: has_adjacent_water_reserve(tile_id: int, db: Session) -> bool
      - Get adjacent tiles
      - Return True if any has_water_reserve=True

  VALIDATION:
    - Unit test: test_get_neighbors_center() # Center tile has 8 neighbors
    - Unit test: test_get_neighbors_corner() # Corner tile has 3 neighbors
    - Unit test: test_get_neighbors_edge() # Edge tile has 5 neighbors
    - Unit test: test_count_adjacent_forests()
    - Unit test: test_has_adjacent_water_reserve()

Task 5: Game Mechanics - Crop Lifecycle
  PRIORITY: CRITICAL - Core gameplay loop

  CREATE Backend/game/mechanics.py:
    - Function: advance_crop_state(tile: Tile, db: Session) -> None
      - If tile_state == "seed": set to "growing"
      - If tile_state == "growing": set to "harvest"
      - If tile_state == "harvest": stays until harvested
      - Commit changes

    - Function: check_crop_death(tile: Tile, current_step: int, db: Session) -> bool
      - Get humidity threshold from zone_id
      - If humidity < threshold AND not irrigated_this_step:
        - Set tile_state = None
        - Set type = "empty"
        - Return True (crop died)
      - Return False

    - Function: harvest_tile(tile: Tile, player: Player, db: Session) -> dict:
      - Validate tile_state == "harvest"
      - Calculate rewards: +1 shovel, +10 score base
      - Check adjacent conserved forests for fertilizer bonus
      - If has fertilizer bonus: +5 additional score
      - Update player resources
      - Reset tile: tile_state=None, type="field"
      - Return rewards dict

  VALIDATION:
    - Unit test: test_advance_crop_state_seed_to_growing()
    - Unit test: test_advance_crop_state_growing_to_harvest()
    - Unit test: test_check_crop_death_not_irrigated()
    - Unit test: test_check_crop_death_irrigated_survives()
    - Unit test: test_harvest_tile_basic_rewards()
    - Unit test: test_harvest_tile_with_forest_bonus()

Task 6: Game Mechanics - Irrigation System
  PRIORITY: HIGH - Prevents crop death

  EXTEND Backend/game/mechanics.py:
    - Function: irrigate_tile(tile: Tile, player: Player, current_step: int, db: Session) -> bool
      - Validate player.drops > 0
      - Validate tile.owner == "player"
      - Validate tile.type == "field" with crop
      - Decrement player.drops
      - Set tile.irrigated_this_step = True
      - Set tile.last_irrigated_step = current_step
      - Return True (success)

    - Function: apply_water_reserve_auto_irrigation(db: Session, current_step: int) -> int
      - Find all tiles with has_water_reserve=True
      - For each, get adjacent tiles
      - For adjacent fields with crops:
        - Set irrigated_this_step = True
        - Set last_irrigated_step = current_step
      - Return count of auto-irrigated tiles

    - Function: reset_irrigation_flags(db: Session) -> None
      - Set irrigated_this_step = False for all tiles
      - Called at start of each turn

  VALIDATION:
    - Unit test: test_irrigate_tile_success()
    - Unit test: test_irrigate_tile_no_drops()
    - Unit test: test_water_reserve_auto_irrigation()
    - Unit test: test_reset_irrigation_flags()

Task 7: Player Actions Implementation
  PRIORITY: CRITICAL - User interaction

  CREATE Backend/game/actions.py:
    - Function: buy_tile(tile_id: int, player: Player, db: Session) -> dict
      - Validate tile.owner is None
      - Validate player.shovels > 0
      - Decrement player.shovels
      - Set tile.owner = "player"
      - Return success message

    - Function: plant_crop(tile_id: int, player: Player, crop_type: str, db: Session) -> dict
      - Validate tile.owner == "player"
      - Validate tile.type in ["empty", "field"]
      - Set tile.type = "field"
      - Set tile.tile_state = "seed"
      - Return success message

    - Function: build_water_reserve(tile_id: int, player: Player, db: Session) -> dict
      - Validate tile.owner == "player"
      - Validate player.drops >= 2 (cost)
      - Decrement player.drops by 2
      - Set tile.has_water_reserve = True
      - Return success message

    - Function: build_firebreak(tile_id: int, player: Player, db: Session) -> dict
      - Validate tile.owner == "player"
      - Validate player.shovels >= 1 (cost)
      - Decrement player.shovels
      - Set tile.has_firebreak = True
      - Return success message

  VALIDATION:
    - Unit test: test_buy_tile_success()
    - Unit test: test_buy_tile_no_shovels()
    - Unit test: test_plant_crop_success()
    - Unit test: test_plant_crop_not_owned()
    - Unit test: test_build_water_reserve()
    - Unit test: test_build_firebreak()

Task 8: Turn Progression System
  PRIORITY: CRITICAL - Core game loop

  EXTEND Backend/game/state.py:
    - Function: advance_to_next_step(db: Session) -> dict
      - Get current GameState
      - Increment current_step
      - Check if current_step >= max_steps: set is_game_over=True

      - Load next step data (weather)
      - Update all tile temperatures and humidities

      - Reset irrigation flags
      - Apply water reserve auto-irrigation
      - Check crop deaths for all tiles
      - Advance crop states for surviving crops

      - Generate resources: +1 drop per turn base
      - Calculate score bonuses from maintained crops

      - Commit all changes
      - Return summary dict

  VALIDATION:
    - Integration test: test_full_turn_progression()
    - Integration test: test_crop_survives_with_irrigation()
    - Integration test: test_crop_dies_without_irrigation()
    - Integration test: test_game_ends_at_max_steps()

Task 9: API Router - Game Endpoints
  PRIORITY: HIGH - API layer

  CREATE Backend/routers/__init__.py:
    - Empty __init__

  CREATE Backend/routers/game.py:
    - Import APIRouter, Depends, HTTPException
    - Import get_db from database.session
    - Import game.state, game.schemas

    - GET /game/state -> GameStateResponse:
      - Call get_current_game_state(db)
      - Return response

    - POST /game/start -> dict:
      - Delete existing game data
      - Call initialize_game(db)
      - Return {"message": "Game started"}

    - POST /game/next-step -> dict:
      - Call advance_to_next_step(db)
      - Return summary

    - GET /game/map -> dict:
      - Get current game state
      - Call get_map() to generate matrix
      - Return compatible with frontend expectation

  VALIDATION:
    - Integration test: curl POST /game/start
    - Integration test: curl GET /game/state
    - Integration test: curl POST /game/next-step
    - Check: All endpoints return 200 with valid data

Task 10: API Router - Tile Actions
  PRIORITY: HIGH - Player interaction

  CREATE Backend/routers/tile.py:
    - Import APIRouter, Depends, HTTPException
    - Import get_db, actions, mechanics

    - POST /tile/{tile_id}/buy -> dict:
      - Get player and tile from db
      - Call actions.buy_tile()
      - Return result

    - POST /tile/{tile_id}/plant -> dict:
      - Parse TileActionRequest body
      - Call actions.plant_crop()
      - Return result

    - POST /tile/{tile_id}/irrigate -> dict:
      - Get player, tile, current_step
      - Call mechanics.irrigate_tile()
      - Return result

    - POST /tile/{tile_id}/harvest -> dict:
      - Get player and tile
      - Call mechanics.harvest_tile()
      - Return result

    - POST /tile/{tile_id}/build-water-reserve -> dict:
      - Call actions.build_water_reserve()
      - Return result

    - POST /tile/{tile_id}/build-firebreak -> dict:
      - Call actions.build_firebreak()
      - Return result

  VALIDATION:
    - Integration test: Full game flow
      - Start game
      - Buy tile
      - Plant crop
      - Advance turn
      - Irrigate
      - Advance turn
      - Harvest
      - Check score increased

Task 11: Main App Integration
  PRIORITY: CRITICAL - Wiring everything together

  MODIFY Backend/main.py:
    - Import routers.game, routers.tile
    - app.include_router(game.router, prefix="/game", tags=["game"])
    - app.include_router(tile.router, prefix="/tile", tags=["tile"])
    - Keep existing /get_map endpoint for frontend compatibility
    - Add error handling middleware

  VALIDATION:
    - Run: python Backend/main.py
    - Visit: http://localhost:8000/docs
    - Check: All endpoints visible in Swagger UI
    - Test: Each endpoint via Swagger UI

Task 12: Error Handling and Validation
  PRIORITY: MEDIUM - Polish

  ENHANCE all action functions:
    - Add try/except blocks
    - Raise HTTPException with appropriate status codes:
      - 400: Invalid request (not enough resources)
      - 404: Tile not found
      - 409: Conflict (tile already owned)
    - Add logging for errors

  CREATE Backend/game/exceptions.py:
    - Define custom exceptions:
      - InsufficientResourcesError
      - TileNotOwnedError
      - InvalidTileStateError
    - Map to HTTP status codes

  VALIDATION:
    - Test: Try buying tile twice (409 expected)
    - Test: Try planting without shovel (400 expected)
    - Test: Invalid tile_id (404 expected)

Task 13: Testing Suite
  PRIORITY: MEDIUM - Quality assurance

  CREATE Backend/tests/__init__.py:
    - Empty __init__

  CREATE Backend/tests/conftest.py:
    - Pytest fixtures:
      - test_db: In-memory SQLite for tests
      - test_client: FastAPI TestClient
      - sample_game_state: Fixture with initialized game

  CREATE Backend/tests/test_game_state.py:
    - Test initialize_game
    - Test get_current_game_state
    - Test advance_to_next_step

  CREATE Backend/tests/test_actions.py:
    - Test all player actions (buy, plant, irrigate, harvest)
    - Test error cases (insufficient resources, etc.)

  CREATE Backend/tests/test_mechanics.py:
    - Test crop lifecycle
    - Test irrigation system
    - Test adjacency effects

  CREATE Backend/tests/test_api.py:
    - Integration tests for all endpoints
    - Test full game flow

  VALIDATION:
    - Run: pytest Backend/tests/ -v
    - Target: >80% code coverage
    - All tests passing
```

### Per-Task Pseudocode (Selected Critical Tasks)

#### Task 3: Game State Management Core
```python
# Backend/game/state.py

from sqlalchemy.orm import Session
from Backend.database.models import GameState, Player, Tile
from Backend.game.schemas import GameStateResponse, PlayerResponse, TileResponse
from Backend.get_map.get_map import get_map

def initialize_game(db: Session) -> None:
    """Initialize new game with default state"""
    # PATTERN: Use db.query().first() to check existence
    existing_state = db.query(GameState).first()
    if existing_state:
        # Clean up old game
        db.query(Tile).delete()
        db.query(Player).delete()
        db.query(GameState).delete()

    # Create new game state
    game_state = GameState(current_step=0, max_steps=10, is_game_over=False)
    player = Player(shovels=3, drops=3, score=0)

    # Generate initial map
    matrix = get_map()  # Returns (ny, nx, 3) array
    ny, nx = matrix.shape[0], matrix.shape[1]

    # Create tiles from matrix
    tiles = []
    for i in range(ny):
        for j in range(nx):
            if matrix[i, j, 0] == 1:  # Island mask
                tile = Tile(
                    grid_i=i,
                    grid_j=j,
                    zone_id=1,  # TODO: Determine from location
                    type="empty",
                    owner=None,
                    temperature=matrix[i, j, 2],
                    humidity=matrix[i, j, 1]
                )
                tiles.append(tile)

    # PATTERN: Add all objects then commit once
    db.add(game_state)
    db.add(player)
    db.add_all(tiles)
    db.commit()

def get_current_game_state(db: Session) -> GameStateResponse:
    """Retrieve complete game state"""
    # PATTERN: Query all entities
    game_state = db.query(GameState).first()
    player = db.query(Player).first()
    tiles = db.query(Tile).all()

    # Calculate tiles_owned
    tiles_owned = [t.id for t in tiles if t.owner == "player"]

    # PATTERN: Use Pydantic from_attributes for ORM conversion
    player_response = PlayerResponse(
        shovels=player.shovels,
        drops=player.drops,
        score=player.score,
        tiles_owned=tiles_owned
    )

    tile_responses = [TileResponse.model_validate(t) for t in tiles]

    return GameStateResponse(
        step=game_state.current_step,
        max_steps=game_state.max_steps,
        is_game_over=game_state.is_game_over,
        player=player_response,
        tiles=tile_responses
    )
```

#### Task 4: Adjacency Logic
```python
# Backend/game/adjacency.py

from typing import List, Tuple
from sqlalchemy.orm import Session
from Backend.database.models import Tile

def get_neighbors(grid_i: int, grid_j: int, ny: int, nx: int) -> List[Tuple[int, int]]:
    """Get 8-neighbor coordinates with boundary checking"""
    # PATTERN: 8-direction offsets
    offsets = [
        (-1, -1), (-1, 0), (-1, 1),  # Top row
        (0, -1),           (0, 1),    # Middle row
        (1, -1),  (1, 0),  (1, 1)     # Bottom row
    ]

    neighbors = []
    for di, dj in offsets:
        ni, nj = grid_i + di, grid_j + dj
        # CRITICAL: Check boundaries
        if 0 <= ni < ny and 0 <= nj < nx:
            neighbors.append((ni, nj))

    return neighbors

def get_adjacent_tiles(tile: Tile, db: Session) -> List[Tile]:
    """Get all adjacent tiles from database"""
    # GOTCHA: Need to know grid dimensions
    # Get from game state or calculate from all tiles
    max_i = db.query(Tile.grid_i).order_by(Tile.grid_i.desc()).first()[0]
    max_j = db.query(Tile.grid_j).order_by(Tile.grid_j.desc()).first()[0]
    ny, nx = max_i + 1, max_j + 1

    neighbor_coords = get_neighbors(tile.grid_i, tile.grid_j, ny, nx)

    # PATTERN: Query with OR filters for coordinates
    adjacent_tiles = []
    for ni, nj in neighbor_coords:
        neighbor = db.query(Tile).filter(
            Tile.grid_i == ni,
            Tile.grid_j == nj
        ).first()
        if neighbor:
            adjacent_tiles.append(neighbor)

    return adjacent_tiles
```

#### Task 8: Turn Progression
```python
# Backend/game/state.py (extend)

def advance_to_next_step(db: Session) -> dict:
    """Progress game to next turn with all mechanics"""
    game_state = db.query(GameState).first()
    player = db.query(Player).first()

    # Increment step
    game_state.current_step += 1

    # Check game over
    if game_state.current_step >= game_state.max_steps:
        game_state.is_game_over = True
        db.commit()
        return {"message": "Game Over", "final_score": player.score}

    # Load new weather data
    # TODO: Implement load_next_step_data(game_state.current_step)
    # Update tile temperatures and humidities

    # Reset irrigation flags (start of turn)
    from Backend.game.mechanics import reset_irrigation_flags
    reset_irrigation_flags(db)

    # Apply water reserve auto-irrigation
    from Backend.game.mechanics import apply_water_reserve_auto_irrigation
    auto_irrigated = apply_water_reserve_auto_irrigation(db, game_state.current_step)

    # Check crop deaths
    from Backend.game.mechanics import check_crop_death
    tiles = db.query(Tile).filter(Tile.tile_state.isnot(None)).all()
    crops_died = 0
    for tile in tiles:
        if check_crop_death(tile, game_state.current_step, db):
            crops_died += 1

    # Advance crop states
    from Backend.game.mechanics import advance_crop_state
    for tile in db.query(Tile).filter(Tile.tile_state.isnot(None)).all():
        advance_crop_state(tile, db)

    # Generate resources
    player.drops += 1  # Base resource generation

    # PATTERN: Commit all changes together
    db.commit()

    return {
        "step": game_state.current_step,
        "auto_irrigated_tiles": auto_irrigated,
        "crops_died": crops_died,
        "player_resources": {
            "shovels": player.shovels,
            "drops": player.drops,
            "score": player.score
        }
    }
```

### Integration Points
```yaml
DATABASE:
  - file: farm_it.db (SQLite)
  - tables: game_state, player, tiles
  - initialization: On app startup via @app.on_event("startup")

CONFIG:
  - file: .env (optional, for future deployment)
  - variables: DATABASE_URL, MAX_STEPS, INITIAL_RESOURCES

ROUTES:
  - file: Backend/main.py
  - pattern: app.include_router(router, prefix="/game", tags=["game"])
  - existing: Keep /get_map for frontend compatibility

FRONTEND:
  - endpoint: GET /game/map (returns matrix data)
  - format: { status, shape, data, layers }
  - compatibility: Must match existing useMatrixData.js expectations
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# CRITICAL: Install ruff first
pip install ruff mypy

# Run linting on new files
ruff check Backend/database/ Backend/game/ Backend/routers/ --fix
ruff check Backend/tests/ --fix

# Type checking (if using type hints)
mypy Backend/database/
mypy Backend/game/
mypy Backend/routers/

# Expected: No errors. If errors, READ and fix before proceeding.
```

### Level 2: Unit Tests
```python
# CREATE Backend/tests/test_game_state.py
import pytest
from Backend.game.state import initialize_game, get_current_game_state
from Backend.database.models import GameState, Player, Tile

def test_initialize_game(test_db):
    """Test game initialization creates all entities"""
    initialize_game(test_db)

    game_state = test_db.query(GameState).first()
    assert game_state is not None
    assert game_state.current_step == 0

    player = test_db.query(Player).first()
    assert player.shovels == 3
    assert player.drops == 3

    tiles = test_db.query(Tile).all()
    assert len(tiles) > 0

def test_get_current_game_state(test_db, sample_game_state):
    """Test retrieving game state returns correct schema"""
    state = get_current_game_state(test_db)

    assert state.step >= 0
    assert state.player.shovels >= 0
    assert len(state.tiles) > 0

# CREATE Backend/tests/test_actions.py
def test_buy_tile_success(test_db, sample_game_state):
    """Test buying a tile decrements shovels"""
    from Backend.game.actions import buy_tile

    player = test_db.query(Player).first()
    tile = test_db.query(Tile).filter(Tile.owner.is_(None)).first()

    initial_shovels = player.shovels
    result = buy_tile(tile.id, player, test_db)

    assert player.shovels == initial_shovels - 1
    assert tile.owner == "player"
    assert result["success"] is True

def test_buy_tile_insufficient_resources(test_db, sample_game_state):
    """Test buying tile without shovels raises error"""
    from Backend.game.actions import buy_tile
    from Backend.game.exceptions import InsufficientResourcesError

    player = test_db.query(Player).first()
    player.shovels = 0
    test_db.commit()

    tile = test_db.query(Tile).filter(Tile.owner.is_(None)).first()

    with pytest.raises(InsufficientResourcesError):
        buy_tile(tile.id, player, test_db)
```

```bash
# Run tests
pytest Backend/tests/ -v --cov=Backend/game --cov=Backend/database

# Expected: All tests pass, coverage >80%
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the service
cd Backend
python main.py &

# Wait for startup
sleep 2

# Test full game flow
echo "=== Starting new game ==="
curl -X POST http://localhost:8000/game/start

echo "=== Getting initial state ==="
curl http://localhost:8000/game/state | jq '.player'

echo "=== Buying a tile ==="
curl -X POST http://localhost:8000/tile/1/buy

echo "=== Planting a crop ==="
curl -X POST http://localhost:8000/tile/1/plant \
  -H "Content-Type: application/json" \
  -d '{"action": "plant", "crop_type": "wheat"}'

echo "=== Advancing turn ==="
curl -X POST http://localhost:8000/game/next-step

echo "=== Checking crop state ==="
curl http://localhost:8000/game/state | jq '.tiles[] | select(.id == 1)'

# Expected outputs:
# - Start: {"message": "Game started"}
# - State: {"shovels": 3, "drops": 3, "score": 0, ...}
# - Buy: {"success": true, ...}
# - Plant: {"success": true, ...}
# - Next step: {"step": 1, "crops_died": 0, ...}
# - Crop state: {"tile_state": "growing", ...}

# Cleanup
pkill -f "python main.py"
```

## Final Validation Checklist
- [ ] All tests pass: `pytest Backend/tests/ -v`
- [ ] No linting errors: `ruff check Backend/`
- [ ] No type errors: `mypy Backend/`
- [ ] Manual integration test successful (curl commands above)
- [ ] Game state persists: Stop server, restart, state unchanged
- [ ] Turn progression works: Crops advance from seed → growing → harvest
- [ ] Irrigation prevents death: Irrigated crops survive low humidity
- [ ] Water reserves auto-irrigate: Adjacent tiles get irrigated
- [ ] Harvest generates resources: Score and shovels increase
- [ ] Game ends properly: Reaches max_steps and sets is_game_over
- [ ] API compatible with frontend: /game/map returns expected format
- [ ] Error handling works: Invalid actions return proper HTTP codes
- [ ] Documentation clear: Swagger UI at /docs is complete

---

## Anti-Patterns to Avoid
- ❌ Don't store game state in memory (class variables) - use database
- ❌ Don't forget check_same_thread=False for SQLite
- ❌ Don't use Pydantic v1 syntax (dict() → model_dump())
- ❌ Don't skip boundary checks in adjacency logic
- ❌ Don't mutate state without db.commit()
- ❌ Don't forget to reset irrigation flags each turn
- ❌ Don't return NumPy arrays in JSON (use .tolist())
- ❌ Don't ignore error cases in tests - test failure paths
- ❌ Don't hard-code grid dimensions - derive from data
- ❌ Don't skip validation in API endpoints

## PRP Quality Score: 9/10

**Confidence Level**: High confidence for one-pass implementation

**Strengths**:
- Comprehensive task breakdown with clear dependencies
- Extensive context including existing code patterns
- Detailed pseudocode for critical functions
- Validation loops at multiple levels (syntax, unit, integration)
- Addresses common pitfalls (SQLite threading, Pydantic v2, etc.)
- Clear integration with existing frontend

**Potential Challenges**:
- Weather data integration may need adjustment based on actual data format
- Zone ID assignment logic needs clarification (climate zone mapping)
- May need fine-tuning of game balance (resource costs, rewards)

**Missing** (-1 point):
- Specific thresholds for crop death (humidity levels per zone)
- Exact mapping of locations to zone_ids (cold/arid/tropical/temperate)
- Performance considerations for large grids (N x M > 10,000 tiles)

These can be addressed during implementation with reasonable assumptions or by consulting INITIAL.md for game balance.
