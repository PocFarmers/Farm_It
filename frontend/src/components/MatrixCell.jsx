import { getTileColor, getTileIcon } from '../utils/tileHelpers';
import { ZONE_NAMES, TILE_TYPE_NAMES, CROP_STATE_NAMES } from '../constants/gameConfig';

export function MatrixCell({ row, col, values, layers, cellSize, tile, onTileClick }) {
  const [mask, moisture, temperature] = values;

  // Get tile visual properties - pass both tile and mask
  const cellStyle = getTileColor(tile, mask);
  const icon = getTileIcon(tile, mask);

  // Build tooltip content with game information
  const buildTooltip = () => {
    // Check mask first - mask === 0 means water
    if (mask === 0) {
      return `
        <div class="space-y-2">
          <div class="font-bold text-lg border-b border-gray-600 pb-2">🌊 Water</div>
          <div class="text-sm text-gray-300">Position [${row}, ${col}]</div>
        </div>
      `;
    }

    // Land tile (mask === 1) but no game tile data yet
    if (!tile) {
      return `
        <div class="space-y-2">
          <div class="font-bold text-lg border-b border-gray-600 pb-2">🏝️ Land</div>
          <div class="text-sm text-gray-300">Position [${row}, ${col}]</div>
          <div class="text-xs text-gray-400 mt-2">Not yet in game</div>
        </div>
      `;
    }

    const zoneName = ZONE_NAMES[tile.zone_id] || 'Unknown';
    const typeName = TILE_TYPE_NAMES[tile.type] || tile.type;
    const isOwned = tile.owner === 'player';

    let content = `
      <div class="space-y-2">
        <div class="font-bold text-lg border-b border-gray-600 pb-2">📍 Tile [${row}, ${col}]</div>
        <div class="space-y-1 text-sm">
          <div><span class="text-gray-400">Zone:</span> <span class="font-semibold">${zoneName}</span></div>
          <div><span class="text-gray-400">Type:</span> <span class="font-semibold">${typeName}</span></div>
          <div><span class="text-gray-400">Owner:</span> <span class="font-semibold">${isOwned ? '✓ You' : 'None'}</span></div>
    `;

    if (tile.tile_state) {
      const cropState = CROP_STATE_NAMES[tile.tile_state] || tile.tile_state;
      content += `<div><span class="text-gray-400">Crop:</span> <span class="font-semibold">${cropState}</span></div>`;
    }

    if (tile.has_water_reserve) {
      content += `<div class="text-blue-400">💧 Water Reserve</div>`;
    }

    if (tile.has_firebreak) {
      content += `<div class="text-orange-400">🔥 Firebreak</div>`;
    }

    content += `
          <div class="mt-2 pt-2 border-t border-gray-600">
            <div><span class="text-gray-400">🌡️ Temp:</span> ${temperature.toFixed(1)}°C</div>
            <div><span class="text-gray-400">💧 Humidity:</span> ${(moisture * 100).toFixed(0)}%</div>
          </div>
        </div>
      </div>
    `;

    return content;
  };

  const handleClick = (e) => {
    e.stopPropagation();
    // Only allow clicks on land tiles (mask === 1)
    // If tile exists in game state, trigger action modal
    if (mask === 1 && tile && onTileClick) {
      onTileClick(tile);
    }
  };

  return (
    <div
      className={`${cellStyle} transition-all duration-150 cursor-pointer border border-black/10 flex items-center justify-center text-xs font-bold select-none`}
      style={{
        width: `${cellSize}px`,
        height: `${cellSize}px`,
      }}
      data-tooltip-id="matrix-cell"
      data-tooltip-html={buildTooltip()}
      onClick={handleClick}
      title=""
    >
      {icon && <span className="drop-shadow-md">{icon}</span>}
    </div>
  );
}
