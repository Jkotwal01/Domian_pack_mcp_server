import React from 'react';

export default function FileAttachment({ file }) {
  const isImage = file.type?.startsWith('image/');
  
  // Get file icon based on type
  const getFileIcon = () => {
    if (isImage) return '🖼️';
    if (file.type?.includes('pdf')) return '📄';
    if (file.type?.includes('text')) return '📝';
    if (file.type?.includes('video')) return '🎥';
    if (file.type?.includes('audio')) return '🎵';
    return '📎';
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="mt-2 max-w-sm">
      {isImage && file.preview ? (
        // Image preview
        <div className="relative group">
          <img 
            src={file.preview} 
            alt={file.name}
            className="rounded-lg border border-slate-200 shadow-sm max-h-64 w-auto hover:shadow-md transition-shadow cursor-pointer"
          />
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent rounded-b-lg p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-white text-xs font-medium truncate">{file.name}</p>
            <p className="text-white/80 text-xs">{formatFileSize(file.size)}</p>
          </div>
        </div>
      ) : (
        // File card for non-images
        <div className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer">
          <div className="text-3xl flex-shrink-0">
            {getFileIcon()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-700 truncate">
              {file.name}
            </p>
            <p className="text-xs text-slate-500">
              {formatFileSize(file.size)}
            </p>
          </div>
          <svg className="w-5 h-5 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </div>
      )}
    </div>
  );
}
