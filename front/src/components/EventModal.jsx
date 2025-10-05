export default function EventModal({ isOpen, onClose, events, cropUpdates, scoreChange }) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/80 z-[2000] flex items-center justify-center">
            <div className="bg-gradient-to-br from-farm-dark to-farm-darker p-8 rounded-2xl max-w-lg border-4 border-farm-green shadow-2xl">
                <h2 className="text-farm-light text-2xl mb-5 text-center">
                    Stage Results
                </h2>

                <div className="space-y-3 mb-5 text-white">
                    {events.length > 0 && (
                        <div>
                            <h3 className="text-farm-green font-bold mb-2">Events:</h3>
                            {events.map((event, i) => (
                                <p key={i} className="text-sm">
                                    {event.type === 'Fire' ? '🔥' : '☀️'} {event.type} at parcel {event.parcel_id}
                                </p>
                            ))}
                        </div>
                    )}

                    {cropUpdates.length > 0 && (
                        <div>
                            <h3 className="text-farm-green font-bold mb-2">Crop Updates:</h3>
                            {cropUpdates.map((update, i) => (
                                <p key={i} className="text-sm">
                                    {update.status === 'harvested' && `✅ Harvested ${update.crop}!`}
                                    {update.status === 'died' && `❌ ${update.crop} died`}
                                    {update.status === 'advanced' && `🌱 ${update.crop} → ${update.new_stage}`}
                                </p>
                            ))}
                        </div>
                    )}

                    <div className="pt-3 border-t border-farm-light/30">
                        <p className="font-bold">
                            Score Change: <span className={scoreChange >= 0 ? 'text-farm-green' : 'text-red-400'}>
                                {scoreChange >= 0 ? '+' : ''}{scoreChange}
                            </span>
                        </p>
                    </div>
                </div>

                <button
                    onClick={onClose}
                    className="w-full p-3 bg-farm-green text-white rounded-lg font-bold text-base hover:bg-farm-green/90 transition"
                >
                    Continue
                </button>
            </div>
        </div>
    )
}
