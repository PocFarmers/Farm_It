export function LoadingState() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-[#F5F2EA]">
      <div className="text-center">
        <div className="relative">
          {/* Animated rings */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 border-4 border-[#A37039] rounded-full animate-ping opacity-30"></div>
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-24 h-24 border-4 border-[#35613F] rounded-full animate-ping opacity-40" style={{ animationDelay: '0.2s' }}></div>
          </div>

          {/* Loading logo */}
          <div className="relative z-10 bg-[#35613F] rounded-full w-20 h-20 flex items-center justify-center shadow-2xl animate-bounce">
            <img src="/logo.png" alt="Loading" className="w-12 h-12 object-contain" />
          </div>
        </div>

        <div className="mt-12 bg-white rounded-lg px-8 py-4 shadow-xl border-2 border-[#35613F]">
          <p className="text-[#35613F] text-xl font-bold mb-2">Loading your farm...</p>
          <div className="flex justify-center gap-1">
            <div className="w-2 h-2 bg-[#F5A842] rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
            <div className="w-2 h-2 bg-[#A37039] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-[#35613F] rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
