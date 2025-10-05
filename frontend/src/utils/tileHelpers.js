/**
 * Tile Helper Functions
 * Utilities for determining tile colors, icons, and action availability
 */

import { TILE_COLORS, TILE_ICONS, ACTION_COSTS } from '../constants/gameConfig';

/**
 * Get Tailwind color class for a tile based on its state
 * @param {Object} tile - The tile data from game state (can be null)
 * @param {number} mask - The mask value from matrix (0 = water, 1 = tile)
 */
export function getTileColor(tile, mask) {
    // Water/ocean (mask = 0)
    if (mask === 0) {
        return TILE_COLORS.water;
    }

    // Tile without data - should not happen but show as error
    if (!tile) {
        return 'bg-red-500';
    }

    // Owned tile with crop
    if (tile.owner === 'player' && tile.tile_state) {
        return TILE_COLORS[tile.tile_state] || TILE_COLORS.owned_empty;
    }

    // Owned but empty
    if (tile.owner === 'player') {
        if (tile.type === 'forest') {
            return TILE_COLORS.forest_owned;
        }
        return TILE_COLORS.owned_empty;
    }

    // Forest (not owned)
    if (tile.type === 'forest') {
        return TILE_COLORS.forest;
    }

    // Unowned tile
    return TILE_COLORS.unowned;
}

/**
 * Get icon/emoji for a tile based on its state
 * @param {Object} tile - The tile data from game state (can be null)
 * @param {number} mask - The mask value from matrix (0 = water, 1 = tile)
 */
export function getTileIcon(tile, mask) {
    // Water - no icon
    if (mask === 0) {
        return '';
    }

    // Tile without data - show error
    if (!tile) {
        return '⚠️';
    }

    // Show structures as overlay
    const icons = [];

    if (tile.has_water_reserve) {
        icons.push(TILE_ICONS.water_reserve);
    }

    if (tile.has_firebreak) {
        icons.push(TILE_ICONS.firebreak);
    }

    // Show crop state
    if (tile.tile_state) {
        icons.push(TILE_ICONS[tile.tile_state]);
    } else if (tile.owner === 'player') {
        icons.push(TILE_ICONS.owned_empty);
    } else if (tile.type === 'forest') {
        icons.push(TILE_ICONS.forest);
    }

    return icons.join('');
}

/**
 * Check if a specific action can be performed on a tile
 */
export function canPerformAction(action, tile, player) {
    if (!tile || !player) return false;

    const isOwned = tile.owner === 'player';

    switch (action) {
        case 'buy':
            return !isOwned;

        case 'plant':
            return isOwned &&
                   (tile.type === 'empty' || tile.type === 'field') &&
                   !tile.tile_state;

        case 'irrigate':
            return isOwned &&
                   tile.type === 'field' &&
                   tile.tile_state &&
                   tile.tile_state !== 'harvest';

        case 'harvest':
            return isOwned && tile.tile_state === 'harvest';

        case 'build_water_reserve':
            return isOwned && !tile.has_water_reserve;

        case 'build_firebreak':
            return isOwned && !tile.has_firebreak;

        default:
            return false;
    }
}

/**
 * Get resource cost for an action
 */
export function getActionCost(action) {
    const costMap = {
        'buy': ACTION_COSTS.BUY_TILE,
        'plant': ACTION_COSTS.PLANT_CROP,
        'irrigate': ACTION_COSTS.IRRIGATE,
        'harvest': ACTION_COSTS.HARVEST,
        'build_water_reserve': ACTION_COSTS.BUILD_WATER_RESERVE,
        'build_firebreak': ACTION_COSTS.BUILD_FIREBREAK
    };
    return costMap[action] || {};
}

/**
 * Check if player has sufficient resources for an action
 */
export function hasResources(player, cost) {
    if (!player || !cost) return true;

    if (cost.shovels && player.shovels < cost.shovels) {
        return false;
    }

    if (cost.drops && player.drops < cost.drops) {
        return false;
    }

    return true;
}

/**
 * Format action button text with cost
 */
export function formatActionButton(action, cost) {
    const actionNames = {
        'buy': 'Buy Tile',
        'plant': 'Plant Crop',
        'irrigate': 'Irrigate',
        'harvest': 'Harvest',
        'build_water_reserve': 'Build Water Reserve',
        'build_firebreak': 'Build Firebreak'
    };

    let text = actionNames[action] || action;

    if (cost.shovels) {
        text += ` (${cost.shovels} 🥄)`;
    }

    if (cost.drops) {
        text += ` (${cost.drops} 💧)`;
    }

    return text;
}
