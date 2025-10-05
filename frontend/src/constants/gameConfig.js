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

// Tile colors - Agricultural Color Palette
export const TILE_COLORS = {
    // Water/ocean
    water: 'bg-blue-400 hover:bg-blue-300',

    // Unowned land
    unowned: 'bg-[#A37039] hover:bg-[#8a5e30]',

    // Owned but empty
    owned_empty: 'bg-[#35613F] hover:bg-[#2a4f32] ring-2 ring-[#F5A842]',

    // Crops by state
    seed: 'bg-[#F5A842] hover:bg-[#e39835] ring-2 ring-[#A37039]',
    growing: 'bg-[#8EB854] hover:bg-[#7da845] ring-2 ring-[#A37039]',
    harvest: 'bg-[#F5A842] hover:bg-[#e39835] ring-2 ring-[#35613F]',

    // Forest
    forest: 'bg-[#35613F] hover:bg-[#2a4f32]',
    forest_owned: 'bg-[#35613F] hover:bg-[#2a4f32] ring-2 ring-[#F5A842]'
};

// Tile icons/emojis - Icons for crops, water reserve, and firebreak
export const TILE_ICONS = {
    water: '',
    unowned: '',
    owned_empty: '',
    seed: '🌱',
    growing: '🌿',
    harvest: '🌾',
    forest: '',
    water_reserve: '💧',
    firebreak: '🔥'
};

// Resource icons - Shovel and water drop
export const RESOURCE_ICONS = {
    shovel: '🥄',
    drop: '💧',
    score: ''
};

// Event icons - For disasters affecting tiles
export const EVENT_ICONS = {
    Drought: '☀️',
    Fire: '🔥'
};

// Game constants
export const GAME_CONSTANTS = {
    MAX_STEPS: 50,  // From INITAL.md
    STEP_DURATION_DAYS: 8,
    CROP_GROWTH_STEPS: 4  // Every 4 steps crop advances
};
