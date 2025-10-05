import { CROP_ICONS } from '../utils/constants'

export default function FarmPanel({ parcels }) {
    const ownedParcels = parcels.filter(p => p.owned)

    // Count crops
    const cropCounts = ownedParcels.reduce((acc, p) => {
        if (p.crop_type) {
            acc[p.crop_type] = (acc[p.crop_type] || 0) + 1
        }
        return acc
    }, {})

    return (
        <div className="bg-white/10 p-4 rounded-lg border-2 border-farm-light/50">
            <h2 className="text-lg mb-4 text-farm-light uppercase tracking-wide">
                My Farm
            </h2>

            <div className="mb-4 p-3 bg-black/20 rounded text-center">
                <div className="text-farm-light font-bold mb-1">Parcels Owned</div>
                <div className="text-2xl text-white">{ownedParcels.length}</div>
            </div>

            <div className="space-y-3">
                {Object.entries(cropCounts).map(([crop, count]) => (
                    <div key={crop} className="flex items-center p-3 bg-black/20 rounded">
                        <div className="text-3xl mr-4">{CROP_ICONS[crop] || '🌱'}</div>
                        <div className="flex-1">
                            <div className="font-bold text-farm-light capitalize">{crop}</div>
                            <div className="text-lg text-white">{count}</div>
                        </div>
                    </div>
                ))}
                {Object.keys(cropCounts).length === 0 && (
                    <p className="text-farm-light/70 text-center">No crops planted</p>
                )}
            </div>
        </div>
    )
}
