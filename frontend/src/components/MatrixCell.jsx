export function MatrixCell({ row, col, values, layers, cellSize }) {
  const [mask, moisture, temperature] = values;

  const tooltipContent = `
    <div class="space-y-2">
      <div class="font-bold text-lg border-b border-gray-600 pb-2">📍 Position [${row}, ${col}]</div>
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <span class="text-blue-400">🏝️</span>
          <span class="text-gray-300">${layers[0]}:</span>
          <span class="font-semibold">${mask === 1 ? 'Terre' : 'Eau'}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-blue-400">💧</span>
          <span class="text-gray-300">${layers[1]}:</span>
          <span class="font-semibold">${moisture.toFixed(3)}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-orange-400">🌡️</span>
          <span class="text-gray-300">${layers[2]}:</span>
          <span class="font-semibold">${temperature.toFixed(2)}°C</span>
        </div>
      </div>
    </div>
  `;

  // Couleurs simples : bleu = eau, vert = terre
  let cellStyle = '';

  if (mask === 0) {
    // Eau - bleu
    cellStyle = 'bg-blue-600 hover:bg-blue-500';
  } else {
    // Terre - vert
    cellStyle = 'bg-green-600 hover:bg-green-500';
  }

  return (
    <div
      className={`${cellStyle} transition-all duration-150 cursor-pointer border border-black/10`}
      style={{
        width: `${cellSize}px`,
        height: `${cellSize}px`,
      }}
      data-tooltip-id="matrix-cell"
      data-tooltip-html={tooltipContent}
      title=""
    >
    </div>
  );
}
