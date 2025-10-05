/**
 * Tile Action Modal Component
 * Modal dialog for performing actions on selected tiles
 */

import { useEffect, useRef, useState } from 'react';
import { useGame } from '../context/GameContext';
import {
    canPerformAction,
    getActionCost,
    hasResources,
    formatActionButton
} from '../utils/tileHelpers';
import {
    buyTile,
    plantCrop,
    irrigateTile,
    harvestTile,
    buildWaterReserve,
    buildFirebreak
} from '../utils/api';
import { ZONE_NAMES, TILE_TYPE_NAMES, CROP_STATE_NAMES } from '../constants/gameConfig';

export function TileActionModal() {
    const dialogRef = useRef(null);
    const { selectedTile, setSelectedTile, getPlayer, refreshGameState } = useGame();
    const [actionLoading, setActionLoading] = useState(false);
    const [actionMessage, setActionMessage] = useState(null);

    const player = getPlayer();

    // Open/close dialog based on selectedTile
    useEffect(() => {
        if (selectedTile && dialogRef.current) {
            dialogRef.current.showModal();
            setActionMessage(null);
        } else if (dialogRef.current && dialogRef.current.open) {
            dialogRef.current.close();
        }
    }, [selectedTile]);

    const closeModal = () => {
        setSelectedTile(null);
        setActionMessage(null);
    };

    // Action handlers
    const performAction = async (action, tileId) => {
        try {
            setActionLoading(true);
            setActionMessage(null);

            let result;
            switch (action) {
                case 'buy':
                    result = await buyTile(tileId);
                    break;
                case 'plant':
                    result = await plantCrop(tileId);
                    break;
                case 'irrigate':
                    result = await irrigateTile(tileId);
                    break;
                case 'harvest':
                    result = await harvestTile(tileId);
                    break;
                case 'build_water_reserve':
                    result = await buildWaterReserve(tileId);
                    break;
                case 'build_firebreak':
                    result = await buildFirebreak(tileId);
                    break;
                default:
                    throw new Error(`Unknown action: ${action}`);
            }

            // Refresh game state to show updated tile
            await refreshGameState();

            // Show success message
            setActionMessage({
                type: 'success',
                text: `✓ ${action.replace('_', ' ')} successful!`
            });

            // Auto-close after 1 second
            setTimeout(() => {
                closeModal();
            }, 1000);
        } catch (error) {
            setActionMessage({
                type: 'error',
                text: error.message || 'Action failed'
            });
        } finally {
            setActionLoading(false);
        }
    };

    if (!selectedTile) return null;

    const zoneName = ZONE_NAMES[selectedTile.zone_id] || 'Unknown';
    const typeName = TILE_TYPE_NAMES[selectedTile.type] || selectedTile.type;
    const isOwned = selectedTile.owner === 'player';

    // Define all possible actions
    const actions = [
        { id: 'buy', label: 'Buy Tile' },
        { id: 'plant', label: 'Plant Crop' },
        { id: 'irrigate', label: 'Irrigate' },
        { id: 'harvest', label: 'Harvest' },
        { id: 'build_water_reserve', label: 'Build Water Reserve' },
        { id: 'build_firebreak', label: 'Build Firebreak' }
    ];

    return (
        <dialog
            ref={dialogRef}
            className="backdrop:bg-black/50 bg-white rounded-lg shadow-2xl p-0 max-w-md w-full"
            onClose={closeModal}
        >
            <div className="bg-[#35613F] text-white px-6 py-4 rounded-t-lg">
                <h2 className="text-2xl font-bold">Tile Actions</h2>
                <p className="text-sm text-[#F5F2EA] opacity-90">Tile ID: {selectedTile.id}</p>
            </div>

            <div className="p-6">
                {/* Tile Information */}
                <div className="mb-6 p-4 bg-[#F5F2EA] rounded-lg border-2 border-[#A37039]">
                    <h3 className="font-semibold text-[#35613F] mb-3 text-lg">Tile Info</h3>
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-[#A37039]">Zone:</span>
                            <span className="font-semibold text-[#35613F]">{zoneName}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-[#A37039]">Type:</span>
                            <span className="font-semibold text-[#35613F]">{typeName}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-[#A37039]">Owner:</span>
                            <span className="font-semibold text-[#35613F]">
                                {isOwned ? 'You' : 'None'}
                            </span>
                        </div>
                        {selectedTile.tile_state && (
                            <div className="flex justify-between">
                                <span className="text-[#A37039]">Crop State:</span>
                                <span className="font-semibold text-[#35613F]">
                                    {CROP_STATE_NAMES[selectedTile.tile_state]}
                                </span>
                            </div>
                        )}
                        {selectedTile.has_water_reserve && (
                            <div className="text-[#35613F] font-medium">Has Water Reserve</div>
                        )}
                        {selectedTile.has_firebreak && (
                            <div className="text-[#F5A842] font-medium">Has Firebreak</div>
                        )}
                    </div>
                </div>

                {/* Action Message */}
                {actionMessage && (
                    <div
                        className={`mb-4 p-3 rounded-lg font-medium ${
                            actionMessage.type === 'success'
                                ? 'bg-[#35613F] text-white border-2 border-[#F5A842]'
                                : 'bg-[#A37039] text-white border-2 border-[#35613F]'
                        }`}
                    >
                        {actionMessage.text}
                    </div>
                )}

                {/* Available Actions */}
                <div className="mb-6">
                    <h3 className="font-semibold text-[#35613F] mb-3 text-lg">Available Actions</h3>
                    <div className="space-y-2">
                        {actions.map(action => {
                            const canPerform = canPerformAction(action.id, selectedTile, player);
                            const cost = getActionCost(action.id);
                            const hasEnoughResources = hasResources(player, cost);
                            const isDisabled = !canPerform || !hasEnoughResources || actionLoading;

                            if (!canPerform) return null;

                            return (
                                <button
                                    key={action.id}
                                    onClick={() => performAction(action.id, selectedTile.id)}
                                    disabled={isDisabled}
                                    className={`w-full px-4 py-3 rounded-lg font-medium text-left transition-colors ${
                                        isDisabled
                                            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                                            : 'bg-[#35613F] hover:bg-[#2a4f32] text-white cursor-pointer'
                                    }`}
                                >
                                    <div className="flex justify-between items-center">
                                        <span>{formatActionButton(action.id, cost)}</span>
                                        {!hasEnoughResources && (
                                            <span className="text-xs text-[#F5A842]">
                                                Insufficient resources
                                            </span>
                                        )}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Close Button */}
                <button
                    onClick={closeModal}
                    className="w-full px-4 py-3 bg-[#A37039] hover:bg-[#8a5e30] text-white font-medium rounded-lg transition-colors"
                    disabled={actionLoading}
                >
                    Close
                </button>
            </div>
        </dialog>
    );
}
