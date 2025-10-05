export function LoadingState() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-sky-400 to-blue-600">
      <div className="text-center">
        <div className="relative">
          {/* Vagues animées */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 border-4 border-blue-300 rounded-full animate-ping opacity-30"></div>
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-24 h-24 border-4 border-blue-400 rounded-full animate-ping opacity-40" style={{ animationDelay: '0.2s' }}></div>
          </div>

          {/* Île qui charge */}
          <div className="relative z-10 bg-gradient-to-br from-green-500 to-green-700 rounded-full w-20 h-20 flex items-center justify-center shadow-2xl animate-bounce">
            <span className="text-4xl">🏝️</span>
          </div>
        </div>

        <div className="mt-12 bg-white/90 backdrop-blur-sm rounded-lg px-8 py-4 shadow-xl">
          <p className="text-green-700 text-xl font-bold mb-2">Chargement de votre île...</p>
          <div className="flex justify-center gap-1">
            <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
            <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
