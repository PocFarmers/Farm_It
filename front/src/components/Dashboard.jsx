export default function Dashboard({ gameState }) {
    if (!gameState) return null

    return (
        <div className="bg-white/10 p-4 rounded-lg mb-5 border-2 border-farm-light/50">
            <h2 className="text-lg mb-4 text-farm-light uppercase tracking-wide">
                Dashboard
            </h2>
            <div className="space-y-2">
                <div className="flex justify-between items-center p-2 bg-black/20 rounded">
                    <span className="font-bold text-farm-light">Score</span>
                    <span className="text-xl text-white">{gameState.score}</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-black/20 rounded">
                    <span className="font-bold text-farm-light">Shovels</span>
                    <span className="text-xl text-white">{gameState.shovels}</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-black/20 rounded">
                    <span className="font-bold text-farm-light">Water Drops</span>
                    <span className="text-xl text-white">{gameState.water_drops}</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-black/20 rounded">
                    <span className="font-bold text-farm-light">Stage</span>
                    <span className="text-xl text-white">{gameState.current_stage}/50</span>
                </div>
            </div>
        </div>
    )
}
