# Bug Fix: Water tooltip on land tiles

## Problem
When hovering over the orange island (land tiles with mask=1), some tiles incorrectly showed "Water" tooltip instead of tile information.

## Root Cause
The tooltip logic checked `if (!tile || mask === 0)` to determine if a cell is water. However:
- The backend only creates ~768 game tiles for specific positions
- The matrix has 727 land cells (mask=1)
- Some land cells (mask=1) don't have a corresponding `tile` object yet
- This caused the condition `!tile` to incorrectly identify land as water

## Solution

### 1. Fixed tooltip logic (MatrixCell.jsx:12-32)
```javascript
// OLD: if (!tile || mask === 0) return Water
// NEW: Check mask FIRST, then check if tile exists

if (mask === 0) {
  return Water tooltip;
}

if (!tile) {
  return Land tooltip with "Not yet in game";
}

// Show normal tile info
```

### 2. Updated getTileColor() function (tileHelpers.js:13-44)
```javascript
// OLD: getTileColor(tile)
// NEW: getTileColor(tile, mask)

// Now checks mask === 0 for water FIRST
// Then handles !tile case as unowned land
```

### 3. Updated getTileIcon() function (tileHelpers.js:51-83)
```javascript
// OLD: getTileIcon(tile)
// NEW: getTileIcon(tile, mask)

// Returns empty string for water and land without tile data
```

### 4. Updated MatrixCell component (MatrixCell.jsx:7-9)
```javascript
const cellStyle = getTileColor(tile, mask);
const icon = getTileIcon(tile, mask);
```

## Result
✅ Water cells (mask=0) always show blue with "Water" tooltip
✅ Land cells (mask=1) without tile data show orange/brown with "Land" tooltip
✅ Land cells (mask=1) with tile data show correct colors and full game info
✅ No more confusion between water and land
