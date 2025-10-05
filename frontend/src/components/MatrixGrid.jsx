import { Tooltip } from 'react-tooltip';
import { MatrixCell } from './MatrixCell';
import { useState } from 'react';

export function MatrixGrid({ data, layers }) {
  const matrix = data.data;
  const gridSize = matrix.length;

  // Calculer la taille de cellule pour que toute la grille tienne à l'écran
  const availableHeight = window.innerHeight - 100;
  const availableWidth = (window.innerWidth * 0.75) - 100; // 3/4 de l'écran moins padding

  // Prendre la plus petite dimension pour que ça tienne
  const cellSize = Math.min(
    Math.floor(availableHeight / gridSize),
    Math.floor(availableWidth / gridSize)
  );

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
      <div className="w-1/4 bg-gradient-to-br from-green-700 to-green-900 p-6 text-white">
        <div className="space-y-6">
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <h2 className="text-xl font-bold mb-3 flex items-center gap-2">
              <span className="text-2xl">🏝️</span>
              Votre Île
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-green-200">Taille:</span>
                <span className="font-bold">{data.shape[0]}x{data.shape[1]}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-200">Tuiles:</span>
                <span className="font-bold">{data.shape[0] * data.shape[1]}</span>
              </div>
            </div>
          </div>

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
                <span className="text-green-200">ℹ️</span>
                <span>Survoler pour détails</span>
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

          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <h3 className="font-bold mb-3 flex items-center gap-2">
              <span>🎨</span>
              Légende
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-blue-600 rounded border-2 border-white/50"></div>
                <span>Eau</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-green-600 rounded border-2 border-white/50"></div>
                <span>Terre</span>
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
              gridTemplateColumns: `repeat(${matrix[0].length}, ${cellSize}px)`,
              gridTemplateRows: `repeat(${gridSize}, ${cellSize}px)`,
            }}
          >
            {matrix.map((row, i) =>
              row.map((cellValues, j) => (
                <MatrixCell
                  key={`${i}-${j}`}
                  row={i}
                  col={j}
                  values={cellValues}
                  layers={layers}
                  cellSize={cellSize}
                />
              ))
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
