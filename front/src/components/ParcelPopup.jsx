import { api } from '../utils/api'
import { GAME_ID } from '../utils/constants'

export default function ParcelPopup({ parcel, onActionExecuted }) {
    const executeAction = async (action, cropType = null) => {
        try {
            await api.executeAction(GAME_ID, {
                parcel_id: parcel.id,
                action,
                crop_type: cropType
            })
            onActionExecuted()
        } catch (err) {
            alert(err.response?.data?.message || 'Action failed')
        }
    }

    return (
        <div className="min-w-[250px]">
            <h3 className="text-base font-bold mb-3 pb-2 border-b border-white/30">
                Parcel Info
            </h3>

            <div className="mb-4 space-y-1 text-sm">
                <div className="flex justify-between">
                    <span>Zone:</span>
                    <strong className="capitalize">{parcel.zone_id}</strong>
                </div>
                <div className="flex justify-between">
                    <span>Type:</span>
                    <strong className="capitalize">{parcel.parcel_type}</strong>
                </div>
                {parcel.crop_type && (
                    <>
                        <div className="flex justify-between">
                            <span>Crop:</span>
                            <strong className="capitalize">{parcel.crop_type}</strong>
                        </div>
                        <div className="flex justify-between">
                            <span>Stage:</span>
                            <strong className="capitalize">{parcel.crop_stage}</strong>
                        </div>
                    </>
                )}
            </div>

            <div>
                <h4 className="text-sm font-bold mb-2 pb-1 border-b border-white/30">
                    Actions
                </h4>
                <div className="space-y-2">
                    {!parcel.owned && (
                        <button
                            onClick={() => executeAction('buy_parcel')}
                            className="w-full p-2 bg-white/20 hover:bg-white/30 border border-white/40 rounded text-sm transition"
                        >
                            Buy Parcel (2 shovels)
                        </button>
                    )}

                    {parcel.owned && parcel.parcel_type === 'field' && !parcel.crop_type && (
                        <>
                            <button
                                onClick={() => executeAction('plant_crop', 'potato')}
                                className="w-full p-2 bg-white/20 hover:bg-white/30 border border-white/40 rounded text-sm transition"
                            >
                                Plant Potato (free)
                            </button>
                            <button
                                onClick={() => executeAction('plant_crop', 'banana')}
                                className="w-full p-2 bg-white/20 hover:bg-white/30 border border-white/40 rounded text-sm transition"
                            >
                                Plant Banana (free)
                            </button>
                            <button
                                onClick={() => executeAction('plant_crop', 'sorghum')}
                                className="w-full p-2 bg-white/20 hover:bg-white/30 border border-white/40 rounded text-sm transition"
                            >
                                Plant Sorghum (free)
                            </button>
                        </>
                    )}

                    {parcel.owned && parcel.crop_type && (
                        <button
                            onClick={() => executeAction('irrigate')}
                            className="w-full p-2 bg-white/20 hover:bg-white/30 border border-white/40 rounded text-sm transition"
                        >
                            Irrigate (1 water drop)
                        </button>
                    )}

                    {parcel.owned && !parcel.has_water_reserve && (
                        <button
                            onClick={() => executeAction('buy_water_reserve')}
                            className="w-full p-2 bg-white/20 hover:bg-white/30 border border-white/40 rounded text-sm transition"
                        >
                            Buy Water Reserve (3 shovels)
                        </button>
                    )}

                    {parcel.owned && !parcel.has_firebreak && (
                        <button
                            onClick={() => executeAction('buy_firebreak')}
                            className="w-full p-2 bg-white/20 hover:bg-white/30 border border-white/40 rounded text-sm transition"
                        >
                            Buy Firebreak (3 shovels)
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}
