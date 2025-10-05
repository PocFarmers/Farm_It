/**
 * Game Configuration Constants
 * Costs, colors, icons, and other game constants
 */

// Action costs (following INITAL.md specifications)
export const ACTION_COSTS = {
    BUY_TILE: { shovels: 2 },
    PLANT_CROP: {},  // No cost
    IRRIGATE: { drops: 1 },
    HARVEST: {},  // No cost
    BUILD_WATER_RESERVE: { shovels: 3 },
    BUILD_FIREBREAK: { shovels: 3 }
};

// Tile type display names
export const TILE_TYPE_NAMES = {
    empty: 'Virgin Land',
    field: 'Field',
    forest: 'Forest'
};

// Crop state display names
export const CROP_STATE_NAMES = {
    seed: 'Seedling',
    growing: 'Growing',
    harvest: 'Ready to Harvest'
};

// Zone names
export const ZONE_NAMES = {
    1: 'Cold Zone',
    2: 'Arid Zone',
    3: 'Tropical Zone',
    4: 'Temperate Zone'
};

// Tile colors (Tailwind classes)
export const TILE_COLORS = {
    // Water/ocean
    water: 'bg-blue-600 hover:bg-blue-500',

    // Unowned land
    unowned: 'bg-amber-700 hover:bg-amber-600',

    // Owned but empty
    owned_empty: 'bg-green-700 hover:bg-green-600 ring-2 ring-yellow-400',

    // Crops by state
    seed: 'bg-yellow-600 hover:bg-yellow-500 ring-2 ring-yellow-400',
    growing: 'bg-lime-600 hover:bg-lime-500 ring-2 ring-yellow-400',
    harvest: 'bg-orange-500 hover:bg-orange-400 ring-2 ring-yellow-400',

    // Forest
    forest: 'bg-green-900 hover:bg-green-800',
    forest_owned: 'bg-green-900 hover:bg-green-800 ring-2 ring-yellow-400'
};

// Tile icons/emojis
export const TILE_ICONS = {
    water: '',
    unowned: '',
    owned_empty: '🏞️',
    seed: '🌱',
    growing: '🌿',
    harvest: '🌾',
    forest: '🌲',
    water_reserve: '💧',
    firebreak: '🔥'
};

// Resource icons
export const RESOURCE_ICONS = {
    shovel: '🥄',
    drop: '💧',
    score: '⭐'
};

// Game constants
export const GAME_CONSTANTS = {
    MAX_STEPS: 50,  // From INITAL.md
    STEP_DURATION_DAYS: 8,
    CROP_GROWTH_STEPS: 4  // Every 4 steps crop advances
};
