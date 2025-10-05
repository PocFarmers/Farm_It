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
        <div className="bg-[#F5F2EA] rounded-lg p-5 shadow-lg">
            {/* Header */}
            <div className="text-center mb-5 pb-4 border-b-2 border-[#A37039]">
                <h2 className="text-2xl font-bold text-[#35613F]">Game Stats</h2>
            </div>

            {/* Step Progress */}
            <div className="mb-4 p-4 bg-white rounded-lg border-2 border-[#A37039] shadow-sm">
                <div className="text-sm text-[#35613F] font-semibold mb-2">Current Step</div>
                <div className="flex items-center justify-between">
                    <span className="text-3xl font-bold text-[#35613F]">{currentStep}</span>
                    <span className="text-base text-[#A37039] font-medium">/ {maxSteps}</span>
                </div>
                <div className="mt-3 bg-[#F5F2EA] rounded-full h-3 overflow-hidden border border-[#A37039]">
                    <div
                        className="bg-[#F5A842] h-full transition-all duration-500"
                        style={{ width: `${(currentStep / maxSteps) * 100}%` }}
                    />
                </div>
            </div>

            {/* Tiles & Fields */}
            <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between p-3 bg-white rounded-lg border-2 border-[#35613F] shadow-sm">
                    <span className="text-sm font-semibold text-[#35613F]">Owned Tiles</span>
                    <span className="text-xl font-bold text-[#35613F]">{ownedTiles}</span>
                </div>

                <div className="flex items-center justify-between p-3 bg-white rounded-lg border-2 border-[#A37039] shadow-sm">
                    <span className="text-sm font-semibold text-[#A37039]">Fields</span>
                    <span className="text-xl font-bold text-[#A37039]">{fields}</span>
                </div>
            </div>

            {/* Forests */}
            <div className="mb-4 p-4 bg-white rounded-lg border-2 border-[#35613F] shadow-sm">
                <div className="text-base font-bold text-[#35613F] mb-3">Forests</div>
                <div className="flex justify-between text-sm text-[#35613F]">
                    <span>Total: <span className="font-bold">{forestsStats.total}</span></span>
                    <span>Owned: <span className="font-bold">{forestsStats.owned}</span></span>
                </div>
            </div>

            {/* Crops */}
            <div className="p-4 bg-white rounded-lg border-2 border-[#F5A842] shadow-sm">
                <div className="text-base font-bold text-[#F5A842] mb-3">Crops</div>
                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span className="text-[#35613F]">Total:</span>
                        <span className="font-bold text-[#35613F]">{cropsStats.total}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-[#35613F]">Seedling:</span>
                        <span className="font-bold text-[#35613F]">{cropsStats.seed}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-[#35613F]">Growing:</span>
                        <span className="font-bold text-[#35613F]">{cropsStats.growing}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-[#35613F]">Ready:</span>
                        <span className="font-bold text-[#35613F]">{cropsStats.harvest}</span>
                    </div>
                </div>
            </div>

            {/* Game Progress Indicator */}
            {currentStep >= maxSteps && (
                <div className="mt-4 p-3 bg-[#F5A842] border-2 border-[#A37039] rounded-lg text-center shadow-sm">
                    <span className="text-sm font-bold text-[#35613F]">Game Complete!</span>
                </div>
            )}
        </div>
    );
}
