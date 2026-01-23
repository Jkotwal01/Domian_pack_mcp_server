import FileAttachment from './FileAttachment';
import ToolCallDisplay from './ToolCallDisplay';

export default function MessageBubble({ message }) {
  const isAi = message.role === "assistant";

  return (
    <div
      className={`flex w-full group ${isAi ? "justify-start" : "justify-end"}`}
    >
      <div
        className={`flex max-w-full md:max-w-[80%] ${isAi ? "flex-row" : "flex-row-reverse"} items-start gap-3`}
      >
        {/* Avatar */}
        <div
          className={`shrink-0 w-8 h-8 rounded-md flex items-center justify-center text-sm font-medium ${
            isAi
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-slate-200 text-slate-600"
          }`}
        >
          {isAi ? "AI" : "User"}
        </div>

        {/* Content */}
        <div className={`flex flex-col ${isAi ? "items-start" : "items-end"} w-full`}>
          <span className="text-xs text-slate-400 mb-1 mx-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {isAi ? "Claude" : "You"}
          </span>

          <div
            className={`px-5 py-3.5 rounded-2xl text-[15px] leading-7 shadow-sm ${
              isAi
                ? "bg-white border border-slate-200 text-slate-800 rounded-tl-none"
                : "bg-indigo-50 text-slate-800 border border-indigo-100 rounded-tr-none"
            }`}
          >
            {/* Message content */}
            {message.content && (
              <div className="whitespace-pre-wrap font-normal">
                {message.content}
              </div>
            )}

            {/* File attachments */}
            {message.files && message.files.length > 0 && (
              <div className="space-y-2 mt-2">
                {message.files.map((file, index) => (
                  <FileAttachment key={index} file={file} />
                ))}
              </div>
            )}

            {/* Tool calls */}
            {message.toolCalls && message.toolCalls.length > 0 && (
              <div className="space-y-2 mt-3">
                {message.toolCalls.map((toolCall, index) => (
                  <ToolCallDisplay key={index} toolCall={toolCall} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
