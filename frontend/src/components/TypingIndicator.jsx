export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mt-4 animate-fadeIn">
      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-[10px] font-black shadow-lg shadow-indigo-200">
        AI
      </div>
      <div className="flex flex-col space-y-2">
        <div className="flex items-center space-x-3 p-4 bg-white/80 backdrop-blur-md border border-indigo-100 rounded-2xl rounded-tl-none shadow-sm shadow-indigo-50/50 min-w-[120px]">
          {/* Neural Network Animation */}
          <div className="relative w-6 h-6">
            <div className="absolute inset-0 bg-indigo-400 rounded-full animate-ping opacity-20"></div>
            <svg viewBox="0 0 24 24" className="w-6 h-6 text-indigo-600 animate-pulse transition-all duration-1000">
              <path fill="currentColor" d="M12,2A10,10,0,0,0,2,12a10,10,0,0,0,10,10a10,10,0,0,0,10-10A10,10,0,0,0,12,2Zm0,18a8,8,0,1,1,8-8A8,8,0,0,1,12,20ZM12,6a6,6,0,1,0,6,6A6,6,0,0,0,12,6Zm0,10a4,4,0,1,1,4-4A4,4,0,0,1,12,16Z" opacity=".2"/>
              <circle cx="12" cy="12" r="3" fill="currentColor">
                <animate attributeName="r" values="3;4;3" dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite" />
              </circle>
              <g className="animate-spin" style={{ transformOrigin: 'center', animationDuration: '3s' }}>
                <circle cx="12" cy="5" r="1.5" fill="currentColor" />
                <circle cx="19" cy="12" r="1.5" fill="currentColor" />
                <circle cx="12" cy="19" r="1.5" fill="currentColor" />
                <circle cx="5" cy="12" r="1.5" fill="currentColor" />
              </g>
            </svg>
          </div>
          <span className="text-[12px] font-bold text-slate-400 tracking-wide animate-pulse">Thinking...</span>
        </div>
      </div>
    </div>
  );
}
