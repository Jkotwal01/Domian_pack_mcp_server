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
    <div className={`flex w-full group ${isAi ? "justify-start" : "justify-end"} animate-fadeIn`}>
      <div className={`flex max-w-[95%] sm:max-w-full md:max-w-[85%] ${isAi ? "flex-row" : "flex-row-reverse"} items-start gap-2 sm:gap-3`}>
        {/* Avatar */}
        <div className={`shrink-0 w-8 h-8 rounded-xl flex items-center justify-center text-sm font-semibold transition-transform duration-300 group-hover:scale-110 ${
            isAi ? "bg-linear-to-br from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-100" : "bg-linear-to-br from-slate-700 to-slate-900 text-white shadow-lg shadow-slate-200"
        }`}>
          {isAi ? "🤖" : "👤"}
        </div>

        {/* Content Container */}
        <div className={`flex flex-col ${isAi ? "items-start" : "items-end"} w-full min-w-0`}>
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 mx-2">
            {isAi ? "Assistant" : "You"}
          </span>

          <div
            className={`px-5 py-4 shadow-sm transition-all duration-300 hover:shadow-md max-w-full overflow-hidden ${
              isAi
                ? "bg-linear-to-br from-indigo-50/80 to-indigo-100/50 text-slate-800 border border-indigo-100 rounded-2xl rounded-tl-none shadow-[0_4px_15px_rgba(79,70,229,0.05)]"
                : "bg-slate-900 text-white rounded-2xl rounded-tr-none shadow-lg shadow-slate-100"
            }`}
          >
            {/* AI Reasoning / Thought Process */}
            {isAi && message.reasoning && (
              <div className="mb-4 p-4 bg-white/60 border border-indigo-100/50 rounded-xl relative overflow-hidden group/reasoning">
                <div className="absolute top-0 left-0 w-1 h-full bg-indigo-400 opacity-40"></div>
                <div className="flex items-start space-x-3">
                  <span className="text-lg mt-0.5 filter drop-shadow-sm">💭</span>
                  <div>
                    <h5 className="text-[9px] font-black text-indigo-400 uppercase tracking-[0.2em] mb-1">
                      Thought Process
                    </h5>
                    <p className="text-[13px] text-indigo-700 leading-relaxed font-medium italic">
                      {message.reasoning}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Message content */}
            {message.content && (
              <div className={`whitespace-pre-wrap font-normal prose prose-sm max-w-none break-words ${isAi ? "text-slate-700" : "text-slate-100"}`}>
                {renderContent(message.content)}
              </div>
            )}

            {/* File attachments */}
            {message.files && message.files.length > 0 && (
              <div className="space-y-2 mt-4 overflow-x-auto">
                {message.files.map((file, index) => (
                  <FileAttachment key={index} file={file} />
                ))}
              </div>
            )}

            {/* Tool calls */}
            {message.toolCalls && message.toolCalls.length > 0 && (
              <div className="space-y-2 mt-4 pt-4 border-t border-indigo-100/50 overflow-x-auto">
                <div className="text-[10px] font-black text-indigo-400 uppercase tracking-wider mb-2">
                  🔧 System Operations ({message.toolCalls.length})
                </div>
                {message.toolCalls.map((toolCall, index) => (
                  <ToolCallDisplay key={index} toolCall={toolCall} />
                ))}
              </div>
            )}

            {/* Proposed Intent / Changes */}
            {message.operations && (
              <IntentConfirmation 
                operations={message.operations} 
                onConfirm={(approved) => onConfirmIntent(message.intentId, approved)}
                readOnly={message.type === 'suggestion'}
                disabled={message.isSystemAction}
              />
            )}

            {/* Diff Explorer */}
            {message.isSystemAction && message.diff && (
              <div className="mt-4 pt-4 border-t border-indigo-100/30">
                <DiffExplorer diff={message.diff} version={message.version} />
              </div>
            )}

            {/* Error state */}
            {message.error && (
              <div className="mt-4 p-3 bg-rose-50 border border-rose-100 rounded-xl flex items-center space-x-2">
                <span className="text-lg">⚠️</span>
                <span className="text-[13px] text-rose-600 font-bold">{message.content || "An unexpected error occurred."}</span>
              </div>
            )}
          </div>

          {/* Timestamp */}
          {message.timestamp && (
            <div className={`flex items-center space-x-1 mt-1.5 mx-2 text-slate-400`}>
              <span className="text-[10px] font-bold">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              {isAi && <span className="text-[8px] opacity-30">|</span>}
              {isAi && <span className="text-[10px] font-medium opacity-50 uppercase tracking-tighter">SECURED BY DOMAIN CORE</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
