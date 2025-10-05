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
            <div className="bg-[#A37039] px-5 py-2 rounded-lg border-2 border-[#35613F] transition-colors">
                <span className="font-bold text-white text-base">
                    Shovels: {shovels}
                </span>
            </div>

            {/* Drops */}
            <div className="bg-[#35613F] px-5 py-2 rounded-lg border-2 border-[#A37039] transition-colors">
                <span className="font-bold text-white text-base">
                    Drops: {drops}
                </span>
            </div>

            {/* Score */}
            <div className="bg-[#F5A842] px-5 py-2 rounded-lg border-2 border-[#A37039] transition-colors shadow-lg">
                <span className="font-bold text-[#35613F] text-base">
                    Score: {score}
                </span>
            </div>
        </div>
    );
}
