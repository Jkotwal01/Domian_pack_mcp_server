import React from 'react';

export default function FileUploadLoader({ fileName, progress = 0 }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg shadow-sm animate-fadeIn">
      {/* Animated spinner */}
      <div className="relative w-10 h-10 shrink-0">
        <div className="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
        <div 
          className="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"
          style={{ animationDuration: '0.8s' }}
        ></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
      </div>

      {/* File info and progress */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <p className="text-sm font-medium text-slate-700 truncate pr-2">
            {fileName}
          </p>
          <span className="text-xs font-semibold text-indigo-600">
            {progress}%
          </span>
        </div>
        
        {/* Progress bar */}
        <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div 
            className="h-full bg-linear-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          >
            <div className="h-full w-full bg-white/30 animate-shimmer"></div>
          </div>
        </div>
        
        <p className="text-xs text-slate-500 mt-1">
          Uploading...
        </p>
      </div>
    </div>
  );
}
