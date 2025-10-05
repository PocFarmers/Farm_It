# Debug Notes

## Bug: Map disappears after clicking Next Step

### Potential Causes:
1. The `data` prop to MatrixGrid becomes null/undefined
2. React re-render issue with GameProvider wrapping
3. Error in nextStep function causing component unmount
4. Conditional rendering hiding the grid

### Fixes Applied:
1. Fixed rectangle grid rendering (rows × cols instead of gridSize)
2. Fixed tile mapping to use grid_i, grid_j from backend
3. Backend now correctly adds +1 shovel, +1 drop, +10 score per step
4. Moved GameStatsPanel to sidebar

### To Test:
1. Open browser console
2. Click Next Step button
3. Check if there are any errors
4. Verify that `data` still exists in MatrixGrid

### Possible Solution:
The issue might be that the MatrixGrid re-renders but the data reference changes or becomes invalid. We should add error boundaries and defensive checks.
