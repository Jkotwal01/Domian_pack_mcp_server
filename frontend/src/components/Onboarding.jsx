import React from 'react';
import FileUploadButton from './FileUploadButton';

/**
 * High-impact onboarding screen to force file upload and explain the system
 */
export default function Onboarding({ onFileUpload, isUploading }) {
  const handleFileChange = (files) => {
    if (files && files.length > 0) {
      onFileUpload(files[0]);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-2xl mx-auto space-y-8 animate-in fade-in zoom-in duration-500">
      {/* Icon/Logo */}
      <div className="relative">
        <div className="w-24 h-24 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-3xl flex items-center justify-center text-white text-5xl shadow-2xl shadow-indigo-200 rotate-3">
          📦
        </div>
        <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center text-white text-xl shadow-lg border-4 border-white">
          ✨
        </div>
      </div>

      {/* Intro Text */}
      <div className="space-y-4">
        <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">
          Domain Pack <span className="text-indigo-600">Generator</span>
        </h1>
        <p className="text-lg text-slate-600 leading-relaxed">
          Welcome! I am your AI-powered assistant for building and maintaining robust **Domain Packs**. 
          I can help you define entities, extraction patterns, business rules, and reasoning templates with ease.
        </p>
      </div>

      {/* Tools Explanation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full text-left">
        <div className="p-4 bg-white border border-slate-100 rounded-xl shadow-sm space-y-2">
          <div className="text-indigo-600 font-bold flex items-center gap-2 text-sm uppercase tracking-wider">
            <span>🔧</span> Intent Flow
          </div>
          <p className="text-xs text-slate-500 leading-normal">
            Describe changes in plain English. I'll propose structured operations for you to approve or reject.
          </p>
        </div>
        <div className="p-4 bg-white border border-slate-100 rounded-xl shadow-sm space-y-2">
          <div className="text-emerald-600 font-bold flex items-center gap-2 text-sm uppercase tracking-wider">
            <span>⏪</span> Version Control
          </div>
          <p className="text-xs text-slate-500 leading-normal">
            Every change creates a new version. See diffs instantly and rollback to any point in time.
          </p>
        </div>
      </div>

      {/* Action Zone */}
      <div className={`w-full p-8 rounded-3xl border-2 border-dashed transition-all duration-300 ${isUploading ? 'bg-indigo-50 border-indigo-300 animate-pulse' : 'bg-slate-50 border-slate-200 hover:border-indigo-300 hover:bg-white'}`}>
        <div className="flex flex-col items-center space-y-6">
          <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center text-indigo-600 shadow-md">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          
          <div className="space-y-1">
            <h3 className="text-xl font-bold text-slate-800">Upload to Begin</h3>
            <p className="text-sm text-slate-500">Please provide your initial **YAML** or **JSON** domain pack file.</p>
          </div>

          <div className="relative group">
             <FileUploadButton 
                onFilesSelected={handleFileChange}
                disabled={isUploading}
                customButton={
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-full shadow-lg shadow-indigo-200 transition-all hover:scale-105 active:scale-95 flex items-center gap-3">
                        {isUploading ? 'Initializing Session...' : 'Select File'}
                        {!isUploading && <span className="text-xl">🚀</span>}
                    </button>
                }
             />
          </div>
          
          <p className="text-[10px] text-slate-400 uppercase tracking-[0.2em] font-semibold pt-4">
            Required Schema: name, version, entities...
          </p>
        </div>
      </div>
    </div>
  );
}
