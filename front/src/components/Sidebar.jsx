import Dashboard from './Dashboard'
import FarmPanel from './FarmPanel'

export default function Sidebar({ gameState, parcels }) {
    return (
        <div className="flex-1 bg-farm-dark/95 p-5 overflow-y-auto shadow-[-5px_0_15px_rgba(0,0,0,0.3)]">
            <Dashboard gameState={gameState} />
            <FarmPanel parcels={parcels} />
        </div>
    )
}
