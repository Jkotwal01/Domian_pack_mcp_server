
export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-md bg-indigo-600 flex items-center justify-center text-white text-sm font-medium">AI</div>
        <div className="flex items-center space-x-1 p-4 bg-white border border-slate-200 rounded-2xl rounded-tl-none shadow-sm h-[54px] w-20 justify-center">
            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
    </div>
  );
}
