import { useState, useEffect } from 'react'

export default function TifValueDisplay({ tifData, mapRef, isVisible }) {
    const [clickedValue, setClickedValue] = useState(null)
    const [clickedPosition, setClickedPosition] = useState(null)

    useEffect(() => {
        if (!tifData || !mapRef?.current || !isVisible) return

        const map = mapRef.current

        const handleMapClick = (e) => {
            const { lat, lng } = e.latlng

            // Convert lat/lng to pixel coordinates
            const { bbox, width, height } = tifData
            const { minX, minY, maxX, maxY } = bbox

            // Calculate pixel position
            const pixelX = Math.floor(((lng - minX) / (maxX - minX)) * width)
            const pixelY = Math.floor(((maxY - lat) / (maxY - minY)) * height)

            // Check if click is within bounds
            if (pixelX >= 0 && pixelX < width && pixelY >= 0 && pixelY < height) {
                const pixelIndex = pixelY * width + pixelX
                const value = tifData.data[pixelIndex]

                if (!isNaN(value) && value !== -9999) {
                    setClickedValue(value)
                    setClickedPosition({ lat, lng })
                }
            }
        }

        map.on('click', handleMapClick)

        return () => {
            map.off('click', handleMapClick)
        }
    }, [tifData, mapRef, isVisible])

    if (!isVisible || !clickedValue) return null

    return (
        <div className="absolute bottom-4 left-4 bg-black/80 text-white p-3 rounded-lg z-[1000] max-w-xs">
            <h3 className="font-bold mb-2">TIF Value at Click</h3>
            <div className="text-sm space-y-1">
                <div><strong>Value:</strong> {clickedValue.toFixed(2)}</div>
                <div><strong>Position:</strong> {clickedPosition?.lat.toFixed(4)}, {clickedPosition?.lng.toFixed(4)}</div>
                <div><strong>Min:</strong> {tifData.stats.min.toFixed(2)}</div>
                <div><strong>Max:</strong> {tifData.stats.max.toFixed(2)}</div>
                <div><strong>Mean:</strong> {tifData.stats.mean.toFixed(2)}</div>
            </div>
            <button
                onClick={() => setClickedValue(null)}
                className="mt-2 px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700"
            >
                Close
            </button>
        </div>
    )
}
