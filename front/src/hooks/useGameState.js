import { useState, useEffect } from 'react'
import { api } from '../utils/api'
import { GAME_ID } from '../utils/constants'

export function useGameState() {
    const [gameState, setGameState] = useState(null)
    const [parcels, setParcels] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchGameState = async () => {
        try {
            const [gameRes, parcelsRes] = await Promise.all([
                api.getGame(GAME_ID),
                api.getParcels(GAME_ID)
            ])
            setGameState(gameRes.data)
            setParcels(parcelsRes.data)
            setLoading(false)
        } catch (err) {
            // If game doesn't exist, create it
            if (err.response?.status === 404) {
                const createRes = await api.createGame()
                setGameState(createRes.data)
                setParcels(createRes.data.parcels)
                setLoading(false)
            } else {
                setError(err.message)
                setLoading(false)
            }
        }
    }

    useEffect(() => {
        fetchGameState()
    }, [])

    return { gameState, parcels, loading, error, refetch: fetchGameState }
}
