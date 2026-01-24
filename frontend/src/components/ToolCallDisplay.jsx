import React, { useState } from 'react';

export default function ToolCallDisplay({ toolCall }) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Extract data from our backend structure
  const toolName = toolCall.tool || toolCall.toolName || 'Tool Call';
  const input = toolCall.arguments || toolCall.input;
  const output = toolCall.result || toolCall.output;
  const status = toolCall.result?.success === false ? 'error' : 'completed';

  // Determine status styling
  const getStatusStyles = () => {
    if (status === 'error') {
      return 'bg-red-50 text-red-700 border-red-200';
    }
    return 'bg-green-50 text-green-700 border-green-200';
  };

  const getStatusIcon = () => {
    if (status === 'error') {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
    }
    return (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    );
  };

  // Get tool icon based on name
  const getToolIcon = () => {
    const iconClass = "w-5 h-5";
    
    if (toolName.includes('create')) {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      );
    }
    if (toolName.includes('apply') || toolName.includes('change')) {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      );
    }
    if (toolName.includes('export')) {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      );
    }
    if (toolName.includes('rollback')) {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      );
    }
    if (toolName.includes('info') || toolName.includes('get')) {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
    
    // Default tool icon
    return (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    );
  };

  return (
    <div className={`border rounded-xl overflow-hidden ${getStatusStyles()} transition-all my-2 shadow-sm`}>
      {/* Tool header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2.5 flex items-center justify-between hover:bg-black/5 transition-colors group gap-3"
      >
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="flex-shrink-0 opacity-80 group-hover:opacity-100 transition-opacity">
            {getToolIcon()}
          </div>
          <div className="text-left min-w-0 flex-1">
            <div className="font-semibold text-sm truncate pr-2">
              {toolName}
            </div>
            <div className="text-[11px] opacity-75 flex items-center gap-2 mt-0.5 min-w-0">
              <div className="flex items-center gap-1 flex-shrink-0">
                {getStatusIcon()}
                <span className="capitalize">{status}</span>
              </div>
              {output?.version && (
                <span className="truncate hidden sm:inline">• Version {output.version}</span>
              )}
            </div>
          </div>
        </div>
        <svg 
          className={`w-4 h-4 text-current opacity-40 group-hover:opacity-70 transition-all flex-shrink-0 ${isExpanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded details */}
      {isExpanded && (
        <div className="px-3 py-3 border-t border-current/10 bg-white/50 space-y-3 text-xs">
          {/* Input parameters */}
          {input && (
            <div>
              <div className="font-semibold mb-1.5 opacity-75 uppercase tracking-wider text-[10px]">Input:</div>
              <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-800/50">
                <pre className="text-emerald-400 p-2.5 whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed max-h-60 overflow-y-auto custom-scrollbar">
                  {typeof input === 'string' 
                    ? input 
                    : JSON.stringify(input, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Output/Result */}
          {output && (
            <div>
              <div className="font-semibold mb-1.5 opacity-75 uppercase tracking-wider text-[10px]">
                {status === 'error' ? 'Error Details:' : 'Result:'}
              </div>
               <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-800/50">
                <pre className="text-cyan-400 p-2.5 whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed max-h-80 overflow-y-auto custom-scrollbar">
                  {typeof output === 'string' 
                    ? output 
                    : JSON.stringify(output, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Session info if present */}
          {output?.session_id && (
            <div className="flex items-center gap-2 text-[11px] bg-indigo-50/80 text-indigo-700 px-2.5 py-1.5 rounded-md border border-indigo-200/60">
              <span className="font-semibold">Session ID:</span> 
              <code className="font-mono text-indigo-800 select-all">{output.session_id}</code>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
