import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet'
import { useState, useEffect } from 'react'
import 'leaflet/dist/leaflet.css'
import { ZONE_COLORS } from '../utils/constants'
import ParcelPopup from './ParcelPopup'

export default function GameMap({ parcels, onActionExecuted }) {
    const [geojsonData, setGeojsonData] = useState(null)

    // Load GeoJSON data (for now, use one zone as example)
    useEffect(() => {
        fetch('/data/masks/farmit_paris_bean.geojson')  // Adjust path based on zone
            .then(res => res.json())
            .then(data => setGeojsonData(data))
    }, [])

    const getParcelStyle = (parcel) => {
        const baseColor = parcel.owned ? '#2196F3' : ZONE_COLORS[parcel.zone_id] || '#ccc'
        return {
            color: parcel.owned ? '#2196F3' : '#333',
            weight: parcel.owned ? 3 : 1,
            fillColor: baseColor,
            fillOpacity: parcel.owned ? 0.6 : 0.3
        }
    }

    return (
        <div className="h-full w-full">
            <MapContainer
                center={[48.8566, 2.3522]}  // Paris coords, adjust per zone
                zoom={10}
                className="h-full w-full"
            >
                <TileLayer
                    attribution='&copy; OpenStreetMap contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Render parcels as rectangles */}
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
            </MapContainer>
        </div>
    )
}
