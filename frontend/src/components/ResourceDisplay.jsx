/**
 * Resource Display Component
 * Shows player resources (shovels, drops, score) at top-right
 */

import { useGame } from '../context/GameContext';
import { RESOURCE_ICONS } from '../constants/gameConfig';

export function ResourceDisplay() {
    const { gameState } = useGame();

    if (!gameState || !gameState.player) {
        return null;
    }

    const { shovels, drops, score } = gameState.player;

    return (
        <div className="flex gap-3 text-sm">
            {/* Shovels */}
            <div className="bg-white/20 px-4 py-2 rounded-full backdrop-blur-sm border-2 border-white/30 hover:bg-white/30 transition-colors">
                <span className="font-bold text-white">
                    {RESOURCE_ICONS.shovel} {shovels}
                </span>
            </div>

            {/* Drops */}
            <div className="bg-white/20 px-4 py-2 rounded-full backdrop-blur-sm border-2 border-white/30 hover:bg-white/30 transition-colors">
                <span className="font-bold text-white">
                    {RESOURCE_ICONS.drop} {drops}
                </span>
            </div>

            {/* Score */}
            <div className="bg-yellow-400/90 px-4 py-2 rounded-full backdrop-blur-sm border-2 border-yellow-500 hover:bg-yellow-500 transition-colors shadow-lg">
                <span className="font-bold text-yellow-900">
                    {RESOURCE_ICONS.score} {score}
                </span>
            </div>
        </div>
    );
}
