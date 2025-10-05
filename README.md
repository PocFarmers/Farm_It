# Farm_It - Interactive Farming Simulation Game

A web-based farming simulation game built with React, Leaflet, and FastAPI. Manage your farm across 4 climate zones, grow crops, and adapt to environmental conditions based on real NASA satellite data.

## 🎮 Game Overview

- **Objective**: Build the largest sustainable farm over 50 stages (1 year of game time)
- **Gameplay**: Turn-based strategy with resource management and crop lifecycle
- **Climate Zones**: Cold, Arid, Tropical, Temperate (each with unique conditions)
- **Crops**: Potato, Banana, Sorghum (each with different growth requirements)
- **Resources**: Shovels (currency), Water Drops, Score

## 📁 Project Structure

```
Farm_It/
├── Backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic validation schemas
│   ├── crud.py          # Database operations
│   ├── game_logic.py    # Game mechanics (crop lifecycle, events)
│   ├── database.py      # Database configuration
│   ├── in_game/
│   │   └── get_event.py # Event detection logic (drought, fire)
│   ├── data/            # CSV data files
│   │   ├── crop_phenology_thresholds.csv
│   │   └── nasa_event_thresholds.csv
│   ├── requirements.txt
│   ├── .env
│   └── venv/
│
├── Farm_It_frontend/    # React frontend
│   ├── src/
│   │   ├── App.jsx     # Main game component
│   │   └── App.css     # Styles
│   ├── package.json
│   └── .env
│
├── app/                 # Additional resources
│   ├── data/           # NASA satellite data (.tif files)
│   └── index.html      # Reference UI design
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.8+ with pip
- **Frontend**: Node.js 18+ with npm
- **Browser**: Modern browser with JavaScript enabled

### Backend Setup

```bash
# Navigate to Backend directory
cd Backend

# Activate virtual environment (already exists)
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python main.py
```

Backend will start at **http://localhost:8000**
- API docs (Swagger): http://localhost:8000/docs

### Frontend Setup

```bash
# Navigate to Frontend directory
cd Farm_It_frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start at **http://localhost:5173**

## 🎯 How to Play

1. **Starting the Game**: Frontend automatically loads or creates a new game
2. **Your Farm**: You start with 3 owned parcels
3. **View Parcels**: Click on any tile on the map to see details and actions
4. **Actions**:
   - **Buy Parcel** (2 shovels): Expand your farm
   - **Plant Crop** (free): Choose potato, banana, or sorghum
   - **Irrigate** (1 water drop): Help crops survive
   - **Buy Water Reserve** (3 shovels): Automatically irrigates adjacent fields
   - **Buy Firebreak** (3 shovels): Protect against fire events
5. **Progress Stage**: Click "Next Stage" button to advance time
   - Each stage = 8 days of game time
   - Gain +1 shovel and +1 water drop per stage
   - Crops advance through lifecycle: seed → growing → harvest (4 stages each)
6. **Scoring**:
   - +10 points per crop harvested
   - +2 points per preserved forest per stage
   - Goal: Highest score after 50 stages

## 🌾 Crop System

### Crop Lifecycle
- **Seed** (4 stages) → **Growing** (4 stages) → **Harvest** (4 stages)
- Total: 12 stages from planting to harvest
- Crops die if temperature or moisture are out of range

### Crop Requirements (from CSV data)

| Crop | Temperature Range | Moisture Range | Best Zone |
|------|------------------|----------------|-----------|
| Potato | 7-25°C | 0.25-0.7 | Temperate, Cold |
| Banana | 20-38°C | 0.35-0.85 | Tropical |
| Sorghum | 20-38°C | 0.15-0.5 | Arid, Temperate |

## 🌍 Climate Zones

| Zone | Temperature | Moisture | Characteristics |
|------|------------|----------|-----------------|
| Cold | 5°C | 0.4 | Low temp, moderate moisture |
| Arid | 35°C | 0.15 | High temp, low moisture |
| Tropical | 28°C | 0.7 | Warm, high moisture |
| Temperate | 18°C | 0.5 | Moderate conditions |

## 🔥 Environmental Events

Based on NASA event thresholds:
- **Drought**: Triggered by specific temperature/moisture combinations
- **Fire**: Triggered by high heat and low moisture
- Events can damage crops and reduce yields

## 📡 API Endpoints

### Game Management
- `POST /api/game` - Create new game
- `GET /api/game/{game_id}` - Get game state
- `GET /api/parcels/{game_id}` - Get all parcels

### Game Actions
- `POST /api/game/{game_id}/action` - Execute action (buy, plant, irrigate, etc.)
  ```json
  {
    "parcel_id": 1,
    "action": "plant_crop",
    "crop_type": "potato"
  }
  ```

### Stage Progression
- `POST /api/game/{game_id}/next-stage` - Advance to next stage
  - Returns: new stage, events, crop updates, score changes

## 🔧 Technical Details

### Backend Stack
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for SQLite database
- **Pydantic**: Data validation
- **Pandas**: CSV data processing

### Frontend Stack
- **React**: UI framework
- **Leaflet**: Interactive map visualization
- **React-Leaflet**: React bindings for Leaflet
- **Axios**: HTTP client

### Database
- **SQLite**: Development database (farm_it.db)
- **Tables**:
  - `game_state`: Game resources and current stage
  - `parcels`: Parcel data (location, zone, crops, improvements)

## 🎨 UI Features

- **Interactive Map**: Click tiles to interact with parcels
- **Color-coded Zones**: Each climate zone has a distinct color
- **Real-time Updates**: UI updates immediately after actions
- **Dashboard**: View resources and current stage
- **Farm Panel**: Track owned parcels and crops
- **Popup Actions**: Context-specific actions in tile popups

## 🐛 Troubleshooting

### Backend Issues
- **Port 8000 already in use**: Change port in `main.py` or kill existing process
- **Database errors**: Delete `farm_it.db` to start fresh
- **Import errors**: Ensure virtual environment is activated

### Frontend Issues
- **CORS errors**: Check backend `.env` has `CORS_ORIGINS=http://localhost:5173`
- **Map not loading**: Ensure Leaflet CSS is imported in App.jsx
- **API errors**: Verify backend is running on port 8000

### Node Version Issues
- **Vite errors**: If using Node 18, Vite 5.4.11 is installed (compatible)
- **For Node 20+**: Can upgrade to latest Vite version

## 📝 Game Tips

1. **Start Local**: Plant crops suited to your starting zone
2. **Expand Wisely**: Buy adjacent parcels for better management
3. **Preserve Forests**: They provide fertilizer bonuses to adjacent fields
4. **Water Reserves**: Great for drought-prone arid zones
5. **Crop Rotation**: Harvest and replant to maximize score
6. **Watch Events**: Monitor environmental conditions each stage

## 🚧 Known Limitations (MVP)

- TIF raster visualization not implemented (simplified with static zone data)
- Temperature/moisture values are hardcoded per zone
- No multiplayer support
- Single game save (ID 1)
- Events detected but don't affect crops yet
- No visual crop stage indicators on map

## 🔮 Future Enhancements

- [ ] Real-time TIF data visualization
- [ ] Multi-game support with save slots
- [ ] More crop types and varieties
- [ ] Weather patterns and seasons
- [ ] Market system for selling harvests
- [ ] Tutorial and help system
- [ ] Mobile-responsive design
- [ ] Achievements and leaderboards

## 📄 License

Hackathon Project - Educational Use

## 🙏 Credits

- **NASA Data**: Temperature (MODIS LST) and Moisture (SMAP) satellite data
- **Leaflet**: Open-source mapping library
- **FastAPI**: Modern Python web framework
- **React**: UI framework by Meta

---

**Built for the Farm_It Hackathon - October 2025**
