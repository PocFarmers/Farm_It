import { getTileColor, getTileIcon } from '../utils/tileHelpers';
import { ZONE_NAMES, TILE_TYPE_NAMES, CROP_STATE_NAMES } from '../constants/gameConfig';

export function MatrixCell({ row, col, values, cellSize, tile, onTileClick }) {
  const [mask, matrixMoisture, matrixTemperature] = values;

  // Use tile data if available (from game state), otherwise use matrix data (from map)
  const moisture = tile?.humidity ?? matrixMoisture;
  const temperature = tile?.temperature ?? matrixTemperature;

  // Debug logging - only show for first island cell to avoid spam
  if (row === 0 && col === 0 && mask === 1) {
    console.log(`🔍 [MatrixCell] Cell [${row}, ${col}] data:`, {
      mask,
      matrixMoisture,
      matrixTemperature,
      hasTile: !!tile,
      tileTemp: tile?.temperature,
      tileHumidity: tile?.humidity,
      finalTemp: temperature,
      finalMoisture: moisture
    });
  }

  // Get tile visual properties - pass both tile and mask
  const cellStyle = getTileColor(tile, mask);
  const icon = getTileIcon(tile, mask);

  // Build tooltip content with game information
  const buildTooltip = () => {
    // ONLY two states: water (mask === 0) or tile (mask === 1)
    if (mask === 0) {
      return `
        <div class="space-y-2">
          <div class="font-bold text-lg border-b border-gray-600 pb-2">🌊 Water</div>
          <div class="text-sm text-gray-300">Position [${row}, ${col}]</div>
        </div>
      `;
    }

    // Tile (mask === 1) - tile should ALWAYS exist after game initialization
    // If tile is missing, it's a bug - log error but show basic data
    if (!tile) {
      console.error(`❌ [MatrixCell] BUG: Island cell [${row}, ${col}] has mask=1 but no tile data!`);
      return `
        <div class="space-y-2">
          <div class="font-bold text-lg border-b border-gray-600 pb-2">⚠️ ERROR</div>
          <div class="text-sm text-red-300">Tile data missing at [${row}, ${col}]</div>
          <div class="text-xs text-gray-400 mt-2">This should not happen. Please report this bug.</div>
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
    // Only allow clicks on tiles (mask === 1), not water
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
