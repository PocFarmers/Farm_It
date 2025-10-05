import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
    createGame: () => axios.post(`${API_URL}/api/game`),
    getGame: (gameId) => axios.get(`${API_URL}/api/game/${gameId}`),
    getParcels: (gameId) => axios.get(`${API_URL}/api/parcels/${gameId}`),
    executeAction: (gameId, action) => axios.post(`${API_URL}/api/game/${gameId}/action`, action),
    nextStage: (gameId) => axios.post(`${API_URL}/api/game/${gameId}/next-stage`),
}
