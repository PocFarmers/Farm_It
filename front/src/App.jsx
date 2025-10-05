import { useState } from 'react'
import GameMap from './components/GameMap'
import Sidebar from './components/Sidebar'
import StageButton from './components/StageButton'
import EventModal from './components/EventModal'
import { useGameState } from './hooks/useGameState'
import { api } from './utils/api'
import { GAME_ID } from './utils/constants'

function App() {
    const { gameState, parcels, loading, error, refetch } = useGameState()
    const [modalOpen, setModalOpen] = useState(false)
    const [stageResults, setStageResults] = useState(null)

    const handleNextStage = async () => {
        try {
            const res = await api.nextStage(GAME_ID)
            setStageResults(res.data)
            setModalOpen(true)
            await refetch()
        } catch (err) {
            alert('Failed to progress stage: ' + err.message)
        }
    }

    if (loading) return <div className="h-screen flex items-center justify-center text-white">Loading...</div>
    if (error) return <div className="h-screen flex items-center justify-center text-red-500">Error: {error}</div>

    return (
        <div className="h-screen flex bg-gradient-to-br from-farm-dark to-farm-darker text-white overflow-hidden">
            <div className="flex-[3] h-full">
                <GameMap
                    parcels={parcels}
                    onActionExecuted={refetch}
                />
            </div>

            <Sidebar gameState={gameState} parcels={parcels} />

            <StageButton
                onClick={handleNextStage}
                disabled={!gameState || gameState.current_stage >= 50}
            />

            <EventModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                events={stageResults?.events || []}
                cropUpdates={stageResults?.crop_updates || []}
                scoreChange={stageResults?.score_change || 0}
            />
        </div>
    )
}

export default App
