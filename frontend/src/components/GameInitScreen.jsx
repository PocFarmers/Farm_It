/**
 * Game Initialization Screen
 * Shows when no game exists and allows starting a new game
 */

import { useState } from 'react';
import { useGame } from '../context/GameContext';
import { GAME_CONSTANTS } from '../constants/gameConfig';

export function GameInitScreen() {
    const { gameState, loading, initializeGame } = useGame();
    const [starting, setStarting] = useState(false);
    const [error, setError] = useState(null);

    // Only show if game is not initialized and not loading
    if (loading || gameState) {
        return null;
    }

    const handleStartGame = async () => {
        try {
            setStarting(true);
            setError(null);
            await initializeGame();
        } catch (err) {
            setError(err.message || 'Failed to start game');
        } finally {
            setStarting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#F5F2EA]">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 overflow-hidden border-4 border-[#35613F]">
                {/* Header */}
                <div className="bg-[#35613F] text-white px-8 py-6">
                    <div className="flex items-center justify-center gap-4 mb-2">
                        <img src="/logo.png" alt="Farm It Logo" className="h-16 w-16 object-contain" />
                        <h1 className="text-5xl font-bold text-center">
                            Farm It
                        </h1>
                    </div>
                    <p className="text-center text-[#F5F2EA] text-lg opacity-90">
                        Build and Manage Your Sustainable Farm
                    </p>
                </div>

                {/* Content */}
                <div className="p-8">
                    {/* Game Description */}
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-[#35613F] mb-4 text-center">
                            Welcome, Farmer!
                        </h2>
                        <div className="space-y-3 text-[#35613F]">
                            <p className="flex items-start gap-2">
                                <span>
                                    <strong>Goal:</strong> Maximize your farm's productivity over{' '}
                                    {GAME_CONSTANTS.MAX_STEPS} steps (1 year)
                                </span>
                            </p>
                            <p className="flex items-start gap-2">
                                <span>
                                    <strong>Crops:</strong> Plant, irrigate, and harvest crops to earn score
                                </span>
                            </p>
                            <p className="flex items-start gap-2">
                                <span>
                                    <strong>Resources:</strong> Manage shovels and water drops wisely
                                </span>
                            </p>
                            <p className="flex items-start gap-2">
                                <span>
                                    <strong>Environment:</strong> Conserve forests for natural benefits
                                </span>
                            </p>
                        </div>
                    </div>

                    {/* Game Rules */}
                    <div className="mb-8 p-4 bg-[#F5F2EA] rounded-lg border-2 border-[#A37039]">
                        <h3 className="font-bold text-[#35613F] mb-3">Quick Rules</h3>
                        <ul className="space-y-2 text-sm text-[#35613F]">
                            <li>• Each step = {GAME_CONSTANTS.STEP_DURATION_DAYS} simulated days</li>
                            <li>• Crops advance every {GAME_CONSTANTS.CROP_GROWTH_STEPS} steps</li>
                            <li>• Click tiles to buy, plant, irrigate, or build structures</li>
                            <li>• Crops die if not irrigated (manual or water reserve)</li>
                            <li>• Conserved forests help adjacent fields grow</li>
                        </ul>
                    </div>

                    {/* Starting Resources */}
                    <div className="mb-8 p-4 bg-[#F5F2EA] rounded-lg border-2 border-[#35613F]">
                        <h3 className="font-bold text-[#35613F] mb-3">Starting Resources</h3>
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div>
                                <div className="text-sm font-semibold text-[#35613F]">3 Virgin Fields</div>
                            </div>
                            <div>
                                <div className="text-sm font-semibold text-[#35613F]">Starting Shovels</div>
                            </div>
                            <div>
                                <div className="text-sm font-semibold text-[#35613F]">Starting Drops</div>
                            </div>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="mb-6 p-4 bg-[#A37039] border-2 border-[#35613F] rounded-lg">
                            <p className="text-white font-medium text-center">
                                {error}
                            </p>
                        </div>
                    )}

                    {/* Start Button */}
                    <button
                        onClick={handleStartGame}
                        disabled={starting}
                        className={`w-full py-5 rounded-lg font-bold text-xl transition-all ${
                            starting
                                ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                                : 'bg-[#35613F] hover:bg-[#2a4f32] text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                        }`}
                    >
                        {starting ? (
                            <span className="flex items-center justify-center gap-2">
                                Starting Game...
                            </span>
                        ) : (
                            'Start New Game'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
