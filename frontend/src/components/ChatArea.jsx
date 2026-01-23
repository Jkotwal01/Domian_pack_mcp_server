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
    <div className="flex flex-col h-full w-full bg-slate-50">
      {/* Header for Mobile */}
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-slate-200 md:hidden sticky top-0 z-10 w-full">
        <button
          onClick={toggleSidebar}
          className="p-2 -ml-2 rounded-md hover:bg-slate-100 text-slate-600"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
        <span className="font-semibold text-slate-700">
          Domain Pack Generator
        </span>
        <div className="w-8"></div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-20 lg:px-32 py-6 space-y-8 scroll-smooth">
        {/* Welcome text if empty */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 space-y-4">
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
      <div className="p-4 sm:p-6 bg-slate-50 sticky bottom-0 z-10">
        <div className="max-w-3xl mx-auto">
          <InputArea onSendMessage={onSendMessage} disabled={isTyping} />
          <p className="text-center text-xs text-slate-400 mt-3">
            AI can make mistakes. Please verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}
