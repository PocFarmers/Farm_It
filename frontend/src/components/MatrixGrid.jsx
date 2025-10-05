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
      return {};
    }

    const map = {};
    gameState.tiles.forEach(tile => {
      // Create key from grid position
      const key = `${tile.grid_i},${tile.grid_j}`;
      map[key] = tile;
    });

    return map;
  }, [gameState?.tiles]);

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
      {/* Grille principale - 3/4 largeur */}
      <div
        className="w-3/4 bg-[#F5F2EA] flex items-center justify-center overflow-hidden relative"
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
            className="grid gap-0 shadow-2xl border-4 border-[#35613F]"
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
          className="!bg-[#35613F] !text-white !rounded-lg !shadow-xl !px-4 !py-3"
          style={{ zIndex: 1000 }}
        />
      </div>

      {/* Panneau latéral droit - 1/4 largeur - Game Stats Only */}
      <div className="w-1/4 bg-[#35613F] p-6 overflow-y-auto">
        <GameStatsPanel />
      </div>
    </div>
  );
}
