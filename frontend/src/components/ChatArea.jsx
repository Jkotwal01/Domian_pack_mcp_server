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
}) {
  const chatContent = (
    <div className="flex flex-col h-full w-full bg-white relative">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto w-full px-4 md:px-8 py-8 space-y-10 scroll-smooth custom-scrollbar">

        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
            onConfirmIntent={onConfirmIntent}
          />
        ))}

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

      {/* Input Fixed at Bottom */}
      <div className="flex-none p-6 bg-white w-full border-t border-slate-50">
        <div className="max-w-4xl mx-auto">
          <InputArea onSendMessage={onSendMessage} disabled={isTyping} />
          <p className="text-center text-[10px] text-slate-400 mt-4 tracking-wide uppercase font-semibold opacity-50">
            Powered by Advanced AI • Secure Data Processing
          </p>
        </div>
      </div>
    </div>
  );

  if (isEnhancementView) {
    return (
      <div className="flex flex-col h-full w-full bg-white">
        <header className="px-8 py-5 border-b border-slate-50 bg-white flex items-center justify-between">
          <h2 className="font-bold text-slate-900">AI Enhancement Chat</h2>
          {onClose && (
            <button 
              onClick={onClose}
              className="p-2 ml-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-all border border-transparent hover:border-slate-200"
              title="Close Chat"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </header>
        <div className="flex-1 overflow-hidden">
          {chatContent}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full w-full bg-white relative">
      {/* Top Bar / Breadcrumbs */}
      <header className="flex items-center justify-between px-8 py-5 border-b border-slate-50 bg-white z-10">
        <div className="flex items-center space-x-4">
          {!sidebarOpen && (
            <button 
              onClick={toggleSidebar}
              className="p-2 rounded-xl hover:bg-slate-50 text-slate-500 transition-all border border-transparent hover:border-slate-100"
              title="Open Sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}
          <div className="flex items-center space-x-2 text-sm text-slate-400">
            <span className="font-medium">Talk to My Data</span>
            <span className="text-slate-300">/</span>
            <span className="text-slate-900 font-bold">New Chat</span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex -space-x-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-400">
                AI
              </div>
            ))}
          </div>
          <span className="text-xs font-semibold text-slate-500 bg-slate-50 px-3 py-1 rounded-full border border-slate-100">AI Assistant</span>
          {onClose && (
            <button 
              onClick={onClose}
              className="p-2 ml-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-all border border-transparent hover:border-slate-200"
              title="Close Chat"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </header>

      {/* Messages Wrapper for non-enhancement view */}
      <div className="flex-1 overflow-hidden">
        {chatContent}
      </div>
    </div>
  );
}
