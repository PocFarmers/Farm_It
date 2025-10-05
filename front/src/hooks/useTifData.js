import { useState, useEffect } from 'react'
import { fromUrl } from 'geotiff'

export function useTifData(tifUrl) {
    const [tifData, setTifData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!tifUrl) return

        const loadTifData = async () => {
            setLoading(true)
            setError(null)
            
            try {
                console.log('Loading TIF from URL:', tifUrl)
                const tiff = await fromUrl(tifUrl)
                console.log('TIF loaded successfully')
                
                const image = await tiff.getImage()
                console.log('Image loaded, dimensions:', image.getWidth(), 'x', image.getHeight())
                
                const rasters = await image.readRasters()
                console.log('Rasters loaded, bands:', rasters.length)
                
                // Get the first band (usually the data we want)
                const data = rasters[0]
                const width = image.getWidth()
                const height = image.getHeight()
                
                // Get geospatial information
                const bbox = image.getBoundingBox()
                const [minX, minY, maxX, maxY] = bbox
                console.log('Bounding box:', { minX, minY, maxX, maxY })
                
                // Calculate statistics
                const validData = data.filter(value => !isNaN(value) && value !== -9999)
                const min = Math.min(...validData)
                const max = Math.max(...validData)
                const mean = validData.reduce((sum, val) => sum + val, 0) / validData.length
                
                console.log('TIF statistics:', { min, max, mean, validCount: validData.length, total: data.length })
                
                setTifData({
                    data,
                    width,
                    height,
                    bbox: { minX, minY, maxX, maxY },
                    stats: { min, max, mean },
                    validDataCount: validData.length,
                    totalPixels: data.length
                })
            } catch (err) {
                console.error('Error loading TIF data:', err)
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }

        loadTifData()
    }, [tifUrl])

    return { tifData, loading, error }
}
