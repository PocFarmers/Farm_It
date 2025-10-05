import { useEffect, useRef } from 'react'
import { useTifData } from '../hooks/useTifData'

export default function TifOverlay({ tifUrl, mapRef, opacity = 0.6, onTifDataLoaded, geojsonBounds = null, geojsonData = null }) {
    const { tifData, loading, error } = useTifData(tifUrl)
    const canvasRef = useRef(null)
    const overlayRef = useRef(null)

    // Function to check if a point is inside a polygon
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

    // Function to convert lat/lon to pixel coordinates
    const latLonToPixel = (lat, lon, bounds, width, height) => {
        const x = ((lon - bounds.minLon) / (bounds.maxLon - bounds.minLon)) * width
        const y = ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * height
        return [Math.round(x), Math.round(y)]
    }

    useEffect(() => {
        if (!tifData || !mapRef?.current) {
            console.log('TifOverlay: Missing tifData or mapRef', { tifData: !!tifData, mapRef: !!mapRef?.current })
            return
        }

        console.log('TifOverlay: Drawing TIF data', tifData)
        const map = mapRef.current
        const canvas = canvasRef.current
        if (!canvas) {
            console.log('TifOverlay: No canvas element')
            return
        }

        // Draw the TIF data on canvas
        const ctx = canvas.getContext('2d')
        canvas.width = tifData.width
        canvas.height = tifData.height
        console.log('TifOverlay: Canvas size set to', canvas.width, 'x', canvas.height)

        // Create image data
        const imageData = ctx.createImageData(tifData.width, tifData.height)
        const data = imageData.data

        // Normalize data to 0-255 range
        const { min, max } = tifData.stats
        const range = max - min

        // Get polygon coordinates for clipping
        let polygon = null
        if (geojsonData && geojsonData.features && geojsonData.features.length > 0) {
            polygon = geojsonData.features[0].geometry.coordinates[0]
            console.log('TifOverlay: Polygon loaded for clipping', polygon.length, 'points')
        }

        console.log('TifOverlay: Processing', tifData.data.length, 'pixels')
        console.log('TifOverlay: Bounds', geojsonBounds)

        for (let i = 0; i < tifData.data.length; i++) {
            const value = tifData.data[i]
            const pixelIndex = i * 4

            if (isNaN(value) || value === -9999) {
                // Transparent for invalid data
                data[pixelIndex] = 0     // R
                data[pixelIndex + 1] = 0 // G
                data[pixelIndex + 2] = 0 // B
                data[pixelIndex + 3] = 0 // A (transparent)
            } else {
                // Check if pixel is inside the GeoJSON polygon
                let shouldShow = true

                // TEMPORAIRE: Désactiver le découpage pour tester
                if (false && polygon && geojsonBounds) {
                    // Convert pixel index to lat/lon
                    const x = i % tifData.width
                    const y = Math.floor(i / tifData.width)

                    // Convert pixel to lat/lon using the bounds
                    const lon = geojsonBounds.minLon + (x / tifData.width) * (geojsonBounds.maxLon - geojsonBounds.minLon)
                    const lat = geojsonBounds.maxLat - (y / tifData.height) * (geojsonBounds.maxLat - geojsonBounds.minLat)

                    // Check if this lat/lon is inside the polygon
                    shouldShow = isPointInPolygon([lon, lat], polygon)
                }

                if (shouldShow) {
                    // Red color for valid data with intensity based on value
                    const normalizedValue = (value - min) / range
                    const intensity = Math.floor(normalizedValue * 255)

                    data[pixelIndex] = 255     // R (always red)
                    data[pixelIndex + 1] = Math.floor(255 * (1 - normalizedValue)) // G (darker red for higher values)
                    data[pixelIndex + 2] = Math.floor(255 * (1 - normalizedValue)) // B (darker red for higher values)
                    data[pixelIndex + 3] = 200 // A (semi-transparent)
                } else {
                    // Transparent for pixels outside the polygon
                    data[pixelIndex] = 0     // R
                    data[pixelIndex + 1] = 0 // G
                    data[pixelIndex + 2] = 0 // B
                    data[pixelIndex + 3] = 0 // A (transparent)
                }
            }
        }

        ctx.putImageData(imageData, 0, 0)

        // Pass tifData to parent component
        if (onTifDataLoaded) {
            onTifDataLoaded(tifData)
        }

        // Create image overlay using Leaflet
        const imageUrl = canvas.toDataURL()

        // Use GeoJSON bounds if provided, otherwise fall back to TIFF bounds
        let bounds
        if (geojsonBounds) {
            // Convert geojsonBounds object to Leaflet format
            bounds = [
                [geojsonBounds.minLat, geojsonBounds.minLon],
                [geojsonBounds.maxLat, geojsonBounds.maxLon]
            ]
        } else {
            // Use TIFF bounds
            bounds = [
                [tifData.bbox.minY, tifData.bbox.minX],
                [tifData.bbox.maxY, tifData.bbox.maxX]
            ]
        }

        console.log('TifOverlay: Using bounds', bounds)

        // Remove existing overlay
        if (overlayRef.current) {
            map.removeLayer(overlayRef.current)
        }

        // Add new overlay
        overlayRef.current = L.imageOverlay(imageUrl, bounds, {
            opacity: opacity,
            interactive: false
        }).addTo(map)

        return () => {
            if (overlayRef.current) {
                map.removeLayer(overlayRef.current)
            }
        }
    }, [tifData, mapRef, opacity])

    if (loading) {
        return <div className="absolute top-2 right-2 bg-black/70 text-white p-2 rounded z-[1000]">
            Loading TIF data...
        </div>
    }

    if (error) {
        return <div className="absolute top-2 right-2 bg-red-500/70 text-white p-2 rounded z-[1000]">
            Error: {error}
        </div>
    }

    if (tifData) {
        return (
            <div className="absolute top-2 right-2 bg-black/70 text-white p-2 rounded z-[1000]">
                <div className="text-sm">
                    <div>Min: {tifData.stats.min.toFixed(2)}</div>
                    <div>Max: {tifData.stats.max.toFixed(2)}</div>
                    <div>Mean: {tifData.stats.mean.toFixed(2)}</div>
                    <div>Valid pixels: {tifData.validDataCount}</div>
                </div>
                <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>
        )
    }

    return null
}
