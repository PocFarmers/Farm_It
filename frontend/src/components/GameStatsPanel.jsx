/**
 * Game Stats Panel Component
 * Shows current step, fields, forests, and crops statistics
 * Positioned at right-center of screen
 */

import { useGame } from '../context/GameContext';
import { GAME_CONSTANTS } from '../constants/gameConfig';

export function GameStatsPanel() {
    const { gameState, getOwnedTilesCount, getCropsStats, getForestsStats } = useGame();

    if (!gameState) {
        return null;
    }

    const ownedTiles = getOwnedTilesCount();
    const cropsStats = getCropsStats();
    const forestsStats = getForestsStats();
    const currentStep = gameState.step || 0;
    const maxSteps = GAME_CONSTANTS.MAX_STEPS;

    // Calculate fields count (owned tiles that are type 'field' or 'empty')
    const fields = gameState.tiles?.filter(t =>
        t.owner === 'player' && (t.type === 'field' || t.type === 'empty')
    ).length || 0;

    return (
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            {/* Header */}
            <div className="text-center mb-4 pb-3 border-b-2 border-white/30">
                <h2 className="text-xl font-bold text-white">📊 Game Stats</h2>
            </div>

            {/* Step Progress */}
            <div className="mb-4 p-3 bg-gradient-to-r from-blue-100 to-blue-200 rounded-lg border-2 border-blue-400">
                <div className="text-sm text-blue-900 font-semibold mb-1">Current Step</div>
                <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-blue-900">{currentStep}</span>
                    <span className="text-sm text-blue-700">/ {maxSteps}</span>
                </div>
                <div className="mt-2 bg-blue-300 rounded-full h-2 overflow-hidden">
                    <div
                        className="bg-blue-600 h-full transition-all duration-500"
                        style={{ width: `${(currentStep / maxSteps) * 100}%` }}
                    />
                </div>
            </div>

            {/* Tiles & Fields */}
            <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between p-2 bg-green-50 rounded border border-green-300">
                    <span className="text-sm font-medium text-green-900">🏞️ Owned Tiles</span>
                    <span className="text-lg font-bold text-green-700">{ownedTiles}</span>
                </div>

                <div className="flex items-center justify-between p-2 bg-amber-50 rounded border border-amber-300">
                    <span className="text-sm font-medium text-amber-900">🌾 Fields</span>
                    <span className="text-lg font-bold text-amber-700">{fields}</span>
                </div>
            </div>

            {/* Forests */}
            <div className="mb-4 p-3 bg-green-100 rounded-lg border-2 border-green-400">
                <div className="text-sm font-semibold text-green-900 mb-2">🌲 Forests</div>
                <div className="flex justify-between text-xs text-green-800">
                    <span>Total: <span className="font-bold">{forestsStats.total}</span></span>
                    <span>Owned: <span className="font-bold">{forestsStats.owned}</span></span>
                </div>
            </div>

            {/* Crops */}
            <div className="p-3 bg-yellow-50 rounded-lg border-2 border-yellow-400">
                <div className="text-sm font-semibold text-yellow-900 mb-2">🌱 Crops</div>
                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <span className="text-yellow-800">Total:</span>
                        <span className="font-bold text-yellow-900">{cropsStats.total}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                        <span className="text-yellow-800">🌱 Seedling:</span>
                        <span className="font-bold text-yellow-900">{cropsStats.seed}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                        <span className="text-yellow-800">🌿 Growing:</span>
                        <span className="font-bold text-yellow-900">{cropsStats.growing}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                        <span className="text-yellow-800">🌾 Ready:</span>
                        <span className="font-bold text-yellow-900">{cropsStats.harvest}</span>
                    </div>
                </div>
            </div>

            {/* Game Progress Indicator */}
            {currentStep >= maxSteps && (
                <div className="mt-4 p-2 bg-red-100 border-2 border-red-500 rounded text-center">
                    <span className="text-sm font-bold text-red-700">🏁 Game Complete!</span>
                </div>
            )}
        </div>
    );
}
