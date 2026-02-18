import MessageBubble from "./MessageBubble";
import InputArea from "./InputArea";
import TypingIndicator from "./TypingIndicator";
import FileUploadLoader from "./FileUploadLoader";
import Onboarding from "./Onboarding";

export default function ChatArea({
  messages,
  isTyping,
  uploadingFiles,
  onSendMessage,
  onConfirmIntent,
  messagesEndRef,
  sidebarOpen,
  toggleSidebar,
  isEnhancementView,
  configSession,
  onClose, // New prop
  onDelete, // New prop
}) {
  return (
    <div className={`flex flex-col h-full bg-slate-50/30 relative overflow-hidden font-sans border-l border-slate-100 ${sidebarOpen ? 'w-full' : 'w-full'} animate-fadeIn overflow-x-hidden`}>
      {/* Glossy Header */}
      <div className="flex-none flex items-center justify-between px-6 py-4 bg-white/70 backdrop-blur-xl border-b border-indigo-100/30 sticky top-0 z-10 shadow-[0_1px_5px_rgba(0,0,0,0.02)]">
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 rounded-2xl bg-linear-to-br from-indigo-600 to-violet-700 flex items-center justify-center text-white shadow-lg shadow-indigo-100 ring-4 ring-white">
            <span className="text-xl">🤖</span>
          </div>
          <div>
            <h2 className="text-sm font-black text-slate-800 tracking-tight">
              {isEnhancementView ? "AI Domain Architect" : "Neural Assistant"}
            </h2>
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-sm shadow-emerald-200"></span>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Connected • v2.8</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => {
              if (window.confirm("Are you sure you want to delete this chat session and all messages? This cannot be undone.")) {
                onDelete();
              }
            }}
            className="p-2.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-all active:scale-90"
            title="Clear current session"
          >
            <span className="text-lg">🗑️</span>
          </button>
          {onClose && (
            <button 
              onClick={onClose}
              className="p-2.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-all active:scale-90"
              title="Close chat"
            >
              <span className="text-lg">❌</span>
            </button>
          )}
        </div>
      </div>

      {/* Messages Stage */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden w-full px-4 md:px-8 py-8 space-y-10 scroll-smooth custom-scrollbar bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.03),transparent_40%),radial-gradient(circle_at_bottom_left,rgba(139,92,246,0.03),transparent_40%)]">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-6 max-w-sm mx-auto mt-10">
            <div className="w-24 h-24 bg-white rounded-[2rem] shadow-2xl flex items-center justify-center text-4xl transform rotate-3 ring-8 ring-indigo-50/50">
              ✨
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-black text-slate-800">Ready to build?</h3>
              <p className="text-xs text-slate-400 font-medium leading-relaxed">
                Describe your domain needs and I'll generate entities, relationships, and patterns in seconds.
              </p>
            </div>
            <button
               onClick={() => onSendMessage("Suggest some entities for my domain")}
               className="mt-4 px-6 py-2.5 bg-indigo-600 text-white text-[11px] font-black uppercase tracking-widest rounded-full shadow-lg shadow-indigo-200 hover:shadow-indigo-300 transition-all hover:-translate-y-0.5"
            >
               Quick Start ✨
            </button>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageBubble 
              key={msg.id || index} 
              message={msg} 
              onConfirmIntent={onConfirmIntent}
            />
          ))
        )}

        {uploadingFiles && uploadingFiles.length > 0 && (
          <div className="space-y-3">
            {uploadingFiles.map((file, index) => (
              <FileUploadLoader key={index} fileName={file.name} progress={75} />
            ))}
          </div>
        )}

        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} className="h-8" />
      </div>

      {/* Input Stage */}
      <div className="flex-none p-6 bg-white w-full border-t border-indigo-50">
        <div className="max-w-4xl mx-auto">
          <InputArea onSendMessage={onSendMessage} disabled={isTyping} />
          <p className="text-center text-[10px] text-slate-400 mt-4 tracking-wide uppercase font-black opacity-40">
            Enterprise Grade Domain Intelligence • Secured by MCP
          </p>
        </div>
      </div>
    </div>
  );
}
