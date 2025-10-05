FEATURE
Core Entities

Tile (parcel)

id: grid index

zoneId: integer (1=cold, 2=arid, 3=tropical, 4=temperate)

type: "forest" | "field" | "empty"

owner: null | "player"

tileState: "seed" | "growing" | "harvest" (only for planted fields)

hasWaterReserve: boolean → irrigates adjacent fields once per step

hasFirebreak: boolean

temperature: float (from temperature layer)

humidity: float (from humidity layer)

lastIrrigatedStep: int

irrigatedThisStep: bool

exploited: "conserve" | "exploit" (for forests — conserved forests provide fertilizer to adjacent fields)

Player (single, local)

resources:

shovels (int)

drops (int)

score (int)

tilesOwned: list of tile IDs

Initial inventory: 3 owned empty fields

Game Loop

Each step (triggered by “Next Step”):

shovels += 1
drops += 1
score += 10


Crop cycle: seed → growing → harvest (advances every 4 steps)

If not irrigated this step and no adjacent water reserve → crop dies (tile becomes "empty")

Player Actions
Action	Cost	Effect
Buy Water Reserve	3 shovels	hasWaterReserve = true
Buy Firebreak	3 shovels	hasFirebreak = true
Buy Tile	2 shovels	owner = player
Manual Irrigation	1 drop	irrigatedThisStep = true
Fertilizer	1 shovel	apply fertilizer to target tile
Map & Spatial Data

Replace OSM with matrix or GeoJSON layers + .tif

Base (RGB): 3 static .tif files

Temporal layers: temperature/ and humidity/ folders (fixed per step)

Each tile reads temperature and humidity values from layers

Zones: defined in GeoJSON/matrix via zoneId

UI

Top-right: display resources (icons for shovels, drops, score)

Right-center: show current step, #fields, #forests (conserved/exploited), crop counts by type

Tile popup (on click):

Display temperature, humidity, zone, type, state

Buttons: buy, irrigate, fertilize, buy water reserve, buy firebreak, plant

Backend

Stack: FastAPI + SQLite/Postgres (local)

Auto-save: save full game state each step

Endpoints:

GET /game/load → load local state

POST /game/save → save full state (player + tiles + step)

POST /game/next-step → compute next step (resources, cycles, effects, deaths, increment step)

POST /tile/:id/action → apply action (buy, irrigate, fertilize, etc.)

Single-player only (no multiplayer logic).

Visualization

Tiles colored by state: seed / growing / harvest / empty / owned / unowned

Icons for water reserves and firebreaks

Show temperature and humidity in popup

DOCUMENTATION
Time & Progression

1 step = 8 simulated days

50 steps = 1 year (game lasts 50 steps)

Game advances only when the player clicks “Next Step”

No failure state → always continues to 50 steps

Objective: have the largest farm at the end (by owned tiles & maintained crops)

Local Effects

Conserved forests: +1 fertilizer per step to each adjacent planted field

Water reserves: auto-irrigate adjacent planted fields once per step

Manual irrigation: irrigates target tile for the current step only

EXAMPLE
Example Game State (JSON)
{
  "step": 1,
  "player": {
    "shovels": 3,
    "drops": 3,
    "score": 0,
    "tilesOwned": [12, 45, 78]
  },
  "tiles": [
    {
      "id": 12,
      "zoneId": "tropical",
      "type": "field",
      "owner": "player",
      "tileState": "seed",
      "hasWaterReserve": false,
      "hasFirebreak": false,
      "temperature": 30.2,
      "humidity": 0.72,
      "lastIrrigatedStep": 0
    }
  ]
}

OTHER CONSIDERATION

Define harvest rewards (shovels, score, or other bonuses).

Decide adjacency logic → use 8-neighbor rule (recommended).

When buying an empty parcel → becomes owned but remains "empty" until planted.

Define timing between harvest and reset to "empty" (currently: manual or automatic after harvest).

Each step triggers:

Resource generation

Crop state transitions

Forest and water reserve effects

Crop death check

Auto-save