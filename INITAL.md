FEATURE
Connect the functional backend with the frontend to gamify the UI. The backend folder is "Backend" and the frontend folder is "frontend". The frontend is implemented in "frontend".

DOCUMENTATION

Game Principle

Entities & State

Tile

id (grid index)

zoneId (1..4: cold, arid, tropical, temperate)

type (forest | field | virgin)

owner (null | player)

tileState (for crops): seed / growing / harvest (for planted fields)

hasWaterReserve (bool) → irrigates adjacent fields once per step if true

hasFirebreak (bool)

temperature (value from layer)

humidity (value from layer)

lastIrrigatedStep (int)

irrigatedThisStep (bool)

exploited (for forests: conserve | exploit?) → if conserved, gives fertilizer to adjacent fields

Player (unique, local)

resources: shovels (int), drops (int), score (int)

tilesOwned: list of tile IDs

initial inventory: 3 empty plots (3 virgin fields at start)

Resources & Step Generation

Each step ("next step" button):

shovels += 1

drops += 1

score += 10

Actions (cost & effect)

Buy water reserve: cost = 3 shovels → sets hasWaterReserve = true on tile

Buy firebreak: cost = 3 shovels → sets hasFirebreak = true

Buy tile: cost = 2 shovels → owner = player

Irrigate (manual): cost = 1 drop → sets irrigatedThisStep = true on target tile

Fertilizer (manual): cost = 1 shovel → applies fertilizer to target tile

Interaction Rules / Local Effects

Conserved forest (owned or not): gives +1 fertilizer per step to each adjacent planted field

Water reserve: automatically irrigates all adjacent planted fields per step

Manual irrigation: irrigates a target tile for that step

Crop lifecycle: seed → growing → harvest

Transition: every 4 steps, crop moves to next state

If not irrigated (no irrigatedThisStep and no adjacent water reserve), crop dies → tile becomes virgin

Time & Progression

1 step = 8 simulated days

50 steps = 1 year (hard mode = 50 steps)

Game advances only when player clicks "next step"

No failure: game continues until 50 steps

Objective: maximize exploited tiles at end of 50 steps (measure: number of owned tiles / maintained crops)

Map / Spatial Data

OSM replaced by matrix / geojson layers + .tif files:

Base RGB: 3 static .tif files

Temporal layers: temperature/ and humidity/ folders with .tif (values per pixel/cell; fixed per step for now)

Each tile reads its temperature/humidity from respective layer

Zones (cold, arid, tropical, temperate) defined in matrix / geojson (zoneId)

Minimal UI Logic

Display resources at top-right: shovels (shovel icon), drops (drop icon), score (laurel icon)

Right-center: current step, number of fields, number of forests, conserved vs exploited forests, number of crops and types (e.g., wheat, potato, banana)

Tile popup (on click): display temperature, humidity, zone, tile type, states, and applicable action buttons (buy, irrigate, fertilizer, buy water reserve, firebreak, plant if possible)

EXAMPLE

Step click: +1 shovel, +1 drop, +10 score

Player buys water reserve on a virgin field → hasWaterReserve = true

Adjacent fields automatically irrigated during step

Conserved forest adjacent to a field → +1 fertilizer per step applied automatically

OTHER CONSIDERATIONS

Maintain separation of backend logic and frontend UI

All game rules must be respected when connecting backend → frontend

Ensure tile state, resources, and step progression update correctly in the UI