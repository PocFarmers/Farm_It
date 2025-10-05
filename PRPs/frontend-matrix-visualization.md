name: "Farm It - Frontend Matrix Visualization with Hover Tooltips"
description: |

## Purpose
Create a React-based frontend that visualizes a 3D matrix (200x200 grid with 3 layers) returned from the FastAPI `/get_map` endpoint. The visualization should display the matrix with blue styling and show detailed layer information on cell hover using an interactive tooltip.

## Core Principles
1. **Simple & Clean Design**: Readable grid display with minimal UI complexity
2. **Interactive Hover**: Smooth tooltip experience showing all layer data
3. **Performance**: Efficiently render 40,000 cells (200x200 grid)
4. **Responsive API**: Auto-fetch data on load with error handling
5. **Modern Stack**: React + Vite + TailwindCSS

---

## Goal
Build a web application that:
- Fetches the 3D matrix from `http://localhost:8000/get_map` on page load
- Renders a 200x200 grid visualization with blue text
- Shows layer information (mask, soil_moisture, soil_temperature) in a tooltip when hovering over cells
- Provides clean, maintainable code structure

## Why
- **User Value**: Visual representation of farm island data makes it easier to understand spatial distribution of environmental metrics
- **Integration**: Frontend connects to existing FastAPI backend without modifications
- **Interactivity**: Hover tooltips provide detailed data access without cluttering the UI
- **Foundation**: Establishes the base visualization layer for future game mechanics

## What
A single-page React application that displays matrix data with the following user-visible behavior:

**On Page Load:**
- Automatically calls `/get_map` endpoint
- Shows loading state during API call
- Displays error message if API fails
- Renders the matrix once data is received

**Grid Display:**
- 200x200 grid of cells
- Blue font color for matrix values
- Responsive cell sizing
- Clear visual boundaries between cells

**Hover Interaction:**
- Tooltip appears when hovering over any cell
- Shows all three layers of data for that cell:
  - Layer 0: Island presence (mask) - 0 or 1
  - Layer 1: Soil moisture value
  - Layer 2: Soil temperature value
- Tooltip follows cursor or anchors to cell
- Smooth show/hide transitions

### Success Criteria
- [ ] Grid renders all 200x200 cells with data from API
- [ ] Blue text styling applied consistently
- [ ] Hovering any cell shows tooltip with correct layer data
- [ ] Page loads and fetches data automatically
- [ ] Loading and error states display appropriately
- [ ] Application runs with `npm run dev` and builds successfully
- [ ] No console errors or warnings

## All Needed Context

### Documentation & References
```yaml
# Backend API Documentation
- file: Backend/main.py
  why: FastAPI endpoint structure, CORS configuration, response format
  critical: |
    - Endpoint: GET http://localhost:8000/get_map
    - Response format: { status, shape, data, layers }
    - data is a 3D array: [200][200][3]
    - layers: ["mask", "soil_moisture", "soil_temperature"]
    - CORS enabled for all origins

- file: Backend/get_map/get_map.py
  why: Understanding the data generation and structure
  critical: |
    - Matrix shape: (200, 200, 3)
    - Layer 0: Binary mask (0 or 1) - island presence
    - Layer 1: Soil moisture (float values, 0 where mask=0)
    - Layer 2: Soil temperature (float values, 0 where mask=0)
    - Values outside the island (mask=0) will be 0 for all layers

# React Documentation
- url: https://react.dev/reference/react
  why: React hooks (useState, useEffect) for state management and data fetching
  section: Hooks API Reference

- url: https://react.dev/learn/synchronizing-with-effects
  why: Understanding useEffect for API calls on component mount

# Vite Documentation
- library: /vitejs/vite
  why: Project setup, dev server, and build configuration
  section: Getting Started - Scaffolding Your First Vite Project
  critical: Use `npm create vite@latest` with React template

# TailwindCSS Documentation
- url: https://tailwindcss.com/docs/installation/using-vite
  why: Setup Tailwind with Vite for styling

- url: https://tailwindcss.com/docs/text-color
  why: Applying blue text color (text-blue-600, text-blue-700)

# React Tooltip Libraries Research
- library: react-tooltip (recommended for simplicity)
  url: https://react-tooltip.com/
  why: Simple, lightweight tooltip with hover support
  critical: |
    - Install: npm install react-tooltip
    - Basic usage: <Tooltip id="my-tooltip" /> + data-tooltip-id attribute
    - Supports HTML content in tooltip body

- alternative: @tippyjs/react (for advanced customization)
  url: https://github.com/atomiks/tippyjs-react
  why: More customization options, animations

- alternative: Floating UI
  url: https://floating-ui.com/
  why: Headless option for full control (more complex)

# Grid Visualization Patterns
- pattern: CSS Grid for responsive layouts
  url: https://css-tricks.com/snippets/css/complete-guide-grid/
  why: May use for overall layout structure

- pattern: Virtualization for large grids (optional optimization)
  url: https://github.com/bvaughn/react-window
  why: If performance becomes an issue with 40,000 cells
  critical: May not be needed initially - test first
```

### Current Codebase Tree
```bash
.
├── Backend/
│   ├── get_map/
│   │   ├── get_map.py          # Matrix generation logic
│   │   └── get_history_info.py # Weather data fetching
│   ├── in_game/
│   │   └── get_event.py        # Event determination
│   ├── main.py                 # FastAPI app with /get_map endpoint
│   └── requirements.txt        # Python dependencies
├── frontend/                    # TO BE CREATED
└── PRPs/
    └── templates/
```

### Desired Codebase Tree
```bash
.
├── Backend/                     # Existing - no changes
├── frontend/                    # NEW - React application
│   ├── public/
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── components/
│   │   │   ├── MatrixGrid.jsx  # Grid display component
│   │   │   ├── MatrixCell.jsx  # Individual cell component with tooltip
│   │   │   └── LoadingState.jsx # Loading indicator
│   │   ├── hooks/
│   │   │   └── useMatrixData.js # Custom hook for API data fetching
│   │   ├── main.jsx            # React entry point
│   │   └── index.css           # Tailwind imports
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
└── PRPs/

Responsibility:
- App.jsx: Root component, orchestrates MatrixGrid and error/loading states
- MatrixGrid.jsx: Renders the 200x200 grid, manages grid layout
- MatrixCell.jsx: Individual cell with value display and tooltip configuration
- LoadingState.jsx: Reusable loading spinner/message component
- useMatrixData.js: Encapsulates API call logic, loading/error states
```

### Known Gotchas & Library Quirks
```javascript
// CRITICAL: FastAPI CORS setup
// The backend already has CORS enabled with allow_origins=["*"]
// Frontend can call http://localhost:8000/get_map directly

// CRITICAL: Matrix data structure
// API returns: { status, shape: [200, 200, 3], data: [[[val,val,val]]], layers: [...] }
// data is a 3D array: data[i][j] = [mask, soil_moisture, soil_temperature]
// Access pattern: data[row][col][layer]

// CRITICAL: Performance consideration
// 200x200 = 40,000 cells to render
// Start simple - if slow, consider:
//   1. React.memo for MatrixCell
//   2. Virtualization with react-window
//   3. Canvas rendering instead of DOM elements

// CRITICAL: Tailwind blue colors
// Use semantic classes: text-blue-600 for main values
// Consider bg-blue-50 for cell backgrounds to show grid structure

// CRITICAL: Tooltip library setup (react-tooltip)
// 1. Import: import { Tooltip } from 'react-tooltip'
// 2. Add <Tooltip id="matrix-cell" /> once in parent
// 3. Use data-tooltip-id="matrix-cell" and data-tooltip-html on cells
// 4. HTML content must be encoded properly

// GOTCHA: useEffect dependency array
// Use empty [] for mount-only effect when fetching data
// Example: useEffect(() => { fetchData(); }, []);

// GOTCHA: Vite dev server proxy (optional)
// Can proxy /get_map to avoid hardcoding localhost:8000
// In vite.config.js:
// server: { proxy: { '/api': 'http://localhost:8000' } }
```

## Implementation Blueprint

### Data Models and Structure

**API Response Type:**
```typescript
// Create types for type safety (optional - can use PropTypes instead)
interface MatrixResponse {
  status: string;
  shape: [number, number, number];
  data: number[][][];  // [row][col][layer]
  layers: string[];     // ["mask", "soil_moisture", "soil_temperature"]
}

interface CellData {
  row: number;
  col: number;
  values: [number, number, number]; // [mask, moisture, temp]
}
```

**Component Props:**
```typescript
// MatrixGrid props
interface MatrixGridProps {
  data: number[][][];
  layers: string[];
}

// MatrixCell props
interface MatrixCellProps {
  row: number;
  col: number;
  values: [number, number, number];
  layers: string[];
}
```

### List of Tasks in Order

```yaml
Task 1: Initialize React + Vite Project
  - Navigate to project root
  - Run: npm create vite@latest frontend -- --template react
  - cd frontend && npm install
  - Test: npm run dev (should see Vite + React page)

Task 2: Install Dependencies
  - Install Tailwind CSS: npm install -D tailwindcss postcss autoprefixer
  - Initialize Tailwind: npx tailwindcss init -p
  - Install tooltip library: npm install react-tooltip
  - Verify package.json has all dependencies

Task 3: Configure Tailwind CSS
  - UPDATE tailwind.config.js:
    - Set content: ["./index.html", "./src/**/*.{js,jsx}"]
  - UPDATE src/index.css:
    - Add Tailwind directives: @tailwind base; @tailwind components; @tailwind utilities;
  - Test: Add a blue text class to App.jsx and verify styling works

Task 4: Create Custom Hook for API Data Fetching
  - CREATE src/hooks/useMatrixData.js
  - Implement useState for data, loading, error states
  - Implement useEffect to fetch from http://localhost:8000/get_map on mount
  - Handle fetch errors with try/catch
  - Return { data, loading, error }
  - PATTERN: Follow standard React hooks conventions

Task 5: Create Loading State Component
  - CREATE src/components/LoadingState.jsx
  - Display centered spinner or "Loading matrix data..." message
  - Use Tailwind for styling (flex, items-center, justify-center)
  - Keep it simple - can use animated div or just text

Task 6: Create MatrixCell Component
  - CREATE src/components/MatrixCell.jsx
  - Accept props: { row, col, values, layers }
  - Render a div with:
    - Blue text color (text-blue-600)
    - Border for cell separation (border border-gray-300)
    - Display values[0] (mask value) or values[1] (moisture) - decide on display strategy
    - Padding and text sizing for readability
  - Add tooltip data attributes:
    - data-tooltip-id="matrix-cell"
    - data-tooltip-html with formatted layer info
  - CRITICAL: Format HTML content properly for tooltip

Task 7: Create MatrixGrid Component
  - CREATE src/components/MatrixGrid.jsx
  - Accept props: { data, layers }
  - Use grid layout (CSS Grid or flex with flex-wrap)
  - Map through data array: data.map((row, i) => row.map((cell, j) => ...))
  - Render MatrixCell for each cell with appropriate props
  - Add Tooltip component once: <Tooltip id="matrix-cell" />
  - PATTERN: Keep grid responsive - may need overflow-scroll container
  - CRITICAL: Consider performance - 40,000 cells

Task 8: Update App.jsx
  - REPLACE default Vite content
  - Import useMatrixData hook
  - Import MatrixGrid, LoadingState components
  - Conditional rendering:
    - if (loading) return <LoadingState />
    - if (error) return <ErrorMessage />
    - if (data) return <MatrixGrid data={data} layers={layers} />
  - Add minimal layout wrapper with Tailwind
  - PATTERN: Clean, simple component structure

Task 9: Clean Up and Styling
  - Remove default Vite assets and unused files
  - Ensure consistent blue color scheme
  - Add container max-width if needed
  - Test responsive behavior
  - Verify grid scrolls if too large for viewport

Task 10: Test Integration with Backend
  - PREREQUISITE: Start backend server (cd Backend && uvicorn main:app --reload)
  - Start frontend: npm run dev
  - Verify API call succeeds in Network tab
  - Check console for any errors
  - Test hover tooltips on multiple cells
  - Verify correct data displays in tooltips

Task 11: Error Handling and Edge Cases
  - Test with backend stopped (should show error state)
  - Handle empty data gracefully
  - Add user-friendly error messages
  - Consider retry mechanism (optional)
```

### Pseudocode with Critical Details

```javascript
// Task 4: useMatrixData.js - API Data Fetching Hook
import { useState, useEffect } from 'react';

export function useMatrixData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // PATTERN: Async function inside useEffect
    const fetchData = async () => {
      try {
        setLoading(true);
        // CRITICAL: Replace with actual backend URL
        const response = await fetch('http://localhost:8000/get_map');

        // GOTCHA: Check response.ok before parsing JSON
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const result = await response.json();

        // CRITICAL: Validate response structure
        if (!result.data || !result.layers) {
          throw new Error('Invalid response format');
        }

        setData(result);
        setError(null);
      } catch (err) {
        // PATTERN: User-friendly error messages
        setError(err.message || 'Failed to load matrix data');
        console.error('Matrix data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []); // CRITICAL: Empty dependency array for mount-only fetch

  return { data, loading, error };
}

// Task 6: MatrixCell.jsx - Individual Cell with Tooltip
import React from 'react';

export function MatrixCell({ row, col, values, layers }) {
  // CRITICAL: Destructure values array
  const [mask, moisture, temperature] = values;

  // PATTERN: Format tooltip content as HTML
  const tooltipContent = `
    <div class="p-2">
      <div class="font-bold mb-1">Cell [${row}, ${col}]</div>
      <div>${layers[0]}: ${mask}</div>
      <div>${layers[1]}: ${moisture.toFixed(4)}</div>
      <div>${layers[2]}: ${temperature.toFixed(4)}</div>
    </div>
  `;

  // DECISION: Display primary value (moisture or mask?)
  const displayValue = mask === 0 ? '·' : moisture.toFixed(2);

  return (
    <div
      className="text-blue-600 border border-gray-200 p-1 text-xs text-center cursor-pointer hover:bg-blue-50"
      data-tooltip-id="matrix-cell"
      data-tooltip-html={tooltipContent}
    >
      {displayValue}
    </div>
  );
}

// Task 7: MatrixGrid.jsx - Grid Layout
import React from 'react';
import { Tooltip } from 'react-tooltip';
import { MatrixCell } from './MatrixCell';

export function MatrixGrid({ data, layers }) {
  // CRITICAL: data.data contains the 3D array
  const matrix = data.data;

  return (
    <div className="p-4 overflow-auto max-h-screen">
      {/* PATTERN: CSS Grid for uniform cell sizing */}
      <div
        className="grid gap-0"
        style={{
          gridTemplateColumns: `repeat(${matrix[0].length}, minmax(20px, 1fr))`,
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
            />
          ))
        )}
      </div>

      {/* CRITICAL: Single Tooltip instance for all cells */}
      <Tooltip id="matrix-cell" />
    </div>
  );
}

// Task 8: App.jsx - Main Application
import React from 'react';
import { useMatrixData } from './hooks/useMatrixData';
import { MatrixGrid } from './components/MatrixGrid';
import { LoadingState } from './components/LoadingState';

function App() {
  const { data, loading, error } = useMatrixData();

  // PATTERN: Early returns for loading/error states
  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600 text-center">
          <h2 className="text-xl font-bold mb-2">Error Loading Data</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div>No data available</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-2xl font-bold">Farm It - Matrix Visualization</h1>
        <p className="text-sm">Grid Size: {data.shape[0]}x{data.shape[1]}</p>
      </header>

      <MatrixGrid data={data} layers={data.layers} />
    </div>
  );
}

export default App;
```

### Integration Points
```yaml
BACKEND:
  - endpoint: http://localhost:8000/get_map
  - method: GET
  - no authentication required
  - CORS already enabled
  - expected response time: < 2s

FRONTEND SETUP:
  - directory: ./frontend/
  - dev server: npm run dev (default: http://localhost:5173)
  - build: npm run build
  - preview: npm run preview

ENVIRONMENT:
  - No .env needed initially
  - Optional: Add VITE_API_URL for configurable backend URL
  - Pattern: import.meta.env.VITE_API_URL in Vite

DEPENDENCIES:
  - Core: react, react-dom
  - Build: vite, @vitejs/plugin-react
  - Styling: tailwindcss, autoprefixer, postcss
  - UI: react-tooltip
  - Optional: prop-types for runtime type checking
```

## Validation Loop

### Level 1: Setup & Dependencies
```bash
# After Task 1-3, verify setup:
cd frontend
npm run dev

# Expected: Vite dev server starts on http://localhost:5173
# Browser should show Vite + React page (before customization)

# Verify Tailwind works:
# Add className="text-blue-600" to any element in App.jsx
# Expected: Text appears blue in browser
```

### Level 2: Component Development
```bash
# After each component (Tasks 4-7), test in isolation:

# Test useMatrixData hook:
# - Add console.log in App.jsx to see { data, loading, error }
# - Expected: loading true -> false, data populated

# Test MatrixCell:
# - Render single cell with mock data
# - Expected: Blue text, border visible, hover shows tooltip

# If errors: Check browser console for detailed error messages
```

### Level 3: Integration Testing
```bash
# Start backend (separate terminal):
cd Backend
python -m uvicorn main:app --reload
# Expected: Server running on http://localhost:8000

# Start frontend:
cd frontend
npm run dev
# Expected: Dev server on http://localhost:5173

# Browser checks:
# 1. Open http://localhost:5173
# 2. Open DevTools Network tab
# 3. Verify GET request to /get_map succeeds (200 status)
# 4. Verify grid renders (should see 200x200 cells)
# 5. Hover over cells - tooltip should appear with layer data
# 6. Check console for no errors/warnings

# If grid doesn't appear:
# - Check Network tab for failed requests
# - Check Console for React errors
# - Verify backend is running and returning data
```

### Level 4: Build Validation
```bash
# Build for production:
cd frontend
npm run build

# Expected output: dist/ directory created, no build errors

# Preview production build:
npm run preview
# Expected: Preview server starts, app works same as dev

# If build fails:
# - Check for unused imports
# - Verify all dependencies in package.json
# - Check for any ESLint errors
```

## Final Validation Checklist
- [ ] Backend running: `cd Backend && uvicorn main:app --reload`
- [ ] Frontend dev server: `cd frontend && npm run dev`
- [ ] Grid displays 200x200 cells with blue text
- [ ] Hovering cells shows tooltip with 3 layers of data
- [ ] Loading state appears briefly on initial load
- [ ] Error state appears when backend is offline
- [ ] No console errors in browser DevTools
- [ ] Production build succeeds: `npm run build`
- [ ] Preview build works: `npm run preview`
- [ ] Code is modular and follows React best practices
- [ ] Tailwind classes applied consistently

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode matrix dimensions - use data.shape from API
- ❌ Don't render all cells if performance is poor - consider virtualization
- ❌ Don't use inline styles when Tailwind classes exist
- ❌ Don't fetch data on every render - use useEffect with empty deps
- ❌ Don't ignore loading/error states - users need feedback
- ❌ Don't use deprecated lifecycle methods - use hooks
- ❌ Don't forget key prop when mapping arrays
- ❌ Don't mutate state directly - use setState functions
- ❌ Don't skip the build test - catch issues before deployment
- ❌ Don't over-engineer - start simple, optimize if needed

## Performance Considerations
```yaml
Initial Approach:
  - Render all 40,000 cells as DOM elements
  - Simple CSS Grid layout
  - Standard hover tooltips

If Performance Issues Arise:
  - Option 1: React.memo on MatrixCell to prevent unnecessary re-renders
  - Option 2: Virtualization with react-window (only render visible cells)
  - Option 3: Canvas rendering instead of DOM (more complex)
  - Option 4: Reduce grid size or implement zoom/pan

Optimization Order:
  1. Test with full grid first
  2. Profile with React DevTools
  3. Apply React.memo if needed
  4. Consider virtualization only if memo insufficient
```

## Confidence Score
**9/10** - High confidence for one-pass implementation success

**Reasoning:**
- ✅ Clear, well-defined API contract with existing backend
- ✅ Comprehensive documentation and examples provided
- ✅ Modern, well-documented tech stack (React, Vite, Tailwind)
- ✅ Step-by-step task breakdown with validation gates
- ✅ Performance considerations addressed
- ⚠️ Minor risk: 40,000 cell rendering may need optimization (addressed in optional tasks)

**Risk Mitigation:**
- Start with simple implementation and optimize if needed
- Clear validation checkpoints at each stage
- Detailed pseudocode prevents common mistakes
- Known gotchas documented upfront
