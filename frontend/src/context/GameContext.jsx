/**
 * Game Context
 * Global state management for Farm It game
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { fetchGameState, startNewGame, advanceStep } from '../utils/api';

const GameContext = createContext(null);

export function GameProvider({ children }) {
    const [gameState, setGameState] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedTile, setSelectedTile] = useState(null);
    const [isGameOver, setIsGameOver] = useState(false);

    // Fetch game state from backend
    const refreshGameState = useCallback(async () => {
        try {
            setError(null);
            const data = await fetchGameState();
            setGameState(data);

            // Check if game is over (50 steps reached)
            if (data.step >= 50) {
                setIsGameOver(true);
            }

            return data;
        } catch (err) {
            if (err.message === 'GAME_NOT_INITIALIZED') {
                setGameState(null);
            } else {
                setError(err.message);
            }
            throw err;
        }
    }, []);

    // Initialize game
    const initializeGame = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await startNewGame();
            setGameState(data);
            setIsGameOver(false);
            return data;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Advance to next step
    const nextStep = useCallback(async () => {
        try {
            setError(null);
            const data = await advanceStep();
            setGameState(data);

            // Check if game is now over
            if (data.step >= 50) {
                setIsGameOver(true);
            }

            return data;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, []);

    // Load game state on mount
    useEffect(() => {
        refreshGameState()
            .catch(() => {
                // Game not initialized, that's ok
            })
            .finally(() => {
                setLoading(false);
            });
    }, [refreshGameState]);

    // Helper to get player resources
    const getPlayer = useCallback(() => {
        if (!gameState?.player) return null;
        return gameState.player;
    }, [gameState]);

    // Helper to get a specific tile by ID
    const getTile = useCallback((tileId) => {
        if (!gameState?.tiles) return null;
        return gameState.tiles.find(t => t.id === tileId);
    }, [gameState]);

    // Get owned tiles count
    const getOwnedTilesCount = useCallback(() => {
        if (!gameState?.tiles) return 0;
        return gameState.tiles.filter(t => t.owner === 'player').length;
    }, [gameState]);

    // Get crops statistics
    const getCropsStats = useCallback(() => {
        if (!gameState?.tiles) return { total: 0, seed: 0, growing: 0, harvest: 0 };

        const crops = gameState.tiles.filter(t => t.tile_state);
        return {
            total: crops.length,
            seed: crops.filter(t => t.tile_state === 'seed').length,
            growing: crops.filter(t => t.tile_state === 'growing').length,
            harvest: crops.filter(t => t.tile_state === 'harvest').length
        };
    }, [gameState]);

    // Get forest statistics
    const getForestsStats = useCallback(() => {
        if (!gameState?.tiles) return { total: 0, owned: 0 };

        const forests = gameState.tiles.filter(t => t.type === 'forest');
        return {
            total: forests.length,
            owned: forests.filter(t => t.owner === 'player').length
        };
    }, [gameState]);

    const value = {
        gameState,
        loading,
        error,
        selectedTile,
        setSelectedTile,
        isGameOver,
        refreshGameState,
        initializeGame,
        nextStep,
        getPlayer,
        getTile,
        getOwnedTilesCount,
        getCropsStats,
        getForestsStats
    };

    return (
        <GameContext.Provider value={value}>
            {children}
        </GameContext.Provider>
    );
}

// Custom hook to use game context
export function useGame() {
    const context = useContext(GameContext);
    if (!context) {
        throw new Error('useGame must be used within a GameProvider');
    }
    return context;
}
