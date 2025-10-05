/**
 * API Client for Farm It Game Backend
 * All API calls to FastAPI backend at localhost:8000
 */

const API_BASE = 'http://localhost:8000';

// Game State Endpoints
export async function fetchGameState() {
    const res = await fetch(`${API_BASE}/game/state`);
    if (!res.ok) {
        if (res.status === 404) {
            throw new Error('GAME_NOT_INITIALIZED');
        }
        throw new Error('Failed to fetch game state');
    }
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

// Tile Action Endpoints
export async function buyTile(tileId) {
    const res = await fetch(`${API_BASE}/tile/${tileId}/buy`, { method: 'POST' });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to buy tile');
    }
    return res.json();
}

export async function plantCrop(tileId, cropType = 'wheat') {
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
