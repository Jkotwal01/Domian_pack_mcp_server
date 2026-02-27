import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import FileAttachment from './FileAttachment';
import ToolCallDisplay from './ToolCallDisplay';
import IntentConfirmation from './IntentConfirmation';
import DiffExplorer from './DiffExplorer';

export default function MessageBubble({ message, onConfirmIntent }) {
  const isAi = message.role === "assistant";

  // Custom components for ReactMarkdown to match the app's aesthetic
  const markdownComponents = {
    // Custom styling for lists
    ul: ({ children }) => <ul className="space-y-2 my-3 ml-1">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal space-y-2 my-3 ml-5">{children}</ol>,
    li: ({ children }) => (
      <li className="flex gap-2 items-start group/li">
        <span className="text-indigo-600 font-bold mt-1.5 shrink-0 text-xs transition-transform group-hover/li:scale-125">•</span>
        <span className="flex-1">{children}</span>
      </li>
    ),
    // Headers
    h1: ({ children }) => <h1 className="text-xl font-black text-slate-900 mt-6 mb-3 first:mt-0 tracking-tight">{children}</h1>,
    h2: ({ children }) => <h2 className="text-lg font-bold text-slate-800 mt-5 mb-2 first:mt-0 tracking-tight">{children}</h2>,
    h3: ({ children }) => <h3 className="text-base font-bold text-slate-800 mt-4 mb-2 first:mt-0">{children}</h3>,
    // Paragraphs and bold
    p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
    strong: ({ children }) => <strong className="font-extrabold text-indigo-900 bg-indigo-50/50 px-1 rounded-sm">{children}</strong>,
    // Code blocks
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <div className="my-4 rounded-xl overflow-hidden border border-slate-700/50 shadow-xl group/code">
            <div className="flex items-center justify-between px-4 py-2 bg-slate-800 text-slate-300 border-b border-slate-700">
                <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-80">{match[1]}</span>
                <button
                    onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                    className="text-[10px] font-bold hover:bg-slate-700/80 px-2.5 py-1 rounded-md transition-all active:scale-95"
                >
                    COPY
                </button>
            </div>
            <pre className="p-4 bg-slate-900 overflow-x-auto scrollbar-thin scrollbar-thumb-slate-700">
                <code className="text-sm font-mono text-emerald-400 leading-relaxed block" {...props}>
                    {children}
                </code>
            </pre>
        </div>
      ) : (
        <code className="bg-slate-100 text-indigo-600 px-1.5 py-0.5 rounded font-mono text-[0.9em] font-semibold border border-indigo-50" {...props}>
          {children}
        </code>
      );
    },
    // Links
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-600 font-bold hover:underline decoration-2 underline-offset-2">
        {children}
      </a>
    ),
    // Blockquotes
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-indigo-200 pl-4 py-1 my-4 italic text-slate-600 bg-indigo-50/30 rounded-r-lg">
        {children}
      </blockquote>
    )
  };

  return (
    <div className={`flex w-full group ${isAi ? "justify-start" : "justify-end"} animate-fadeIn`}>
      <div className={`flex max-w-[95%] sm:max-w-full md:max-w-[85%] ${isAi ? "flex-row" : "flex-row-reverse"} items-start gap-2 sm:gap-4`}>
        {/* Avatar */}
        <div className={`shrink-0 w-9 h-9 rounded-2xl flex items-center justify-center text-base font-semibold transition-all duration-500 group-hover:rotate-12 group-hover:scale-110 shadow-md ${
            isAi 
              ? "bg-linear-to-br from-indigo-500 via-indigo-600 to-purple-700 text-white shadow-indigo-200/50 ring-2 ring-white" 
              : "bg-linear-to-br from-slate-700 to-slate-900 text-white shadow-slate-200/50 ring-2 ring-white"
        }`}>
          {isAi ? "🤖" : "👤"}
        </div>

        {/* Content Container */}
        <div className={`flex flex-col ${isAi ? "items-start" : "items-end"} w-full min-w-0`}>
          <div className="flex items-center space-x-2 mb-1.5 px-1">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em]">
              {isAi ? "Domain Core AI" : "Architect"}
            </span>
          </div>

          <div
            className={`px-6 py-5 shadow-sm transition-all duration-500 hover:shadow-xl max-w-full overflow-hidden border ${
              isAi
                ? "bg-white text-slate-800 border-indigo-100 rounded-3xl rounded-tl-none shadow-[0_10px_40px_rgba(79,70,229,0.06)]"
                : "bg-slate-900 text-white border-slate-800 rounded-3xl rounded-tr-none shadow-2xl shadow-slate-200/50"
            }`}
          >
            {/* AI Reasoning / Thought Process */}
            {isAi && message.reasoning && (
              <div className="mb-5 p-4.5 bg-indigo-50/40 border border-indigo-100/50 rounded-2xl relative overflow-hidden group/reasoning hover:bg-indigo-50/60 transition-colors">
                <div className="absolute top-0 left-0 w-1.5 h-full bg-linear-to-b from-indigo-400 to-purple-500 opacity-60"></div>
                <div className="flex items-start space-x-4">
                  <span className="text-xl mt-0.5 filter drop-shadow-sm select-none">🧠</span>
                  <div className="flex-1">
                    <h5 className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.3em] mb-1.5 opacity-80">
                      Processing Context
                    </h5>
                    <p className="text-[13.5px] text-indigo-800/90 leading-relaxed font-medium">
                      {message.reasoning}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Message content with ReactMarkdown */}
            {message.content && (
              <div className={`markdown-content prose prose-slate prose-sm max-w-none break-words ${isAi ? "text-slate-700" : "text-white"}`}>
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]} 
                  components={markdownComponents}
                >
                  {message.content}
                </ReactMarkdown>
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
