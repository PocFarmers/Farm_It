/**
 * Next Step Button Component
 * Button to advance the game to the next turn/step
 */

import { useState } from 'react';
import { useGame } from '../context/GameContext';
import { GAME_CONSTANTS } from '../constants/gameConfig';

export function NextStepButton() {
    const { gameState, nextStep, isGameOver } = useGame();
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    const handleNextStep = async () => {
        try {
            setLoading(true);
            setMessage(null);

            await nextStep();

            // Show success message
            setMessage({
                type: 'success',
                text: '✓ Step advanced!'
            });

            // Clear message after 2 seconds
            setTimeout(() => {
                setMessage(null);
            }, 2000);
        } catch (error) {
            setMessage({
                type: 'error',
                text: error.message || 'Failed to advance step'
            });
        } finally {
            setLoading(false);
        }
    };

    if (!gameState) {
        return null;
    }

    const currentStep = gameState.step || 0;
    const maxSteps = GAME_CONSTANTS.MAX_STEPS;
    const isDisabled = loading || isGameOver;

    return (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-20">
            <div className="bg-[#F5F2EA] rounded-lg shadow-2xl border-4 border-[#35613F] p-4 min-w-[300px]">
                {/* Message Display */}
                {message && (
                    <div
                        className={`mb-3 p-2 rounded text-sm font-medium text-center ${
                            message.type === 'success'
                                ? 'bg-[#35613F] text-white'
                                : 'bg-[#A37039] text-white'
                        }`}
                    >
                        {message.text}
                    </div>
                )}

                {/* Next Step Button */}
                <button
                    onClick={handleNextStep}
                    disabled={isDisabled}
                    className={`w-full px-6 py-4 rounded-lg font-bold text-lg transition-all ${
                        isDisabled
                            ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                            : 'bg-[#35613F] hover:bg-[#2a4f32] text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                    }`}
                >
                    {loading ? (
                        <span className="flex items-center justify-center gap-2">
                            Processing...
                        </span>
                    ) : isGameOver ? (
                        <span>Game Complete!</span>
                    ) : (
                        <span className="flex items-center justify-center gap-2">
                            Next Step
                            <span className="text-sm font-normal">
                                ({currentStep + 1}/{maxSteps})
                            </span>
                        </span>
                    )}
                </button>

                {/* Step Info */}
                <div className="mt-3 text-center text-xs text-[#35613F]">
                    {isGameOver ? (
                        <span className="font-bold text-[#A37039]">
                            Maximum steps reached
                        </span>
                    ) : (
                        <span>
                            Each step = {GAME_CONSTANTS.STEP_DURATION_DAYS} days •
                            Crops advance every {GAME_CONSTANTS.CROP_GROWTH_STEPS} steps
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
