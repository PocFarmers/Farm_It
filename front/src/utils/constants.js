export const ZONE_COLORS = {
    tropical: '#ff6b6b',
    cold: '#4dabf7',
    arid: '#ffd43b',
    temperate: '#51cf66'
}

export const CROP_ICONS = {
    potato: '🥔',
    banana: '🍌',
    sorghum: '🌾'
}

export const GAME_ID = 1  // Single game for MVP

// Zone configurations with proper coordinates and GeoJSON files
export const ZONE_CONFIGS = {
    temperate: {
        name: 'Paris, France',
        center: [48.8566, 2.3522],
        zoom: 10,
        geojsonFile: '/data/masks/farmit_paris_bean.geojson'
    },
    arid: {
        name: 'Biskra, Algeria',
        center: [34.85, 6.11],
        zoom: 10,
        geojsonFile: '/data/masks/farmit_north_africa_arid_biskra_bean.geojson'
    },
    tropical: {
        name: 'Kinshasa-Brazzaville, Congo',
        center: [-4.4419, 15.2663],
        zoom: 10,
        geojsonFile: '/data/masks/farmit_kinshasa_brazzaville_bean.geojson'
    },
    cold: {
        name: 'Amazon Central, Brazil',
        center: [-3.1190, -60.0217],
        zoom: 10,
        geojsonFile: '/data/masks/farmit_amazon_central_bean.geojson'
    }
}
