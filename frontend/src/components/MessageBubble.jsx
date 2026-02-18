import FileAttachment from './FileAttachment';
import ToolCallDisplay from './ToolCallDisplay';
import IntentConfirmation from './IntentConfirmation';
import DiffExplorer from './DiffExplorer';

export default function MessageBubble({ message, onConfirmIntent }) {
  const isAi = message.role === "assistant";

  // Simple markdown-like rendering
  const renderContent = (content) => {
    if (!content) return null;

    // Split by code blocks
    const parts = content.split(/```(\w+)?\n([\s\S]*?)```/g);
    const elements = [];

    for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        if (!part) continue;

        if (i % 3 === 0) {
            // Regular text
            const lines = part.split('\n');
            const nodes = lines.map((line, idx) => {
                // List items
                if (line.match(/^[-*+]\s/)) {
                    return (
                        <div key={`${i}-li-${idx}`} className="flex gap-2 ml-1">
                            <span className="text-indigo-600 font-bold">•</span>
                            <span>{line.replace(/^[-*+]\s/, '')}</span>
                        </div>
                    );
                }
                // Numbered lists
                if (line.match(/^\d+\.\s/)) {
                    return (
                        <div key={`${i}-num-${idx}`} className="flex gap-2 ml-1">
                            <span className="text-indigo-600 font-medium min-w-6">{line.match(/^\d+\./)[0]}</span>
                            <span>{line.replace(/^\d+\.\s/, '')}</span>
                        </div>
                    );
                }
                // Headers
                if (line.match(/^#{1,6}\s/)) {
                    const level = line.match(/^#{1,6}/)[0].length;
                    const text = line.replace(/^#{1,6}\s/, '');
                    const sizes = { 1: 'text-xl', 2: 'text-lg', 3: 'text-base' };
                    return <div key={`${i}-h-${idx}`} className={`font-bold ${sizes[level] || 'text-base'} mt-4 mb-2 first:mt-0`}>{text}</div>;
                }
                // Bold
                if (line.match(/\*\*(.*?)\*\*/)) {
                     const parts = line.split(/(\*\*.*?\*\*)/);
                     return (
                        <div key={`${i}-bold-${idx}`} className="min-h-[1.5em]">
                            {parts.map((p, pIdx) => {
                                if (p.startsWith('**') && p.endsWith('**')) {
                                    return <strong key={pIdx}>{p.slice(2, -2)}</strong>;
                                }
                                return p;
                            })}
                        </div>
                     );
                }
                
                return line ? <div key={`${i}-p-${idx}`} className="min-h-[1.5em]">{line}</div> : <div key={`${i}-br-${idx}`} className="h-2"></div>;
            });
            elements.push(<div key={`block-${i}`} className="space-y-1">{nodes}</div>);
        } else if (i % 3 === 2) {
            // Code block content (captured group 2)
            const language = parts[i-1] || 'text'; // captured group 1
            elements.push(
                <div key={`code-${i}`} className="my-3 rounded-lg overflow-hidden border border-slate-700/50 shadow-sm">
                    <div className="flex items-center justify-between px-3 py-1.5 bg-slate-800 text-slate-300 border-b border-slate-700">
                        <span className="text-xs font-mono uppercase tracking-wider opacity-75">{language}</span>
                        <button
                            onClick={() => navigator.clipboard.writeText(part)}
                            className="text-[10px] hover:bg-slate-700 px-2 py-0.5 rounded transition-colors"
                        >
                            COPY
                        </button>
                    </div>
                    <pre className="p-3 bg-slate-900 overflow-x-auto">
                        <code className="text-sm font-mono text-emerald-400 leading-relaxed font-normal">
                            {part}
                        </code>
                    </pre>
                </div>
            );
        }
    }
    return elements;
  };

  return (
    <div
      className={`flex w-full group ${isAi ? "justify-start" : "justify-end"}`}
    >
      <div
        className={`flex max-w-[95%] sm:max-w-full md:max-w-[85%] ${isAi ? "flex-row" : "flex-row-reverse"} items-start gap-2 sm:gap-3`}
      >
        {/* Avatar */}
        <div
          className={`shrink-0 w-6 h-6 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center text-xs sm:text-sm font-semibold ${
            isAi
              ? "bg-linear-to-br from-indigo-500 to-purple-600 text-white shadow-md"
              : "bg-linear-to-br from-slate-200 to-slate-300 text-slate-700"
          }`}
        >
          {isAi ? "🤖" : "👤"}
        </div>

        {/* Content */}
        <div className={`flex flex-col ${isAi ? "items-start" : "items-end"} w-full min-w-0 max-w-full overflow-hidden`}>
          <span className="text-[10px] sm:text-xs text-slate-500 mb-1 mx-1 font-medium">
            {isAi ? "Assistant" : "You"}
          </span>

          <div
            className={`px-3 sm:px-5 py-3 sm:py-4 rounded-2xl text-[14px] sm:text-[15px] leading-6 sm:leading-7 shadow-sm w-full relative ${
              isAi
                ? "bg-white border border-slate-200 text-slate-800 rounded-tl-md"
                : "bg-linear-to-br from-indigo-50 to-indigo-100 text-slate-800 border border-indigo-200 rounded-tr-md"
            }`}
          >
            {/* Message content */}
            {message.content && (
              <div className="whitespace-pre-wrap font-normal prose prose-sm max-w-none wrap-break-word overflow-hidden">
                {renderContent(message.content)}
              </div>
            )}

            {/* File attachments */}
            {message.files && message.files.length > 0 && (
              <div className="space-y-2 mt-3 overflow-x-auto">
                {message.files.map((file, index) => (
                  <FileAttachment key={index} file={file} />
                ))}
              </div>
            )}

            {/* Tool calls */}
            {message.toolCalls && message.toolCalls.length > 0 && (
              <div className="space-y-2 mt-4 pt-4 border-t border-slate-200 overflow-x-auto">
                <div className="text-[10px] sm:text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                  🔧 Tool Executions ({message.toolCalls.length})
                </div>
                {message.toolCalls.map((toolCall, index) => (
                  <ToolCallDisplay key={index} toolCall={toolCall} />
                ))}
              </div>
            )}

            {/* Proposed Intent / Changes (Show for both operations and suggestions if data exists) */}
            {message.operations && (
              <IntentConfirmation 
                operations={message.operations} 
                onConfirm={(approved) => onConfirmIntent(message.intentId, approved)}
                readOnly={message.type === 'suggestion'}
                disabled={message.isSystemAction} // Disable if already applied
              />
            )}

            {/* Diff Explorer (for applied actions) */}
            {message.isSystemAction && message.diff && (
              <DiffExplorer diff={message.diff} version={message.version} />
            )}

            {/* Error state */}
            {message.error && (
              <div className="mt-2 text-xs sm:text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-2 sm:px-3 py-2">
                ⚠️ Error: {message.content || "Something went wrong"}
              </div>
            )}
          </div>

          {/* Timestamp */}
          {message.timestamp && (
            <span className="text-[10px] sm:text-xs text-slate-400 mt-1 mx-1">
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
