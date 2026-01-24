import MessageBubble from "./MessageBubble";
import InputArea from "./InputArea";
import TypingIndicator from "./TypingIndicator";
import FileUploadLoader from "./FileUploadLoader";

export default function ChatArea({
  messages,
  isTyping,
  uploadingFiles,
  onSendMessage,
  messagesEndRef,
  sidebarOpen,
  toggleSidebar,
}) {
  return (
    <div className="flex flex-col h-full w-full bg-slate-50 relative">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto w-full px-2 sm:px-6 md:px-12 lg:px-24 xl:px-48 py-4 sm:py-6 space-y-6 sm:space-y-8 scroll-smooth">
        {/* Welcome text if empty */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 space-y-4 px-4">
            <div className="w-16 h-16 bg-slate-200 rounded-full flex items-center justify-center mb-4">
              <span className="text-3xl">👋</span>
            </div>
            <h2 className="text-2xl font-semibold text-slate-700">
              Welcome to Chat
            </h2>
            <p>Start a conversation below.</p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
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
