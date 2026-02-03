import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function YAMLViewer({ yamlContent, title = "YAML Content", onClose }) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const handleCopy = () => {
    navigator.clipboard.writeText(yamlContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_')}.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return createPortal(
    <div className="fixed inset-0 bg-black/90 z-[9999] flex items-center justify-center p-4 md:p-10 backdrop-blur-md">
      <div 
        className="bg-slate-800 rounded-3xl shadow-[0_0_100px_rgba(0,0,0,0.8)] max-w-7xl w-full h-full max-h-[90vh] flex flex-col border border-slate-700 overflow-hidden transform transition-all animate-in fade-in zoom-in duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm">
          <div className="flex flex-col">
            <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
            <p className="text-sm text-slate-400 mt-1">Validated YAML Content</p>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={handleCopy}
              className="px-5 py-2.5 bg-slate-700 hover:bg-indigo-600 text-white text-sm font-semibold rounded-xl transition-all flex items-center gap-2 shadow-lg"
              title="Copy to clipboard"
            >
              {copied ? (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Copied!
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </>
              )}
            </button>
            <button
              onClick={handleDownload}
              className="px-5 py-2.5 bg-slate-700 hover:bg-emerald-600 text-white text-sm font-semibold rounded-xl transition-all flex items-center gap-2 shadow-lg"
              title="Download YAML"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
            <div className="w-px h-8 bg-slate-700 mx-1" />
            <button
              onClick={onClose}
              className="p-2.5 hover:bg-red-500/10 rounded-xl text-slate-400 hover:text-red-500 transition-all group"
              title="Close (Esc)"
            >
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto bg-slate-900 custom-scrollbar">
          <SyntaxHighlighter
            language="yaml"
            style={vscDarkPlus}
            showLineNumbers
            customStyle={{
              margin: 0,
              padding: '2rem',
              borderRadius: 0,
              fontSize: '1.125rem',
              lineHeight: '1.7',
              background: 'transparent',
            }}
          >
            {yamlContent}
          </SyntaxHighlighter>
        </div>
        
        {/* Footer info */}
        <div className="px-6 py-3 bg-slate-800/80 border-t border-slate-700 flex justify-between items-center">
          <span className="text-xs text-slate-500 font-mono">Lines: {yamlContent.split('\n').length}</span>
          <span className="text-xs text-slate-500">Press ESC to close</span>
        </div>
      </div>
    </div>,
    document.body
  );
}
