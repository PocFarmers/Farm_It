name: "Farm It - Turn-Based Farming Game Implementation"
description: |

## Purpose
Implement a complete turn-based farming game with resource management, crop cycles, tile ownership, and spatial effects. Transform the current matrix visualization into an interactive game where players manage a farm over 50 steps (1 year).

## Core Principles
1. **Single-Player Local**: No multiplayer, simpler state management
2. **Auto-Save**: Persist game state after each action/step
3. **Spatial Logic**: 8-neighbor adjacency for effects (water reserves, forests)
4. **Progressive Gameplay**: Turn-based with no failure state, just optimization
5. **Data-Driven**: Temperature/humidity from existing layers affect gameplay

---

## Goal
Build a complete farming simulation game where:
- Players start with 3 owned empty tiles and basic resources
- Each game lasts 50 steps (50 turns = 1 year)
- Players buy tiles, plant crops, manage irrigation and resources
- Crops follow a cycle: seed → growing → harvest (4 steps each phase)
- Forests and water reserves provide local effects to adjacent tiles
- Game state persists in SQLite database with auto-save

## Why
- **Player Engagement**: Transform static visualization into interactive game
- **Resource Management**: Strategic decisions about shovels, drops, and tile investments
- **Spatial Strategy**: Adjacency effects create interesting tactical choices
- **Replayability**: Random island generation + optimization goals = high replay value
- **Learning Tool**: Demonstrates real temperature/humidity data in game mechanics

## What
A complete turn-based farming game with:

**Core Gameplay:**
- 50x50 grid map with zones (cold, arid, tropical, temperate)
- Resources: shovels (building), drops (irrigation), score (points)
- Tile types: empty, field (with crop states), forest (conserved/exploited)
- Actions: buy tiles, plant, irrigate, buy water reserve/firebreak, fertilize
- Each step: resources increment, crops advance, effects apply, auto-save

**User Interface:**
- Map view with tile visualization (color-coded by state)
- Resource panel (top-right): shovels, drops, score
- Game stats (right-center): step count, tile counts, crop breakdown
- Tile interaction: click to select, show popup with actions
- "Next Step" button to advance game

**Backend:**
- FastAPI + SQLAlchemy + SQLite
- Game state persistence (player, tiles, current step)
- Game logic engine (crop cycles, effects, irrigation checks)
- RESTful endpoints for game operations

### Success Criteria
- [ ] Game initializes with 3 owned empty tiles, starting resources
- [ ] Players can buy tiles, plant crops, and perform all 6 actions
- [ ] Crop cycle advances correctly (seed→growing→harvest every 4 steps)
- [ ] Irrigation mechanic works (crops die if not irrigated)
- [ ] Water reserves auto-irrigate adjacent tiles
- [ ] Conserved forests fertilize adjacent fields
- [ ] "Next Step" increments resources and advances game state
- [ ] Game state saves/loads from database
- [ ] UI shows resources, stats, and tile details
- [ ] Game completes after 50 steps with final score

## All Needed Context

### Documentation & References
```yaml
# Backend - FastAPI + SQLAlchemy
- url: https://fastapi.tiangolo.com/tutorial/sql-databases/
  why: SQLAlchemy integration patterns, dependency injection
  critical: Use get_db() dependency for session management

- url: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
  why: SQLAlchemy 2.0 ORM basics, model definitions
  section: Defining Table Metadata, Working with Data

- pattern: State Pattern for Game Logic
  url: https://gameprogrammingpatterns.com/state.html
  why: Managing crop states and game phases
  critical: Use enum for states, finite state machine for transitions

- file: Backend/main.py
  why: Existing FastAPI app structure, CORS config, endpoint patterns
  critical: Follow same async endpoint pattern, error handling

- file: Backend/get_map/get_map.py
  why: Current map generation with temperature/humidity layers
  critical: Tiles read temp/humidity from existing matrix data

# Frontend - React Game UI
- file: frontend/src/components/MatrixGrid.jsx
  why: Existing grid display with zoom/pan
  critical: Extend with tile selection and action UI

- pattern: Tile Selection in React
  url: https://medium.com/@tylercmasterson/board-game-logic-in-react-199d6983fc23
  why: Board game tile selection patterns
  critical: Use selectedTile state, highlight selected, show context actions

# Game Design Patterns
- url: https://gamedev.stackexchange.com/questions/82082/how-should-i-structure-the-implementation-of-turn-based-board-game-rules
  why: Turn-based game rule implementation
  critical: Separate game logic from UI, validate actions before applying

# Database Design
- url: https://stackoverflow.com/questions/8934681/database-design-for-turn-based-game
  why: Turn-based game state storage patterns
  critical: Store current game state + history for statistics
```

### Current Codebase Tree
```bash
.
├── Backend/
│   ├── get_map/
│   │   ├── get_map.py              # Map generation (50x50 grid)
│   │   ├── get_history_info.py     # Weather data fetch
│   │   └── download_files.py
│   ├── in_game/
│   │   └── get_event.py           # Event determination
│   ├── main.py                     # FastAPI app (needs game endpoints)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── MatrixGrid.jsx     # Grid display with zoom/pan
│   │   │   ├── MatrixCell.jsx     # Individual cell render
│   │   │   └── LoadingState.jsx
│   │   ├── hooks/
│   │   │   └── useMatrixData.js   # API data fetching
│   │   ├── index.css
│   │   └── main.jsx
│   └── package.json
└── INITAL.md                       # Complete game spec
```

### Desired Codebase Tree
```bash
.
├── Backend/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                  # SQLAlchemy setup, get_db()
│   │   └── models.py              # ORM models (GameState, Player, Tile)
│   ├── game/
│   │   ├── __init__.py
│   │   ├── schemas.py             # Pydantic models for API
│   │   ├── game_logic.py          # Core game engine (crop cycles, effects)
│   │   ├── actions.py             # Player actions (buy, plant, irrigate)
│   │   └── utils.py               # Adjacency calc, zone logic
│   ├── routers/
│   │   ├── __init__.py
│   │   └── game.py                # Game endpoints router
│   ├── main.py                    # Updated with game routes
│   └── requirements.txt           # Add: sqlalchemy, alembic
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Game/
│   │   │   │   ├── GameBoard.jsx        # Main game view
│   │   │   │   ├── TileCell.jsx         # Interactive tile
│   │   │   │   ├── TilePopup.jsx        # Action popup
│   │   │   │   ├── ResourcePanel.jsx    # Top-right resources
│   │   │   │   ├── GameStats.jsx        # Right stats panel
│   │   │   │   └── NextStepButton.jsx   # Step advance
│   │   ├── hooks/
│   │   │   ├── useGameState.js    # Game state management
│   │   │   └── useGameActions.js  # Action API calls
│   │   └── types/                 # TypeScript/PropTypes
│   └── ...

Responsibility:
- database/: SQLAlchemy setup, ORM models
- game/: Game logic, actions, calculations
- routers/game.py: API endpoints for game operations
- frontend/Game/: Game UI components
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: FastAPI + SQLAlchemy Session Management
# Use dependency injection for db sessions
# NEVER create session manually in endpoints
# Pattern: db: Session = Depends(get_db)

# CRITICAL: Pydantic v2 Compatibility
# requirements.txt has pydantic==2.5.0
# Use: model_validate() not parse_obj()
# Use: model_dump() not dict()

# CRITICAL: Crop State Machine
# seed → growing → harvest (changes every 4 steps)
# Death condition: if not irrigated AND no adjacent water reserve
# Check irrigation BEFORE advancing state

# CRITICAL: Adjacency Logic (8-neighbor)
# For tile at (i,j), neighbors are:
# (i-1,j-1), (i-1,j), (i-1,j+1),
# (i,j-1),            (i,j+1),
# (i+1,j-1), (i+1,j), (i+1,j+1)
# Handle edge cases (grid boundaries)

# CRITICAL: Zone Assignment
# Use existing zoneId from map generation
# Zones affect crop viability (future feature hook)

# GOTCHA: Numpy Array to DB
# Matrix from get_map() is numpy, convert to Python types
# Use .tolist() or float()/int() before DB storage

# GOTCHA: React State Updates
# Tile selection must trigger UI update
# Use useState for selectedTile
# Re-render action popup when selection changes
```

## Implementation Blueprint

### Data Models and Structure

**Database Models (SQLAlchemy ORM):**
```python
# database/models.py

class GameState(Base):
    __tablename__ = "game_state"

    id: int = Column(Integer, primary_key=True, index=True)
    current_step: int = Column(Integer, default=0)
    is_completed: bool = Column(Boolean, default=False)
    created_at: datetime
    updated_at: datetime

    # Relationships
    player: Mapped["Player"] = relationship(back_populates="game")
    tiles: Mapped[List["Tile"]] = relationship(back_populates="game")

class Player(Base):
    __tablename__ = "players"

    id: int = Column(Integer, primary_key=True, index=True)
    game_id: int = Column(Integer, ForeignKey("game_state.id"))
    shovels: int = Column(Integer, default=3)  # Start with 3
    drops: int = Column(Integer, default=3)
    score: int = Column(Integer, default=0)

    game: Mapped["GameState"] = relationship(back_populates="player")

class Tile(Base):
    __tablename__ = "tiles"

    id: int = Column(Integer, primary_key=True, index=True)
    game_id: int = Column(Integer, ForeignKey("game_state.id"), index=True)
    grid_index: int = Column(Integer, index=True)  # 0-2499 for 50x50
    row: int = Column(Integer)
    col: int = Column(Integer)

    # Tile properties
    zone_id: int = Column(Integer)  # 1=cold, 2=arid, 3=tropical, 4=temperate
    tile_type: str = Column(String)  # "forest" | "field" | "empty"
    owner: str = Column(String, nullable=True)  # null | "player"

    # Field-specific (only when type="field")
    tile_state: str = Column(String, nullable=True)  # "seed" | "growing" | "harvest"
    state_step_count: int = Column(Integer, default=0)  # Steps in current state

    # Forest-specific
    exploited: str = Column(String, nullable=True)  # "conserve" | "exploit"

    # Upgrades
    has_water_reserve: bool = Column(Boolean, default=False)
    has_firebreak: bool = Column(Boolean, default=False)

    # Environmental data
    temperature: float = Column(Float)
    humidity: float = Column(Float)

    # Irrigation tracking
    last_irrigated_step: int = Column(Integer, default=-1)
    irrigated_this_step: bool = Column(Boolean, default=False)

    game: Mapped["GameState"] = relationship(back_populates="tiles")

    @property
    def position(self):
        return (self.row, self.col)
```

**Pydantic Schemas (API):**
```python
# game/schemas.py

class TileResponse(BaseModel):
    id: int
    grid_index: int
    row: int
    col: int
    zone_id: int
    tile_type: str
    owner: str | None
    tile_state: str | None
    has_water_reserve: bool
    has_firebreak: bool
    temperature: float
    humidity: float

    model_config = ConfigDict(from_attributes=True)

class PlayerResponse(BaseModel):
    shovels: int
    drops: int
    score: int

class GameStateResponse(BaseModel):
    step: int
    player: PlayerResponse
    tiles: List[TileResponse]
    is_completed: bool

class TileActionRequest(BaseModel):
    action: str  # "buy", "plant", "irrigate", "buy_water", "buy_firebreak", "fertilize"
    tile_id: int
```

### List of Tasks to Complete

```yaml
Task 1: Setup Database Infrastructure
  CREATE Backend/database/__init__.py
  CREATE Backend/database/db.py:
    - Setup SQLAlchemy engine (SQLite: farmit.db)
    - Create SessionLocal factory
    - Implement get_db() dependency
    - Add Base = declarative_base()

  CREATE Backend/database/models.py:
    - Define GameState, Player, Tile models (as shown above)
    - Add relationships and indexes
    - Include __repr__ for debugging

  CREATE Backend/alembic/ (optional but recommended):
    - Initialize alembic for migrations
    - Create initial migration

Task 2: Implement Core Game Logic
  CREATE Backend/game/__init__.py

  CREATE Backend/game/utils.py:
    - get_neighbors(row, col, grid_size=50) -> List[Tuple[int,int]]
      Returns 8-neighbor coordinates, handling boundaries
    - assign_zone_from_position(row, col) -> int
      Determine zone based on position (use simple quadrant logic)
    - check_crop_viability(temperature, humidity, zone_id) -> bool
      Future hook for crop death from environmental factors

  CREATE Backend/game/game_logic.py:
    - initialize_game(db: Session) -> GameState
      Create new game: 1 player, 50x50 tiles (3 owned empty)
      Load temp/humidity from get_map()

    - advance_step(db: Session, game_id: int) -> GameState
      1. Increment step counter
      2. Update player resources (+1 shovel, +1 drop, +10 score)
      3. Process crop cycles (advance states, check deaths)
      4. Apply water reserve effects (auto-irrigate neighbors)
      5. Apply forest effects (fertilizer to neighbors)
      6. Reset irrigated_this_step flags
      7. Auto-save

    - process_crop_cycle(db: Session, game: GameState):
      For each field tile:
        - Increment state_step_count
        - If state_step_count == 4: transition state
        - Check irrigation: if not irrigated → crop dies (type="empty")

    - apply_water_effects(db: Session, game: GameState):
      For each tile with has_water_reserve:
        - Get neighbors
        - For each neighbor field: set irrigated_this_step=True

    - apply_forest_effects(db: Session, game: GameState):
      For each conserved forest:
        - Get neighbors
        - For each neighbor field: apply +1 fertilizer (future: growth boost)

Task 3: Implement Player Actions
  CREATE Backend/game/actions.py:
    - buy_tile(db, game_id, tile_id) -> Tile
      Cost: 2 shovels
      Effect: owner = "player"
      Validation: tile not owned, player has resources

    - plant_seed(db, game_id, tile_id) -> Tile
      Effect: type="field", tile_state="seed", state_step_count=0
      Validation: tile owned, type="empty"

    - manual_irrigate(db, game_id, tile_id) -> Tile
      Cost: 1 drop
      Effect: irrigated_this_step=True, last_irrigated_step=current_step
      Validation: type="field", player has drops

    - buy_water_reserve(db, game_id, tile_id) -> Tile
      Cost: 3 shovels
      Effect: has_water_reserve=True

    - buy_firebreak(db, game_id, tile_id) -> Tile
      Cost: 3 shovels
      Effect: has_firebreak=True

    - apply_fertilizer(db, game_id, tile_id) -> Tile
      Cost: 1 shovel
      Effect: boost growth (future: reduce state_step_count)

  All actions:
    - Validate resources before deducting
    - Update player resources in same transaction
    - Return updated tile

Task 4: Create Game API Endpoints
  CREATE Backend/routers/__init__.py

  CREATE Backend/routers/game.py:
    - GET /game/new -> GameStateResponse
      Creates new game, returns initial state

    - GET /game/load/{game_id} -> GameStateResponse
      Loads existing game by ID

    - GET /game/current -> GameStateResponse
      Loads most recent game (latest ID)

    - POST /game/{game_id}/save -> GameStateResponse
      Explicit save (auto-save happens on actions)

    - POST /game/{game_id}/next-step -> GameStateResponse
      Calls advance_step(), returns updated state

    - POST /game/{game_id}/tile/{tile_id}/action -> TileResponse
      Body: { "action": "buy" | "plant" | "irrigate" | ... }
      Executes action, returns updated tile

  MODIFY Backend/main.py:
    - Import game router
    - Add: app.include_router(game_router, prefix="/game", tags=["game"])
    - Update requirements.txt: sqlalchemy, alembic (if used)

Task 5: Initialize Database on Startup
  MODIFY Backend/main.py:
    - Add startup event handler
    - Create tables: Base.metadata.create_all(bind=engine)
    - Optionally create default game for testing

Task 6: Frontend - Game State Hook
  CREATE frontend/src/hooks/useGameState.js:
    - Fetch game state from /game/current or /game/new
    - Poll for updates (optional) or manual refresh
    - Manage loading/error states
    - Return: { gameState, loading, error, refetch }

Task 7: Frontend - Game Action Hook
  CREATE frontend/src/hooks/useGameActions.js:
    - nextStep() -> POST /game/{id}/next-step
    - performAction(tileId, action) -> POST /game/{id}/tile/{tileId}/action
    - Handle optimistic updates (optional)
    - Return: { nextStep, performAction, loading }

Task 8: Frontend - Resource Panel Component
  CREATE frontend/src/components/Game/ResourcePanel.jsx:
    - Display: shovels (🔨), drops (💧), score (⭐)
    - Show current step / 50
    - Use icons + numbers
    - Position: top-right, fixed or absolute

Task 9: Frontend - Game Stats Component
  CREATE frontend/src/components/Game/GameStats.jsx:
    - Calculate from gameState.tiles:
      - # owned tiles
      - # fields (seed/growing/harvest breakdown)
      - # forests (conserved vs exploited)
    - Display in right-center panel
    - Update when gameState changes

Task 10: Frontend - Tile Cell Component
  MODIFY frontend/src/components/MatrixCell.jsx -> TileCell.jsx:
    - Accept: tile data, isSelected, onClick
    - Color by state:
      - empty: gray
      - field+seed: light green
      - field+growing: medium green
      - field+harvest: gold
      - forest: dark green
      - owned: add border highlight
    - Show icons: 💧 (water reserve), 🛡️ (firebreak)
    - On click: call onClick(tile)

Task 11: Frontend - Tile Popup Component
  CREATE frontend/src/components/Game/TilePopup.jsx:
    - Props: selectedTile, playerResources, onAction, onClose
    - Display tile info: temperature, humidity, zone, type, state
    - Action buttons (conditional on tile state):
      - Buy Tile (if not owned, 2 shovels)
      - Plant Seed (if owned, empty)
      - Irrigate (if field, 1 drop)
      - Buy Water Reserve (3 shovels)
      - Buy Firebreak (3 shovels)
      - Fertilize (1 shovel)
    - Disable buttons if insufficient resources
    - On action: call onAction(action), close popup

Task 12: Frontend - Game Board Component
  CREATE frontend/src/components/Game/GameBoard.jsx:
    - Use existing MatrixGrid as base
    - Add tile selection state: selectedTile
    - Render TileCell for each tile (not MatrixCell)
    - Show TilePopup when tile selected
    - Pass gameState to children

Task 13: Frontend - Next Step Button
  CREATE frontend/src/components/Game/NextStepButton.jsx:
    - Button: "Next Step (Day {step*8})"
    - On click: call nextStep()
    - Show loading state during API call
    - Position: bottom-right, prominent

Task 14: Frontend - Main Game View
  MODIFY frontend/src/App.jsx:
    - Import useGameState, useGameActions
    - Fetch initial game state
    - Render layout:
      - <ResourcePanel /> (top-right)
      - <GameStats /> (right-center)
      - <GameBoard /> (main area, 3/4 width)
      - <NextStepButton /> (bottom-right)
    - Handle game completion (step == 50)

Task 15: Integration & Testing
  - Test game initialization
  - Test all 6 actions (buy, plant, irrigate, etc.)
  - Test step advancement (resources, crop cycles)
  - Test adjacency effects (water, forest)
  - Test crop death from no irrigation
  - Test game save/load
  - Test UI updates on actions
  - Verify 50-step game completion
```

### Pseudocode for Critical Functions

```python
# game/game_logic.py

def initialize_game(db: Session) -> GameState:
    """Create new game with starting conditions"""
    # 1. Create game state
    game = GameState(current_step=0, is_completed=False)
    db.add(game)
    db.flush()  # Get game.id

    # 2. Create player with starting resources
    player = Player(
        game_id=game.id,
        shovels=3,
        drops=3,
        score=0
    )
    db.add(player)

    # 3. Generate map data (50x50)
    map_data = get_map()  # Returns 50x50x3 matrix

    # 4. Create tiles
    owned_indices = random.sample(range(2500), 3)  # 3 random owned tiles

    for i in range(50):
        for j in range(50):
            grid_index = i * 50 + j

            # Extract environmental data
            mask = map_data[i,j,0]
            humidity = float(map_data[i,j,1])
            temperature = float(map_data[i,j,2])

            # Determine tile type
            if mask == 0:
                tile_type = "empty"  # Water/unusable
                owner = None
            else:
                tile_type = "empty" if grid_index in owned_indices else "empty"
                owner = "player" if grid_index in owned_indices else None

            # Assign zone (simple quadrant logic)
            zone_id = assign_zone_from_position(i, j)

            tile = Tile(
                game_id=game.id,
                grid_index=grid_index,
                row=i,
                col=j,
                zone_id=zone_id,
                tile_type=tile_type,
                owner=owner,
                temperature=temperature,
                humidity=humidity
            )
            db.add(tile)

    db.commit()
    db.refresh(game)
    return game

def advance_step(db: Session, game_id: int) -> GameState:
    """Advance game by one step (8 days)"""
    game = db.query(GameState).filter(GameState.id == game_id).first()
    if not game or game.is_completed:
        raise ValueError("Game not found or already completed")

    # 1. Increment step
    game.current_step += 1

    # 2. Update player resources
    player = game.player
    player.shovels += 1
    player.drops += 1
    player.score += 10

    # 3. Apply water reserve effects (BEFORE crop processing)
    apply_water_effects(db, game)

    # 4. Process crop cycles
    process_crop_cycle(db, game)

    # 5. Apply forest effects
    apply_forest_effects(db, game)

    # 6. Reset irrigation flags for next step
    for tile in game.tiles:
        tile.irrigated_this_step = False

    # 7. Check completion
    if game.current_step >= 50:
        game.is_completed = True

    db.commit()
    db.refresh(game)
    return game

def process_crop_cycle(db: Session, game: GameState):
    """Advance crop states, check deaths"""
    for tile in game.tiles:
        if tile.tile_type != "field":
            continue

        # Check irrigation requirement
        needs_irrigation = tile.tile_state in ["seed", "growing"]
        has_irrigation = (
            tile.irrigated_this_step or
            tile_has_adjacent_water_reserve(db, tile)
        )

        if needs_irrigation and not has_irrigation:
            # Crop dies
            tile.tile_type = "empty"
            tile.tile_state = None
            tile.state_step_count = 0
            continue

        # Advance crop state
        tile.state_step_count += 1

        if tile.state_step_count >= 4:
            # Transition state
            if tile.tile_state == "seed":
                tile.tile_state = "growing"
                tile.state_step_count = 0
            elif tile.tile_state == "growing":
                tile.tile_state = "harvest"
                tile.state_step_count = 0
            elif tile.tile_state == "harvest":
                # Harvest complete: reward player
                game.player.shovels += 2  # Harvest reward
                game.player.score += 20
                tile.tile_type = "empty"  # Reset to empty
                tile.tile_state = None
                tile.state_step_count = 0

def tile_has_adjacent_water_reserve(db: Session, tile: Tile) -> bool:
    """Check if any neighbor has water reserve"""
    neighbors = get_neighbors(tile.row, tile.col, grid_size=50)

    for nr, nc in neighbors:
        neighbor_index = nr * 50 + nc
        neighbor = db.query(Tile).filter(
            Tile.game_id == tile.game_id,
            Tile.grid_index == neighbor_index
        ).first()

        if neighbor and neighbor.has_water_reserve:
            return True

    return False

# game/actions.py

def buy_tile(db: Session, game_id: int, tile_id: int) -> Tile:
    """Buy an unowned tile"""
    game = db.query(GameState).filter(GameState.id == game_id).first()
    player = game.player
    tile = db.query(Tile).filter(Tile.id == tile_id).first()

    # Validate
    if tile.owner is not None:
        raise ValueError("Tile already owned")
    if player.shovels < 2:
        raise ValueError("Insufficient shovels")

    # Apply action
    player.shovels -= 2
    tile.owner = "player"

    db.commit()
    db.refresh(tile)
    return tile

def plant_seed(db: Session, game_id: int, tile_id: int) -> Tile:
    """Plant a seed on owned empty tile"""
    tile = db.query(Tile).filter(Tile.id == tile_id).first()

    # Validate
    if tile.owner != "player":
        raise ValueError("Tile not owned")
    if tile.tile_type != "empty":
        raise ValueError("Tile not empty")

    # Apply
    tile.tile_type = "field"
    tile.tile_state = "seed"
    tile.state_step_count = 0

    db.commit()
    db.refresh(tile)
    return tile
```

### Integration Points
```yaml
DATABASE:
  - file: Backend/database/db.py
  - engine: SQLite (farmit.db)
  - setup: Create tables on startup (main.py)
  - pattern: Dependency injection (get_db)

EXISTING_ENDPOINTS:
  - Keep: /get_map (for initial tile data)
  - Keep: /get_event (future use)
  - Keep: /health
  - Add: /game/* (new router)

FRONTEND_STATE:
  - Global: gameState (from useGameState)
  - Local: selectedTile (in GameBoard)
  - Actions: useGameActions hook
  - Update pattern: refetch after action/step

MAP_INTEGRATION:
  - Use get_map() for initial tile temp/humidity
  - 50x50 grid matches current implementation
  - Zone assignment from position (quadrant logic)
```

## Validation Loop

### Level 1: Database Setup
```bash
# After Task 1-2, verify database
cd Backend
python -c "from database.db import engine; from database.models import Base; Base.metadata.create_all(bind=engine); print('Tables created')"

# Check tables exist
sqlite3 farmit.db ".tables"
# Expected: game_state, players, tiles

# Check schema
sqlite3 farmit.db ".schema tiles"
# Expected: All columns defined
```

### Level 2: Game Logic Unit Tests
```bash
# After Task 2-3, test core logic
cd Backend
pytest tests/test_game_logic.py -v

# Test cases:
# - test_initialize_game() -> creates 1 player, 2500 tiles, 3 owned
# - test_advance_step() -> increments resources, step counter
# - test_crop_cycle() -> seed->growing->harvest->empty
# - test_crop_death() -> no irrigation = death
# - test_water_reserve_effect() -> auto-irrigates neighbors
# - test_adjacency_calculation() -> 8-neighbor logic
```

### Level 3: API Integration Tests
```bash
# After Task 4-5, test endpoints
cd Backend
python -m uvicorn main:app --reload &

# Test game creation
curl http://localhost:8000/game/new
# Expected: GameStateResponse with step=0, player resources

# Test next step
curl -X POST http://localhost:8000/game/1/next-step
# Expected: step=1, resources incremented

# Test action
curl -X POST http://localhost:8000/game/1/tile/50/action \
  -H "Content-Type: application/json" \
  -d '{"action": "buy"}'
# Expected: Tile owned by player, shovels decreased

# Verify save/load
curl http://localhost:8000/game/current
# Expected: Persisted state matches
```

### Level 4: Frontend Integration
```bash
# After Task 6-14, test UI
cd frontend
npm run dev

# Manual checks:
# 1. Load game -> see 50x50 grid, resources panel
# 2. Click tile -> popup shows with actions
# 3. Buy tile -> resources update, tile changes color
# 4. Plant seed -> tile turns green
# 5. Click "Next Step" -> step increments, crops advance
# 6. Test crop death -> don't irrigate, crop dies after 4 steps
# 7. Play to step 50 -> game completion message

# Browser console checks:
# - No errors
# - Game state updates correctly
# - Actions reflect in UI immediately
```

## Final Validation Checklist
- [ ] Database tables created with correct schema
- [ ] Game initializes with 3 owned tiles, starting resources
- [ ] All 6 player actions work (buy, plant, irrigate, water, firebreak, fertilize)
- [ ] Crop cycle advances correctly (4 steps per state)
- [ ] Crops die without irrigation
- [ ] Water reserves auto-irrigate neighbors
- [ ] Forests apply effects to neighbors (conserved mode)
- [ ] Next step increments resources and game state
- [ ] Game state persists in database
- [ ] UI shows resources, stats, and tile states
- [ ] Tile selection and popup work correctly
- [ ] Game completes after 50 steps
- [ ] No console errors in frontend
- [ ] Backend tests pass: `pytest tests/ -v`
- [ ] Integration tests pass (manual curl/UI checks)

---

## Anti-Patterns to Avoid
- ❌ Don't create session manually - use get_db() dependency
- ❌ Don't forget to commit transactions after actions
- ❌ Don't skip irrigation check before advancing crop state
- ❌ Don't hardcode grid size - use constant (50)
- ❌ Don't mutate gameState directly in React - use setState
- ❌ Don't forget to refresh game state after actions
- ❌ Don't allow actions without resource validation
- ❌ Don't skip boundary checks in adjacency calculation
- ❌ Don't forget to convert numpy types to Python types for DB
- ❌ Don't create duplicate game instances - check for existing

## Confidence Score
**8/10** - High confidence for one-pass implementation

**Reasoning:**
- ✅ Clear game mechanics and data models
- ✅ Existing backend/frontend structure to build on
- ✅ Well-researched patterns (State Pattern, SQLAlchemy best practices)
- ✅ Comprehensive task breakdown with pseudocode
- ✅ Validation checkpoints at each stage
- ⚠️ Minor risk: Adjacency logic edge cases, crop state transitions
- ⚠️ Minor risk: Frontend state synchronization complexity

**Risk Mitigation:**
- Pseudocode provided for critical functions
- Test cases defined for edge cases
- Validation loops catch issues early
- Existing visualization code provides solid foundation
