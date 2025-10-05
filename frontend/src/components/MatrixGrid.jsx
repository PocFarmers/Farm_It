import { Tooltip } from 'react-tooltip';
import { MatrixCell } from './MatrixCell';
import { GameStatsPanel } from './GameStatsPanel';
import { useState, useMemo } from 'react';
import { useGame } from '../context/GameContext';

export function MatrixGrid({ data, layers }) {
  // Defensive checks
  if (!data || !data.data || !Array.isArray(data.data)) {
    console.error('MatrixGrid: Invalid data prop', data);
    return (
      <div className="flex items-center justify-center h-screen bg-red-100">
        <p className="text-red-800 font-bold">Error: Invalid map data</p>
      </div>
    );
  }

  const matrix = data.data;
  const rows = matrix.length;
  const cols = matrix[0]?.length || 0;

  if (rows === 0 || cols === 0) {
    console.error('MatrixGrid: Empty matrix', { rows, cols });
    return (
      <div className="flex items-center justify-center h-screen bg-yellow-100">
        <p className="text-yellow-800 font-bold">Error: Empty map matrix</p>
      </div>
    );
  }

  // Get game state and tile selection handler
  const { gameState, setSelectedTile } = useGame();

  // Calculer la taille de cellule pour que toute la grille tienne à l'écran
  const availableHeight = window.innerHeight - 100;
  const availableWidth = (window.innerWidth * 0.75) - 100; // 3/4 de l'écran moins padding

  // Calculate cell size based on the rectangle dimensions
  const cellSizeByHeight = Math.floor(availableHeight / rows);
  const cellSizeByWidth = Math.floor(availableWidth / cols);
  const cellSize = Math.min(cellSizeByHeight, cellSizeByWidth);

  // Create tile map by grid position (i,j) for quick lookup
  const tileMap = useMemo(() => {
    if (!gameState?.tiles) {
      console.log('🗺️ [MatrixGrid] No gameState.tiles - game not initialized yet');
      return {};
    }

    console.log('🗺️ [MatrixGrid] Building tileMap from gameState.tiles:', {
      tilesCount: gameState.tiles.length,
      firstTile: gameState.tiles[0]
    });

    const map = {};
    gameState.tiles.forEach(tile => {
      // Create key from grid position
      const key = `${tile.grid_i},${tile.grid_j}`;
      map[key] = tile;
    });

    console.log(`🗺️ [MatrixGrid] Created tileMap with ${Object.keys(map).length} tiles`);
    console.log('🗺️ [MatrixGrid] Sample tileMap keys:', Object.keys(map).slice(0, 5));

    // Verify all island cells have tiles
    if (data?.data) {
      let islandCells = 0;
      let missingTiles = 0;
      data.data.forEach((row, i) => {
        row.forEach((cell, j) => {
          const mask = cell[0];
          if (mask === 1) {
            islandCells++;
            const key = `${i},${j}`;
            if (!map[key]) {
              missingTiles++;
              if (missingTiles <= 5) {
                console.error(`❌ [MatrixGrid] Missing tile for island cell [${i}, ${j}]`);
              }
            }
          }
        });
      });
      console.log(`🗺️ [MatrixGrid] Verification: ${islandCells} island cells, ${Object.keys(map).length} tiles in DB`);
      if (missingTiles > 0) {
        console.error(`❌ [MatrixGrid] ${missingTiles} island cells are missing tile data!`);
      } else {
        console.log('✅ [MatrixGrid] All island cells have tile data');
      }
    }

    return map;
  }, [gameState?.tiles, data]);

  // Helper to get tile by grid position
  const getTileByPosition = (row, col) => {
    const key = `${row},${col}`;
    return tileMap[key];
  };

  // Handle tile click
  const handleTileClick = (tile) => {
    setSelectedTile(tile);
  };

  // État pour le zoom et le pan
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Gestion du zoom avec la molette
  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom((prevZoom) => Math.min(Math.max(prevZoom * delta, 0.25), 4));
  };

  // Gestion du drag
  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Reset zoom et pan
  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="flex h-[calc(100vh-80px)]">
      {/* Panneau latéral gauche - 1/4 largeur */}
      <div className="w-1/4 bg-gradient-to-br from-green-700 to-green-900 p-6 text-white overflow-y-auto">
        <GameStatsPanel />

        <div className="mt-6 space-y-4">
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <h3 className="font-bold mb-3 flex items-center gap-2">
              <span>🎮</span>
              Contrôles
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-green-200">🖱️</span>
                <span>Molette pour zoomer</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-200">✋</span>
                <span>Clic + glisser pour déplacer</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-200">👆</span>
                <span>Cliquer sur tuile pour agir</span>
              </div>
            </div>
            <button
              onClick={resetView}
              className="mt-3 w-full bg-green-600 hover:bg-green-500 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              🔄 Réinitialiser vue
            </button>
          </div>

          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <h3 className="font-bold mb-3 flex items-center gap-2">
              <span>🔍</span>
              Zoom
            </h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-green-200">Niveau:</span>
                <span className="font-bold">{(zoom * 100).toFixed(0)}%</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setZoom((z) => Math.max(z * 0.8, 0.25))}
                  className="flex-1 bg-white/20 hover:bg-white/30 text-white font-bold py-1 px-2 rounded transition-colors"
                >
                  −
                </button>
                <button
                  onClick={() => setZoom((z) => Math.min(z * 1.25, 4))}
                  className="flex-1 bg-white/20 hover:bg-white/30 text-white font-bold py-1 px-2 rounded transition-colors"
                >
                  +
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Grille principale - 3/4 largeur */}
      <div
        className="w-3/4 bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center overflow-hidden relative"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.1s ease-out',
          }}
        >
          <div
            className="grid gap-0 shadow-2xl border-4 border-white/30"
            style={{
              gridTemplateColumns: `repeat(${cols}, ${cellSize}px)`,
              gridTemplateRows: `repeat(${rows}, ${cellSize}px)`,
            }}
          >
            {matrix.map((row, i) =>
              row.map((cellValues, j) => {
                const tile = getTileByPosition(i, j);
                return (
                  <MatrixCell
                    key={`${i}-${j}`}
                    row={i}
                    col={j}
                    values={cellValues}
                    layers={layers}
                    cellSize={cellSize}
                    tile={tile}
                    onTileClick={handleTileClick}
                  />
                );
              })
            )}
          </div>
        </div>

        <Tooltip
          id="matrix-cell"
          className="!bg-gray-900/95 !text-white !rounded-lg !shadow-xl !px-4 !py-3 !backdrop-blur-md"
          style={{ zIndex: 1000 }}
        />
      </div>
    </div>
  );
}
