name: "Farm It - Frontend-Backend Integration for Game UI"
description: |
  Connect the functional backend with the React frontend to create a complete playable game.
  Add game resource management, tile interactions, action buttons, and turn progression UI.

---

## Goal
Transform the existing matrix visualization into a fully playable farming game by:
- Integrating backend API endpoints for game state and player actions
- Adding game UI components (resources, stats, action modals)
- Implementing tile click interactions with action buttons
- Creating turn progression system with "Next Step" button
- Managing game state with React hooks and context

## Why
- **Business value**: Create a complete playable game from existing visualization
- **User experience**: Enable strategic gameplay with clear resource management and tile interactions
- **Integration**: Seamless connection between backend game logic and frontend UI
- **Problems solved**: Bridge visualization-only frontend to interactive game experience

## What
Add interactive game features to existing frontend:
- Resource display panel (shovels, drops, score) in top-right header
- Game stats panel showing step, tiles owned, crops, forests
- Tile click modal with tile details and action buttons
- Action handlers for buy, plant, irrigate, harvest, build structures
- Next Step button to progress game turns
- Game initialization and state synchronization

### Success Criteria
- [ ] Player can see current resources (shovels, drops, score) in UI
- [ ] Player can click tiles to see details and available actions
- [ ] Player can perform actions (buy, plant, irrigate, harvest) via UI
- [ ] Next Step button advances game and updates all UI elements
- [ ] Game state syncs with backend after each action
- [ ] Resource costs are validated and deducted properly
- [ ] Visual feedback for owned tiles, crop states, and structures
- [ ] Game Over screen displays when reaching max steps

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window

- file: INITAL.md
  why: Complete game specification with costs, rules, and UI requirements
  critical: Resource costs differ from backend (buy tile = 2 shovels, water reserve = 3 shovels)

- file: frontend/src/App.jsx
  why: Current app structure with header and MatrixGrid
  critical: Keep existing layout structure and Tailwind styling

- file: frontend/src/hooks/useMatrixData.js
  why: Pattern for API data fetching with React hooks
  critical: Use same pattern for game state fetching

- file: frontend/src/components/MatrixGrid.jsx
  why: Grid rendering with zoom/pan controls
  critical: Add onClick handler to cells, keep existing controls

- file: frontend/src/components/MatrixCell.jsx
  why: Cell rendering with tooltip
  critical: Add visual indicators for owned tiles, crops, structures

- file: Backend/routers/game.py
  why: Game API endpoints (start, state, next-step, map)
  critical: /game/state returns full game state with player and tiles

- file: Backend/routers/tile.py
  why: Tile action endpoints (buy, plant, irrigate, harvest, build)
  critical: All endpoints follow pattern: POST /tile/{id}/{action}

- url: https://react.dev/learn/managing-state
  why: React state management patterns
  critical: Use Context API for game state, avoid prop drilling

- url: https://react.dev/reference/react-dom/components/dialog
  why: Native HTML dialog element in React
  critical: Use <dialog> for tile action modal, better accessibility

- package: react-tooltip@5.29.1
  why: Already installed for tooltips
  critical: Keep for hover details, use dialog for actions

- pattern: Optimistic UI updates
  why: Better UX for action feedback
  source: https://www.patterns.dev/react/optimistic-ui
  critical: Show action result immediately, rollback if fails
```

### Current Codebase Tree
```bash
frontend/
├── src/
│   ├── App.jsx                # Main app with header, MatrixGrid
│   ├── main.jsx               # React entry point
│   ├── index.css              # Tailwind styles
│   ├── hooks/
│   │   └── useMatrixData.js   # Hook for fetching /get_map
│   └── components/
│       ├── LoadingState.jsx   # Loading spinner
│       ├── MatrixGrid.jsx     # Grid with zoom/pan, side panel
│       └── MatrixCell.jsx     # Individual cell with tooltip
├── package.json               # React 19, Tailwind 4, react-tooltip
└── vite.config.js             # Vite dev server config

Backend/
├── main.py                    # FastAPI app with CORS
├── routers/
│   ├── game.py               # /game/* endpoints
│   └── tile.py               # /tile/{id}/* endpoints
└── game/
    ├── state.py              # Game state management
    ├── actions.py            # Player actions
    ├── mechanics.py          # Crop lifecycle, irrigation
    └── schemas.py            # Pydantic response models
```

### Desired Codebase Tree with New Files
```bash
frontend/src/
├── App.jsx                           # [MODIFY] Add GameProvider wrapper
├── hooks/
│   ├── useMatrixData.js             # [KEEP] Existing matrix hook
│   ├── useGameState.js              # [CREATE] Hook for /game/state
│   └── useGameActions.js            # [CREATE] Hook for tile actions
├── components/
│   ├── MatrixGrid.jsx               # [MODIFY] Add onClick to cells
│   ├── MatrixCell.jsx               # [MODIFY] Visual indicators for tiles
│   ├── LoadingState.jsx             # [KEEP] Existing
│   ├── ResourceDisplay.jsx          # [CREATE] Shovels, drops, score display
│   ├── GameStatsPanel.jsx           # [CREATE] Step, tiles, crops stats
│   ├── TileActionModal.jsx          # [CREATE] Dialog with action buttons
│   ├── NextStepButton.jsx           # [CREATE] Turn progression button
│   └── GameOverScreen.jsx           # [CREATE] End game display
├── context/
│   └── GameContext.jsx              # [CREATE] Global game state
├── utils/
│   ├── api.js                       # [CREATE] API client functions
│   └── tileHelpers.js               # [CREATE] Tile color, icon helpers
└── constants/
    └── gameConfig.js                # [CREATE] Costs, colors, icons
```

### Known Gotchas & Library Quirks
```javascript
// CRITICAL: Resource costs in INITAL.md differ from backend implementation
// Frontend must follow INITAL.md specs:
// - Buy tile: 2 shovels (backend has 1)
// - Water reserve: 3 shovels (backend has 2 drops)
// - Firebreak: 3 shovels (backend has 1)
// - Irrigate: 1 drop (same)

// CRITICAL: Tile types naming inconsistency
// INITAL.md: "virgin" (empty unowned tile)
// Backend: "empty" (same concept)
// Frontend must map: backend "empty" → display as "Virgin Land"

// CRITICAL: React 19 new features
// StrictMode now runs effects twice in development
// Use cleanup functions in useEffect

// CRITICAL: HTML <dialog> element
// Must call .showModal() to open as modal (not just .show())
// Backdrop click closes automatically with ::backdrop CSS

// CRITICAL: State updates after API calls
// Always refetch game state after actions to sync with backend
// Backend is source of truth, not frontend state

// CRITICAL: Tailwind 4.x syntax changes
// Use Tailwind CSS v4 with @tailwindcss/vite plugin
// Class names may differ from v3

// CRITICAL: CORS configuration
// Backend already has CORS enabled for all origins
// Frontend on localhost:5173 can call localhost:8000

// CRITICAL: Step progression resource generation
// INITAL.md: +1 shovel, +1 drop, +10 score per step
// Backend: +1 drop per step only
// Frontend must display backend values, not INITAL specs
```

## Implementation Blueprint

### Data Models and Structure

#### 1. Game State Context
Create `frontend/src/context/GameContext.jsx`:
```javascript
import { createContext, useContext, useState, useEffect } from 'react';
import { fetchGameState, startNewGame } from '../utils/api';

const GameContext = createContext(null);

export function GameProvider({ children }) {
    const [gameState, setGameState] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedTile, setSelectedTile] = useState(null);

    const refreshGameState = async () => {
        try {
            const state = await fetchGameState();
            setGameState(state);
        } catch (error) {
            console.error('Failed to refresh game state:', error);
        }
    };

    useEffect(() => {
        refreshGameState().finally(() => setLoading(false));
    }, []);

    const value = {
        gameState,
        loading,
        refreshGameState,
        selectedTile,
        setSelectedTile,
        player: gameState?.player,
        tiles: gameState?.tiles,
        step: gameState?.step,
        isGameOver: gameState?.is_game_over
    };

    return (
        <GameContext.Provider value={value}>
            {children}
        </GameContext.Provider>
    );
}

export const useGame = () => {
    const context = useContext(GameContext);
    if (!context) {
        throw new Error('useGame must be used within GameProvider');
    }
    return context;
};
```

#### 2. API Client Utilities
Create `frontend/src/utils/api.js`:
```javascript
const API_BASE = 'http://localhost:8000';

// Game endpoints
export async function fetchGameState() {
    const res = await fetch(`${API_BASE}/game/state`);
    if (!res.ok) throw new Error('Failed to fetch game state');
    return res.json();
}

export async function startNewGame() {
    const res = await fetch(`${API_BASE}/game/start`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to start game');
    return res.json();
}

export async function advanceStep() {
    const res = await fetch(`${API_BASE}/game/next-step`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to advance step');
    return res.json();
}

// Tile action endpoints
export async function buyTile(tileId) {
    const res = await fetch(`${API_BASE}/tile/${tileId}/buy`, { method: 'POST' });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to buy tile');
    }
    return res.json();
}

export async function plantCrop(tileId, cropType) {
    const res = await fetch(`${API_BASE}/tile/${tileId}/plant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'plant', crop_type: cropType })
    });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to plant crop');
    }
    return res.json();
}

export async function irrigateTile(tileId) {
    const res = await fetch(`${API_BASE}/tile/${tileId}/irrigate`, { method: 'POST' });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to irrigate');
    }
    return res.json();
}

export async function harvestTile(tileId) {
    const res = await fetch(`${API_BASE}/tile/${tileId}/harvest`, { method: 'POST' });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to harvest');
    }
    return res.json();
}

export async function buildWaterReserve(tileId) {
    const res = await fetch(`${API_BASE}/tile/${tileId}/build-water-reserve`, { method: 'POST' });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to build water reserve');
    }
    return res.json();
}

export async function buildFirebreak(tileId) {
    const res = await fetch(`${API_BASE}/tile/${tileId}/build-firebreak`, { method: 'POST' });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to build firebreak');
    }
    return res.json();
}
```

### List of Tasks in Implementation Order

```yaml
Task 1: API Client and Utilities Setup
  PRIORITY: CRITICAL - Foundation for all API interactions

  CREATE frontend/src/utils/api.js:
    - Implement all API client functions as shown above
    - Add proper error handling with try/catch
    - Return JSON responses or throw errors

  CREATE frontend/src/constants/gameConfig.js:
    - Define resource costs from INITAL.md
    - Define tile type colors and icons
    - Define crop state colors
    - Define zone names (cold, arid, tropical, temperate)

  CREATE frontend/src/utils/tileHelpers.js:
    - getTileColor(tile) - returns Tailwind class based on type, owner, state
    - getTileIcon(tile) - returns emoji based on type and state
    - canPerformAction(action, tile, player) - validates if action is possible
    - getActionCost(action) - returns resource cost for action

  VALIDATION:
    - Run: npm run dev
    - Check: No console errors, utils can be imported

Task 2: Game State Management with Context
  PRIORITY: CRITICAL - Central state management

  CREATE frontend/src/context/GameContext.jsx:
    - Implement GameProvider with state hooks as shown above
    - Add refreshGameState function
    - Add selectedTile state for modal
    - Export useGame hook

  MODIFY frontend/src/App.jsx:
    - Import GameProvider
    - Wrap entire app with <GameProvider>
    - Keep existing structure

  VALIDATION:
    - Run: npm run dev
    - Check: useGame hook accessible in components
    - Check: gameState loads on mount

Task 3: Resource Display Component
  PRIORITY: HIGH - Core game UI

  CREATE frontend/src/components/ResourceDisplay.jsx:
    - Display shovels with shovel icon (🥄 or custom SVG)
    - Display drops with water drop icon (💧)
    - Display score with trophy/star icon (⭐ or 🏆)
    - Use useGame hook to get player resources
    - Style with Tailwind: pill badges, icons, bold numbers
    - Add tooltips explaining each resource

  MODIFY frontend/src/App.jsx:
    - Add <ResourceDisplay /> in header, top-right
    - Replace static badges with ResourceDisplay component

  VALIDATION:
    - Check: Resources display correctly
    - Check: Resources update when game state changes

Task 4: Game Stats Panel Component
  PRIORITY: HIGH - Game information display

  CREATE frontend/src/components/GameStatsPanel.jsx:
    - Display current step / max_steps
    - Count and display owned tiles (filter tiles by owner="player")
    - Count and display crops by state (seed, growing, harvest)
    - Count forests (type="forest")
    - Display conserved vs exploited forests
    - Use useGame hook for game state
    - Style as panel, use icons for visual interest

  MODIFY frontend/src/components/MatrixGrid.jsx:
    - Add <GameStatsPanel /> to left sidebar
    - Position below existing controls panel

  VALIDATION:
    - Check: Stats display correctly
    - Check: Counts match game state

Task 5: Enhanced Tile Visualization
  PRIORITY: HIGH - Visual feedback for game state

  MODIFY frontend/src/components/MatrixCell.jsx:
    - Import tileHelpers (getTileColor, getTileIcon)
    - Change cellStyle based on tile owner, type, state
    - Colors:
      - Unowned: light green/brown
      - Owned: darker green with border
      - Field with crop: yellow (seed), light green (growing), gold (harvest)
      - Forest: dark green
      - Water reserve: blue border overlay
    - Add icon overlay for crops and structures
    - Keep hover tooltip with details
    - Add onClick handler to trigger tile selection

  MODIFY frontend/src/components/MatrixGrid.jsx:
    - Pass onClick handler to MatrixCell
    - onClick calls setSelectedTile from useGame

  VALIDATION:
    - Check: Owned tiles visually distinct
    - Check: Crop states have different colors
    - Check: Clicking tile selects it

Task 6: Tile Action Modal
  PRIORITY: CRITICAL - Main player interaction

  CREATE frontend/src/components/TileActionModal.jsx:
    - Use HTML <dialog> element for modal
    - Accept selectedTile prop
    - Display tile details (position, type, owner, temperature, humidity, zone)
    - Show current crop state if applicable
    - Render action buttons based on tile state:
      - Buy Tile (if not owned)
      - Plant Crop (if owned, empty/field, no crop)
      - Irrigate (if owned, has crop)
      - Harvest (if owned, crop state = harvest)
      - Build Water Reserve (if owned, not already built)
      - Build Firebreak (if owned, not already built)
    - Each button shows resource cost and validates player has resources
    - Disable buttons if player lacks resources
    - On action click:
      - Call API function
      - Show loading state
      - On success: refresh game state, close modal, show toast
      - On error: show error message, keep modal open
    - Close button (X) and backdrop click closes modal

  MODIFY frontend/src/App.jsx:
    - Add <TileActionModal /> component
    - Pass selectedTile and setSelectedTile from useGame
    - Modal renders when selectedTile is not null

  VALIDATION:
    - Check: Modal opens when clicking tile
    - Check: Correct actions shown for tile state
    - Check: Action performs and updates game state
    - Check: Error handling works (insufficient resources)
    - Check: Modal closes after action or on backdrop click

Task 7: Next Step Button and Turn Progression
  PRIORITY: CRITICAL - Core game mechanic

  CREATE frontend/src/components/NextStepButton.jsx:
    - Large prominent button: "Next Step" or "End Turn"
    - Shows current step / max_steps
    - On click:
      - Call advanceStep API
      - Show loading state
      - On success: refresh game state
      - Show toast with step summary (crops advanced, etc.)
    - Disable if game is over
    - Style: prominent, colorful, animated

  MODIFY frontend/src/App.jsx or MatrixGrid:
    - Add <NextStepButton /> to header or left panel
    - Position prominently (e.g., bottom of left sidebar)

  VALIDATION:
    - Check: Button advances step
    - Check: Game state refreshes after step
    - Check: Crop states advance correctly
    - Check: Resources increase per step
    - Check: Button disabled when game over

Task 8: Game Over Screen
  PRIORITY: MEDIUM - End game experience

  CREATE frontend/src/components/GameOverScreen.jsx:
    - Full-screen overlay when is_game_over = true
    - Display final score, tiles owned, crops harvested
    - Show congratulations message
    - "Play Again" button that calls startNewGame
    - Style with celebration theme (confetti, trophy)

  MODIFY frontend/src/App.jsx:
    - Check if gameState.is_game_over
    - Render <GameOverScreen /> instead of normal UI

  VALIDATION:
    - Check: Game over screen shows at step 10 (max_steps)
    - Check: Play Again button restarts game
    - Check: New game loads correctly

Task 9: Loading States and Error Handling
  PRIORITY: HIGH - User experience polish

  ENHANCE all API-calling components:
    - Add loading spinners during API calls
    - Show error toasts for failed actions
    - Optimistic UI updates where appropriate
    - Graceful degradation if backend is down

  CREATE frontend/src/components/Toast.jsx (optional):
    - Simple toast notification for success/error messages
    - Auto-dismiss after 3 seconds
    - Position: top-right corner

  VALIDATION:
    - Check: Loading states show during actions
    - Check: Errors display user-friendly messages
    - Check: App doesn't crash on API failures

Task 10: Game Initialization Flow
  PRIORITY: MEDIUM - First-time user experience

  MODIFY frontend/src/App.jsx:
    - On first load, if game state returns 404:
      - Show welcome screen with "Start New Game" button
      - Call startNewGame API on click
      - Load game state after initialization
    - If game already exists, load directly

  VALIDATION:
    - Check: Fresh server shows "Start Game" screen
    - Check: Starting game loads correctly
    - Check: Existing game loads without prompt

Task 11: Responsive Design and Polish
  PRIORITY: LOW - Visual polish

  ENHANCE all components:
    - Ensure responsive layout on different screen sizes
    - Add animations/transitions for state changes
    - Polish color scheme and typography
    - Add icons for better visual communication
    - Test zoom and pan still works with new features

  VALIDATION:
    - Test: UI works on desktop (1920x1080, 1280x720)
    - Test: All buttons are accessible
    - Test: No visual glitches with zoom/pan

Task 12: Testing and Bug Fixes
  PRIORITY: HIGH - Quality assurance

  TEST full game flow:
    - Start new game
    - Buy a tile
    - Plant a crop
    - Irrigate the crop
    - Advance multiple steps
    - Harvest the crop
    - Build water reserve
    - Build firebreak
    - Reach game over
    - Play again

  FIX any bugs found during testing

  VALIDATION:
    - All actions work correctly
    - Game state stays in sync
    - No console errors
    - Performance is good (no lag with 1209 tiles)
```

### Per-Task Pseudocode (Selected Critical Tasks)

#### Task 2: Game State Management
```javascript
// frontend/src/context/GameContext.jsx

import { createContext, useContext, useState, useEffect } from 'react';
import { fetchGameState } from '../utils/api';

const GameContext = createContext(null);

export function GameProvider({ children }) {
    const [gameState, setGameState] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedTile, setSelectedTile] = useState(null);
    const [error, setError] = useState(null);

    const refreshGameState = async () => {
        try {
            setError(null);
            const state = await fetchGameState();
            setGameState(state);
        } catch (err) {
            setError(err.message);
            console.error('Failed to refresh game state:', err);
        }
    };

    useEffect(() => {
        refreshGameState().finally(() => setLoading(false));
    }, []);

    // Derived values for convenience
    const player = gameState?.player;
    const tiles = gameState?.tiles || [];
    const step = gameState?.step || 0;
    const isGameOver = gameState?.is_game_over || false;

    // Find selected tile details
    const selectedTileDetails = selectedTile
        ? tiles.find(t => t.id === selectedTile.id)
        : null;

    const value = {
        gameState,
        loading,
        error,
        refreshGameState,
        selectedTile: selectedTileDetails,
        setSelectedTile,
        player,
        tiles,
        step,
        isGameOver
    };

    return (
        <GameContext.Provider value={value}>
            {children}
        </GameContext.Provider>
    );
}

export const useGame = () => {
    const context = useContext(GameContext);
    if (!context) {
        throw new Error('useGame must be used within GameProvider');
    }
    return context;
};
```

#### Task 6: Tile Action Modal
```javascript
// frontend/src/components/TileActionModal.jsx

import { useRef, useEffect, useState } from 'react';
import { useGame } from '../context/GameContext';
import * as api from '../utils/api';
import { canPerformAction, getActionCost } from '../utils/tileHelpers';

export function TileActionModal() {
    const { selectedTile, setSelectedTile, player, refreshGameState } = useGame();
    const dialogRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Open/close dialog based on selectedTile
    useEffect(() => {
        if (selectedTile && dialogRef.current) {
            dialogRef.current.showModal();
        } else if (dialogRef.current && dialogRef.current.open) {
            dialogRef.current.close();
        }
    }, [selectedTile]);

    const handleClose = () => {
        setSelectedTile(null);
        setError(null);
    };

    const performAction = async (actionFn, actionName) => {
        setLoading(true);
        setError(null);
        try {
            await actionFn(selectedTile.id);
            await refreshGameState();
            handleClose();
            // TODO: Show success toast
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (!selectedTile) return null;

    const isOwned = selectedTile.owner === 'player';
    const hasResources = (cost) => {
        if (cost.shovels && player.shovels < cost.shovels) return false;
        if (cost.drops && player.drops < cost.drops) return false;
        return true;
    };

    return (
        <dialog
            ref={dialogRef}
            onClose={handleClose}
            className="backdrop:bg-black/50 rounded-lg shadow-2xl p-6 max-w-md"
        >
            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-2xl font-bold">
                        Tile [{selectedTile.grid_i}, {selectedTile.grid_j}]
                    </h2>
                    <button
                        onClick={handleClose}
                        className="text-gray-500 hover:text-gray-700 text-2xl"
                    >
                        ×
                    </button>
                </div>

                {/* Tile Details */}
                <div className="bg-gray-100 rounded p-4 space-y-2 text-sm">
                    <div><strong>Type:</strong> {selectedTile.type}</div>
                    <div><strong>Owner:</strong> {selectedTile.owner || 'None'}</div>
                    <div><strong>Temperature:</strong> {selectedTile.temperature.toFixed(2)}°C</div>
                    <div><strong>Humidity:</strong> {selectedTile.humidity.toFixed(3)}</div>
                    {selectedTile.tile_state && (
                        <div><strong>Crop State:</strong> {selectedTile.tile_state}</div>
                    )}
                </div>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                        {error}
                    </div>
                )}

                {/* Action Buttons */}
                <div className="space-y-2">
                    {!isOwned && canPerformAction('buy', selectedTile, player) && (
                        <button
                            onClick={() => performAction(api.buyTile, 'Buy Tile')}
                            disabled={loading || !hasResources({ shovels: 2 })}
                            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                        >
                            Buy Tile (2 🥄)
                        </button>
                    )}

                    {isOwned && !selectedTile.tile_state && canPerformAction('plant', selectedTile, player) && (
                        <button
                            onClick={() => performAction((id) => api.plantCrop(id, 'wheat'), 'Plant Crop')}
                            disabled={loading}
                            className="w-full bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                        >
                            Plant Crop 🌱
                        </button>
                    )}

                    {isOwned && selectedTile.tile_state && canPerformAction('irrigate', selectedTile, player) && (
                        <button
                            onClick={() => performAction(api.irrigateTile, 'Irrigate')}
                            disabled={loading || !hasResources({ drops: 1 })}
                            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                        >
                            Irrigate (1 💧)
                        </button>
                    )}

                    {isOwned && selectedTile.tile_state === 'harvest' && (
                        <button
                            onClick={() => performAction(api.harvestTile, 'Harvest')}
                            disabled={loading}
                            className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                        >
                            Harvest 🌾
                        </button>
                    )}

                    {isOwned && !selectedTile.has_water_reserve && (
                        <button
                            onClick={() => performAction(api.buildWaterReserve, 'Build Water Reserve')}
                            disabled={loading || !hasResources({ shovels: 3 })}
                            className="w-full bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                        >
                            Build Water Reserve (3 🥄)
                        </button>
                    )}

                    {isOwned && !selectedTile.has_firebreak && (
                        <button
                            onClick={() => performAction(api.buildFirebreak, 'Build Firebreak')}
                            disabled={loading || !hasResources({ shovels: 3 })}
                            className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                        >
                            Build Firebreak (3 🥄)
                        </button>
                    )}
                </div>

                {loading && (
                    <div className="text-center text-gray-600">
                        Processing...
                    </div>
                )}
            </div>
        </dialog>
    );
}
```

### Integration Points
```yaml
BACKEND:
  - base_url: http://localhost:8000
  - endpoints: /game/state, /game/start, /game/next-step, /tile/{id}/*
  - CORS: Already enabled for all origins

FRONTEND:
  - dev_server: http://localhost:5173 (Vite default)
  - api_calls: Use fetch API with async/await
  - state_management: React Context API

DATA_FLOW:
  - On mount: Fetch /game/state → populate GameContext
  - On action: POST to /tile/{id}/{action} → refresh /game/state
  - On next step: POST to /game/next-step → refresh /game/state
  - Tile data: Backend tiles array → map to grid positions for rendering
```

## Validation Loop

### Level 1: Development Server
```bash
# Start backend
cd Backend
source venv/bin/activate
python main.py &

# Start frontend
cd frontend
npm run dev

# Expected: No console errors, localhost:5173 loads
```

### Level 2: Component Testing
```bash
# Test each component in isolation
# 1. ResourceDisplay shows 3 shovels, 3 drops, 0 score
# 2. GameStatsPanel shows step 0, 0 owned tiles
# 3. Clicking tile opens TileActionModal
# 4. Action buttons are visible and enabled/disabled correctly
# 5. Performing action updates game state
```

### Level 3: Integration Testing
```bash
# Full game flow test:

1. Start new game
   - Click "Start Game" button
   - Verify game state loads
   - Verify resources: 3 shovels, 3 drops, 0 score

2. Buy first tile
   - Click any green (land) tile
   - Modal opens with "Buy Tile" button
   - Click "Buy Tile"
   - Verify modal closes
   - Verify tile is now owned (different color)
   - Verify shovels decreased to 1 (cost was 2)

3. Plant crop
   - Click owned tile
   - Click "Plant Crop"
   - Verify tile shows seed icon/color
   - Verify modal closes

4. Advance turn
   - Click "Next Step" button
   - Verify step increases to 1
   - Verify drops increase to 4
   - Verify crop advances to "growing"

5. Irrigate crop
   - Click tile with crop
   - Click "Irrigate"
   - Verify drops decrease to 3

6. Advance turns until harvest
   - Click "Next Step" multiple times
   - Verify crop advances to "harvest"

7. Harvest crop
   - Click harvest-ready tile
   - Click "Harvest"
   - Verify shovels and score increase
   - Verify tile returns to empty field

8. Build water reserve
   - Buy another tile
   - Click "Build Water Reserve"
   - Verify shovels decrease by 3

9. Reach game over
   - Click "Next Step" until step 10
   - Verify Game Over screen appears
   - Verify final score displayed

10. Play again
    - Click "Play Again"
    - Verify game resets to step 0
```

## Final Validation Checklist
- [ ] All API endpoints integrated successfully
- [ ] Resource display updates in real-time
- [ ] Tile clicks open action modal
- [ ] All tile actions work correctly
- [ ] Resource costs are enforced
- [ ] Turn progression advances game state
- [ ] Crop lifecycle progresses correctly
- [ ] Visual indicators for owned tiles, crops, structures
- [ ] Game Over screen appears at max_steps
- [ ] Play Again restarts game
- [ ] No console errors during gameplay
- [ ] Loading states shown during API calls
- [ ] Error handling works gracefully
- [ ] UI is responsive and visually polished

---

## Anti-Patterns to Avoid
- ❌ Don't store game state in multiple places - use Context as single source
- ❌ Don't mutate state directly - always use setter functions
- ❌ Don't forget to refresh game state after actions
- ❌ Don't use stale data - always get fresh data from backend
- ❌ Don't implement game logic in frontend - backend is authoritative
- ❌ Don't hardcode resource costs - use constants file
- ❌ Don't skip error handling - always catch API errors
- ❌ Don't block UI during API calls - use loading states
- ❌ Don't use index as key in lists - use tile.id
- ❌ Don't forget to close modal after successful action

## PRP Quality Score: 9/10

**Confidence Level**: High confidence for one-pass implementation

**Strengths**:
- Comprehensive task breakdown with clear dependencies
- Detailed pseudocode for critical components
- Existing frontend structure provides solid foundation
- Backend API is complete and working
- Clear validation steps at each level
- Integration with existing Tailwind styling patterns
- Addresses API/spec inconsistencies explicitly

**Potential Challenges**:
- Resource cost discrepancies between INITAL.md and backend may need reconciliation
- Performance with 1209 tiles and frequent state updates may need optimization
- Modal UX may need iteration based on user testing

**Missing** (-1 point):
- Specific design mockups for new UI components
- Performance optimization strategies for large tile grids
- Accessibility testing checklist (keyboard navigation, screen readers)

These can be addressed during implementation with reasonable UI/UX decisions.
