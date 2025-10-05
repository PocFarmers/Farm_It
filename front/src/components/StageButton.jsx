export default function StageButton({ onClick, disabled }) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className="fixed bottom-8 right-8 px-8 py-4 text-base font-bold bg-gradient-to-br from-farm-green to-farm-green/80 text-white border-none rounded-lg cursor-pointer shadow-lg hover:translate-y-[-2px] hover:shadow-xl transition-all uppercase tracking-wide z-[1000] disabled:opacity-50 disabled:cursor-not-allowed"
        >
            Next Stage
        </button>
    )
}
