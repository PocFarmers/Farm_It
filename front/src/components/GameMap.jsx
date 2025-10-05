import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet'
import { useState, useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import { ZONE_COLORS, ZONE_CONFIGS } from '../utils/constants'
import ParcelPopup from './ParcelPopup'
import TifOverlay from './TifOverlay'
import TifValueDisplay from './TifValueDisplay'

export default function GameMap({ parcels, onActionExecuted }) {
    const [geojsonData, setGeojsonData] = useState(null)
    const [parcelPolygons, setParcelPolygons] = useState([])
    const [selectedTifFile, setSelectedTifFile] = useState(null)
    const [tifData, setTifData] = useState(null)
    const mapRef = useRef(null)

    // Load the North Africa GeoJSON data
    useEffect(() => {
        fetch('/data/masks/farmit_amazon_central_bean.geojson')
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`)
                }
                return res.json()
            })
            .then(data => {
                console.log('GeoJSON loaded:', data)
                setGeojsonData(data)
                // Create parcel polygons from the GeoJSON shape
                createParcelPolygons(data, parcels)
            })
            .catch(err => {
                console.error('Error loading GeoJSON:', err)
                // Try alternative path
                fetch('./data/masks/farmit_north_africa_arid_biskra_bean.geojson')
                    .then(res => res.json())
                    .then(data => {
                        console.log('GeoJSON loaded from alternative path:', data)
                        setGeojsonData(data)
                        createParcelPolygons(data, parcels)
                    })
                    .catch(err2 => console.error('Error loading GeoJSON from alternative path:', err2))
            })
    }, [parcels])

    // Function to calculate bounds from GeoJSON
    const calculateGeoJSONBounds = (geojsonData) => {
        if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
            return null
        }

        let minLat = Infinity, maxLat = -Infinity
        let minLon = Infinity, maxLon = -Infinity

        geojsonData.features.forEach(feature => {
            if (feature.geometry && feature.geometry.coordinates) {
                const coordinates = feature.geometry.coordinates

                // Handle different geometry types
                const processCoordinates = (coords) => {
                    if (Array.isArray(coords[0])) {
                        // Multi-dimensional array (polygon, etc.)
                        coords.forEach(coord => processCoordinates(coord))
                    } else if (coords.length >= 2) {
                        // Single coordinate [lon, lat]
                        const [lon, lat] = coords
                        minLat = Math.min(minLat, lat)
                        maxLat = Math.max(maxLat, lat)
                        minLon = Math.min(minLon, lon)
                        maxLon = Math.max(maxLon, lon)
                    }
                }

                processCoordinates(coordinates)
            }
        })

        return {
            minLat,
            maxLat,
            minLon,
            maxLon
        }
    }

    // Function to create small parcel polygons within the GeoJSON shape
    const createParcelPolygons = (geojsonData, parcels) => {
        if (!geojsonData || !parcels || parcels.length === 0) return

        const polygon = geojsonData.features[0].geometry.coordinates[0]

        // Find bounding box of the polygon
        const lats = polygon.map(coord => coord[1])
        const lngs = polygon.map(coord => coord[0])
        const minLat = Math.min(...lats)
        const maxLat = Math.max(...lats)
        const minLng = Math.min(...lngs)
        const maxLng = Math.max(...lngs)

        // Create grid of small polygons within the bounding box
        const gridSize = 0.005 // Smaller grid for more parcels
        const parcelPolygons = []

        for (let i = 0; i < parcels.length; i++) {
            const parcel = parcels[i]

            // Calculate grid position
            const row = Math.floor(i / 10)
            const col = i % 10

            const lat = minLat + (row * gridSize)
            const lng = minLng + (col * gridSize)

            // Create small square polygon
            const parcelPolygon = [
                [lng, lat],
                [lng + gridSize, lat],
                [lng + gridSize, lat + gridSize],
                [lng, lat + gridSize],
                [lng, lat]
            ]

            // Check if this parcel is within the main polygon (simplified check)
            const isInside = isPointInPolygon([lng + gridSize / 2, lat + gridSize / 2], polygon)

            if (isInside) {
                parcelPolygons.push({
                    ...parcel,
                    polygon: parcelPolygon
                })
            }
        }

        setParcelPolygons(parcelPolygons)
    }

    // Simple point-in-polygon test
    const isPointInPolygon = (point, polygon) => {
        const [x, y] = point
        let inside = false

        for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            const [xi, yi] = polygon[i]
            const [xj, yj] = polygon[j]

            if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
                inside = !inside
            }
        }

        return inside
    }

    const getParcelStyle = (parcel) => {
        const baseColor = parcel.owned ? '#2196F3' : ZONE_COLORS[parcel.zone_id] || '#ccc'
        return {
            color: parcel.owned ? '#2196F3' : '#333',
            weight: parcel.owned ? 3 : 1,
            fillColor: baseColor,
            fillOpacity: parcel.owned ? 0.6 : 0.3
        }
    }

    // Available TIF files
    const tifFiles = [
        { name: 'Temperature (Arid)', url: '/data/tif/aride_MOD11A2.061_LST_Day_1km_doy2023361000000_aid0001.tif' },
        { name: 'Soil Moisture (Arid)', url: '/data/tif/aride_SPL3SMP_E.006_Soil_Moisture_Retrieval_Data_PM_soil_moisture_pm_doy2024132000000_aid0001.tif' },
        { name: 'Temperature (Cold)', url: '/data/tif/froide_MOD11A2.061_LST_Day_1km_doy2023361000000_aid0001.tif' },
        { name: 'Soil Moisture (Cold)', url: '/data/tif/froide_SPL3SMP_E.006_Soil_Moisture_Retrieval_Data_PM_soil_moisture_pm_doy2024132000000_aid0001.tif' },
        { name: 'Temperature (Temperate)', url: '/data/tif/tempere_MOD11A2.061_LST_Day_1km_doy2023361000000_aid0001.tif' },
        { name: 'Soil Moisture (Temperate)', url: '/data/tif/tempere_SPL3SMP_E.006_Soil_Moisture_Retrieval_Data_PM_soil_moisture_pm_doy2024132000000_aid0001.tif' },
        { name: 'Temperature (Tropical)', url: '/data/tif/tropicale_MOD11A2.061_LST_Day_1km_doy2023361000000_aid0001.tif' },
        { name: 'Soil Moisture (Tropical)', url: '/data/tif/tropicale_SPL3SMP_E.006_Soil_Moisture_Retrieval_Data_PM_soil_moisture_pm_doy2024132000000_aid0001.tif' }
    ]

    return (
        <div className="h-full w-full">
            {/* Debug info */}
            {geojsonData && (
                <div className="absolute top-2 left-2 bg-black/70 text-white p-2 rounded z-[1000]">
                    GeoJSON loaded: {geojsonData.features?.length || 0} features
                </div>
            )}

            {/* TIF file selector */}
            <div className="absolute top-2 left-1/2 transform -translate-x-1/2 bg-black/70 text-white p-2 rounded z-[1000]">
                <select
                    value={selectedTifFile || ''}
                    onChange={(e) => setSelectedTifFile(e.target.value)}
                    className="bg-gray-800 text-white px-2 py-1 rounded"
                >
                    <option value="">Select TIF data to display</option>
                    {tifFiles.map((file, index) => (
                        <option key={index} value={file.url}>{file.name}</option>
                    ))}
                </select>
            </div>

            <MapContainer
                center={[-3.1190, -60.0217]}  // Amazon Central coordinates
                zoom={10}
                className="h-full w-full"
                ref={mapRef}
            >
                <TileLayer
                    attribution='&copy; OpenStreetMap contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Render the North Africa GeoJSON mask */}
                {geojsonData && (
                    <GeoJSON
                        data={geojsonData}
                        style={{
                            color: '#0066cc',
                            weight: 3,
                            fillColor: '#0066cc',
                            fillOpacity: 0.4
                        }}
                    />
                )}

                {/* Render parcels as simple rectangles for now */}
                {parcels.map(parcel => (
                    <GeoJSON
                        key={parcel.id}
                        data={{
                            type: "Feature",
                            geometry: {
                                type: "Polygon",
                                coordinates: [[
                                    [parcel.lng, parcel.lat],
                                    [parcel.lng + 0.001, parcel.lat],
                                    [parcel.lng + 0.001, parcel.lat + 0.001],
                                    [parcel.lng, parcel.lat + 0.001],
                                    [parcel.lng, parcel.lat]
                                ]]
                            }
                        }}
                        style={getParcelStyle(parcel)}
                    >
                        <Popup>
                            <ParcelPopup
                                parcel={parcel}
                                onActionExecuted={onActionExecuted}
                            />
                        </Popup>
                    </GeoJSON>
                ))}

                {/* TIF data overlay */}
                {selectedTifFile && geojsonData && (() => {
                    const bounds = calculateGeoJSONBounds(geojsonData)
                    return (
                        <>
                            <TifOverlay
                                tifUrl={selectedTifFile}
                                mapRef={mapRef}
                                opacity={0.8}
                                onTifDataLoaded={setTifData}
                                geojsonBounds={bounds ? {
                                    minLat: bounds.minLat,
                                    maxLat: bounds.maxLat,
                                    minLon: bounds.minLon,
                                    maxLon: bounds.maxLon
                                } : null}
                                geojsonData={geojsonData}
                            />
                            <TifValueDisplay
                                tifData={tifData}
                                mapRef={mapRef}
                                isVisible={!!selectedTifFile}
                            />
                        </>
                    )
                })()}
            </MapContainer>
        </div>
    )
}
