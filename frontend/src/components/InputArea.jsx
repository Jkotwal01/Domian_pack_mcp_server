import React, { useState, useRef, useEffect } from 'react';
import FileUploadButton from './FileUploadButton';

export default function InputArea({ onSendMessage, disabled }) {
    const [input, setInput] = useState('');
    const [attachedFiles, setAttachedFiles] = useState([]);
    const textareaRef = useRef(null);

    const handleSubmit = () => {
        if ((!input.trim() && attachedFiles.length === 0) || disabled) return;
        onSendMessage(input, attachedFiles);
        setInput('');
        setAttachedFiles([]);
        // Reset height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'; 
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleFilesSelected = (files) => {
        setAttachedFiles(prev => [...prev, ...files]);
    };

    const removeFile = (index) => {
        setAttachedFiles(prev => {
            const newFiles = [...prev];
            // Revoke preview URL to prevent memory leaks
            if (newFiles[index].preview) {
                URL.revokeObjectURL(newFiles[index].preview);
            }
            newFiles.splice(index, 1);
            return newFiles;
        });
    };
    
    // Auto-resize textarea
    useEffect(() => {
        const el = textareaRef.current;
        if (el) {
             el.style.height = 'auto';
             el.style.height = Math.min(el.scrollHeight, 200) + 'px';
        }
    }, [input]);

    // Cleanup preview URLs on unmount
    useEffect(() => {
        return () => {
            attachedFiles.forEach(file => {
                if (file.preview) {
                    URL.revokeObjectURL(file.preview);
                }
            });
        };
    }, []);

    return (
        <div className="w-full max-w-3xl mx-auto">
            {/* File previews */}
            {attachedFiles.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-2">
                    {attachedFiles.map((file, index) => (
                        <div key={index} className="relative group">
                            <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 border border-slate-200 rounded-lg">
                                <span className="text-sm text-slate-700 truncate max-w-[150px]">
                                    {file.name}
                                </span>
                                <button
                                    onClick={() => removeFile(index)}
                                    className="text-slate-400 hover:text-red-500 transition-colors"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Input area */}
            <div className="relative bg-white border border-slate-200 rounded-xl shadow-lg focus-within:ring-2 focus-within:ring-indigo-100 focus-within:border-indigo-400 transition-all">
                <textarea
                    ref={textareaRef}
                    rows={1}
                    className="w-full py-3 pl-4 pr-24 bg-transparent border-none rounded-xl focus:ring-0 resize-none max-h-48 overflow-y-auto text-slate-700 placeholder-slate-400 leading-relaxed"
                    placeholder="Message Claude..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={disabled}
                />
                <div className="absolute right-2 bottom-2 flex items-center gap-1">
                    <FileUploadButton 
                        onFilesSelected={handleFilesSelected}
                        disabled={disabled}
                    />
                    <button 
                        onClick={handleSubmit} 
                        disabled={(!input.trim() && attachedFiles.length === 0) || disabled}
                        className={`p-2 rounded-lg transition-colors duration-200 ${
                           (input.trim() || attachedFiles.length > 0) && !disabled 
                             ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm' 
                             : 'bg-slate-100 text-slate-300 cursor-not-allowed'
                        }`}
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19V5m0 0l-7 7m7-7l7 7" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
}
