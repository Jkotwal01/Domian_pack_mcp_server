import React, { useState } from 'react';

export default function ToolCallDisplay({ toolCall }) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Determine status styling
  const getStatusStyles = () => {
    switch (toolCall.status) {
      case 'pending':
        return 'bg-slate-100 text-slate-600 border-slate-200';
      case 'running':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'completed':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'error':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  const getStatusIcon = () => {
    switch (toolCall.status) {
      case 'pending':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'running':
        return (
          <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        );
      case 'completed':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`border rounded-lg overflow-hidden ${getStatusStyles()}`}>
      {/* Tool header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-black/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            {getStatusIcon()}
          </div>
          <div className="text-left">
            <div className="font-medium text-sm">
              {toolCall.toolName || 'Tool Call'}
            </div>
            <div className="text-xs opacity-75 capitalize">
              {toolCall.status || 'pending'}
            </div>
          </div>
        </div>
        <svg 
          className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded details */}
      {isExpanded && (
        <div className="px-4 py-3 border-t border-current/10 bg-white/50">
          {/* Input parameters */}
          {toolCall.input && (
            <div className="mb-3">
              <div className="text-xs font-semibold mb-1 opacity-75">Input:</div>
              <pre className="text-xs bg-slate-900 text-slate-100 p-3 rounded overflow-x-auto">
                {typeof toolCall.input === 'string' 
                  ? toolCall.input 
                  : JSON.stringify(toolCall.input, null, 2)}
              </pre>
            </div>
          )}

          {/* Output/Result */}
          {toolCall.output && (
            <div>
              <div className="text-xs font-semibold mb-1 opacity-75">Output:</div>
              <pre className="text-xs bg-slate-900 text-slate-100 p-3 rounded overflow-x-auto">
                {typeof toolCall.output === 'string' 
                  ? toolCall.output 
                  : JSON.stringify(toolCall.output, null, 2)}
              </pre>
            </div>
          )}

          {/* Error message */}
          {toolCall.error && (
            <div>
              <div className="text-xs font-semibold mb-1 text-red-700">Error:</div>
              <div className="text-xs bg-red-100 text-red-800 p-3 rounded">
                {toolCall.error}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
