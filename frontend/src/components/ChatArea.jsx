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
}) {
  return (
    <div className="flex flex-col h-full w-full bg-slate-50 relative">
      {/* Mobile Top Bar */}
      <header className="flex md:hidden items-center justify-between p-3 border-b bg-white text-slate-800 z-10">
        <button 
          onClick={toggleSidebar}
          className="p-1.5 rounded-md hover:bg-slate-100 text-slate-600 transition-colors"
          title="Open Menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span className="font-semibold text-slate-700">Domain Pack Editor</span>
        <div className="w-9 h-9" /> {/* Placeholder for balance */}
      </header>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto w-full px-2 sm:px-6 md:px-12 lg:px-24 xl:px-48 py-4 sm:py-6 space-y-6 sm:space-y-8 scroll-smooth">
        {/* Onboarding if empty */}
        {messages.length === 0 && (
          <Onboarding 
            onFileUpload={(file) => onSendMessage("", [file])}
            isUploading={isTyping}
          />
        )}

        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
            onConfirmIntent={onConfirmIntent}
          />
        ))}

        {uploadingFiles && uploadingFiles.length > 0 && (
          <div className="space-y-2">
            {uploadingFiles.map((file, index) => (
              <FileUploadLoader key={index} fileName={file.name} progress={75} />
            ))}
          </div>
        )}

        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} className="h-4" />
      </div>

      {/* Input Fixed at Bottom */}
      {/* Input Fixed at Bottom */}
      <div className="flex-none p-3 sm:p-6 bg-slate-50 w-full border-t border-slate-100 sm:border-none z-10">
        <div className="max-w-4xl mx-auto">
          <InputArea onSendMessage={onSendMessage} disabled={isTyping} />
          <p className="text-center text-[10px] sm:text-xs text-slate-400 mt-2 sm:mt-3 px-2">
            AI can make mistakes. Please verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}
