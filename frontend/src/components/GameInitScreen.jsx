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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-green-500 via-emerald-600 to-teal-700">
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl max-w-2xl w-full mx-4 overflow-hidden border-4 border-white/30">
                {/* Header */}
                <div className="bg-gradient-to-r from-green-600 to-emerald-700 text-white px-8 py-6">
                    <h1 className="text-5xl font-bold text-center mb-2">
                        🏝️ Farm It
                    </h1>
                    <p className="text-center text-green-100 text-lg">
                        Build and Manage Your Sustainable Farm
                    </p>
                </div>

                {/* Content */}
                <div className="p-8">
                    {/* Game Description */}
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
                            Welcome, Farmer!
                        </h2>
                        <div className="space-y-3 text-gray-700">
                            <p className="flex items-start gap-2">
                                <span className="text-2xl">🎯</span>
                                <span>
                                    <strong>Goal:</strong> Maximize your farm's productivity over{' '}
                                    {GAME_CONSTANTS.MAX_STEPS} steps (1 year)
                                </span>
                            </p>
                            <p className="flex items-start gap-2">
                                <span className="text-2xl">🌾</span>
                                <span>
                                    <strong>Crops:</strong> Plant, irrigate, and harvest crops to earn score
                                </span>
                            </p>
                            <p className="flex items-start gap-2">
                                <span className="text-2xl">🥄</span>
                                <span>
                                    <strong>Resources:</strong> Manage shovels and water drops wisely
                                </span>
                            </p>
                            <p className="flex items-start gap-2">
                                <span className="text-2xl">🌲</span>
                                <span>
                                    <strong>Environment:</strong> Conserve forests for natural benefits
                                </span>
                            </p>
                        </div>
                    </div>

                    {/* Game Rules */}
                    <div className="mb-8 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                        <h3 className="font-bold text-blue-900 mb-3">📋 Quick Rules</h3>
                        <ul className="space-y-2 text-sm text-blue-800">
                            <li>• Each step = {GAME_CONSTANTS.STEP_DURATION_DAYS} simulated days</li>
                            <li>• Crops advance every {GAME_CONSTANTS.CROP_GROWTH_STEPS} steps</li>
                            <li>• Click tiles to buy, plant, irrigate, or build structures</li>
                            <li>• Crops die if not irrigated (manual or water reserve)</li>
                            <li>• Conserved forests help adjacent fields grow</li>
                        </ul>
                    </div>

                    {/* Starting Resources */}
                    <div className="mb-8 p-4 bg-green-50 rounded-lg border-2 border-green-200">
                        <h3 className="font-bold text-green-900 mb-3">🎁 Starting Resources</h3>
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div>
                                <div className="text-3xl mb-1">🏞️</div>
                                <div className="text-sm font-semibold text-green-900">3 Virgin Fields</div>
                            </div>
                            <div>
                                <div className="text-3xl mb-1">🥄</div>
                                <div className="text-sm font-semibold text-green-900">Starting Shovels</div>
                            </div>
                            <div>
                                <div className="text-3xl mb-1">💧</div>
                                <div className="text-sm font-semibold text-green-900">Starting Drops</div>
                            </div>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="mb-6 p-4 bg-red-100 border-2 border-red-300 rounded-lg">
                            <p className="text-red-800 font-medium text-center">
                                ⚠️ {error}
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
                                : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                        }`}
                    >
                        {starting ? (
                            <span className="flex items-center justify-center gap-2">
                                <span className="animate-spin">⏳</span>
                                Starting Game...
                            </span>
                        ) : (
                            '🚀 Start New Game'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
