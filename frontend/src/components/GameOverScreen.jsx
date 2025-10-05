/**
 * Game Over Screen Component
 * Shows final game statistics and allows starting a new game
 */

import { useGame } from '../context/GameContext';
import { GAME_CONSTANTS } from '../constants/gameConfig';

export function GameOverScreen() {
    const { gameState, isGameOver, initializeGame, getOwnedTilesCount, getCropsStats, getForestsStats } = useGame();

    if (!isGameOver || !gameState) {
        return null;
    }

    const player = gameState.player;
    const ownedTiles = getOwnedTilesCount();
    const cropsStats = getCropsStats();
    const forestsStats = getForestsStats();

    const handleNewGame = async () => {
        if (window.confirm('Start a new game? This will reset all progress.')) {
            await initializeGame();
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-6">
                    <h1 className="text-4xl font-bold text-center mb-2">
                        🏁 Game Complete!
                    </h1>
                    <p className="text-center text-yellow-100">
                        You survived {GAME_CONSTANTS.MAX_STEPS} steps (1 year)
                    </p>
                </div>

                {/* Final Score */}
                <div className="p-8">
                    <div className="text-center mb-8">
                        <div className="text-6xl font-bold text-yellow-600 mb-2">
                            ⭐ {player.score}
                        </div>
                        <p className="text-xl text-gray-600">Final Score</p>
                    </div>

                    {/* Statistics Grid */}
                    <div className="grid grid-cols-2 gap-4 mb-8">
                        {/* Resources */}
                        <div className="bg-blue-50 rounded-lg p-4 border-2 border-blue-200">
                            <h3 className="font-bold text-blue-900 mb-3">📦 Final Resources</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-blue-800">🥄 Shovels:</span>
                                    <span className="font-bold text-blue-900">{player.shovels}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-blue-800">💧 Drops:</span>
                                    <span className="font-bold text-blue-900">{player.drops}</span>
                                </div>
                            </div>
                        </div>

                        {/* Land */}
                        <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
                            <h3 className="font-bold text-green-900 mb-3">🏞️ Land Owned</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-green-800">Total Tiles:</span>
                                    <span className="font-bold text-green-900">{ownedTiles}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-green-800">🌲 Forests:</span>
                                    <span className="font-bold text-green-900">{forestsStats.owned}</span>
                                </div>
                            </div>
                        </div>

                        {/* Crops */}
                        <div className="bg-yellow-50 rounded-lg p-4 border-2 border-yellow-200">
                            <h3 className="font-bold text-yellow-900 mb-3">🌾 Crops</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-yellow-800">Total:</span>
                                    <span className="font-bold text-yellow-900">{cropsStats.total}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-yellow-800">🌾 Ready:</span>
                                    <span className="font-bold text-yellow-900">{cropsStats.harvest}</span>
                                </div>
                            </div>
                        </div>

                        {/* Performance */}
                        <div className="bg-purple-50 rounded-lg p-4 border-2 border-purple-200">
                            <h3 className="font-bold text-purple-900 mb-3">📊 Performance</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-purple-800">Steps:</span>
                                    <span className="font-bold text-purple-900">{gameState.step}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-purple-800">Avg Score/Step:</span>
                                    <span className="font-bold text-purple-900">
                                        {(player.score / gameState.step).toFixed(1)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Performance Rating */}
                    <div className="mb-8 p-4 bg-gradient-to-r from-green-100 to-blue-100 rounded-lg border-2 border-green-300">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-gray-800 mb-2">
                                {player.score >= 600 && '🏆 Excellent Farm Manager!'}
                                {player.score >= 400 && player.score < 600 && '👍 Good Farming Skills!'}
                                {player.score >= 200 && player.score < 400 && '🌱 Keep Learning!'}
                                {player.score < 200 && '💪 Try Again!'}
                            </div>
                            <p className="text-sm text-gray-600">
                                {ownedTiles > 10
                                    ? 'You expanded your farm significantly!'
                                    : 'Focus on expanding your territory next time.'}
                            </p>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-4">
                        <button
                            onClick={handleNewGame}
                            className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-4 px-6 rounded-lg transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
                        >
                            🔄 New Game
                        </button>
                        <button
                            onClick={() => window.location.reload()}
                            className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-4 px-6 rounded-lg transition-colors"
                        >
                            🔍 Review Map
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
