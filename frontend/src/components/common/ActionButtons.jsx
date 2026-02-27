import React from 'react';

/**
 * Reusable action buttons component for edit, duplicate, and delete operations
 * Appears on hover with smooth transitions
 */
export default function ActionButtons({ 
  onEdit, 
  onDuplicate, 
  onDelete,
  showDuplicate = false 
}) {
  return (
    <div className="flex items-center space-x-1.5 translate-z-0">
      {onEdit && (
        <button
          onClick={onEdit}
          className="p-1.5 bg-white border border-slate-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
          title="Edit"
        >
          <svg className="w-3 h-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
      )}
      
      {showDuplicate && onDuplicate && (
        <button
          onClick={onDuplicate}
          className="p-1.5 bg-white border border-slate-200 rounded-lg hover:bg-purple-50 hover:border-purple-300 transition-colors"
          title="Duplicate"
        >
          <svg className="w-3 h-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
      )}
      
      {onDelete && (
        <button
          onClick={onDelete}
          className="p-1.5 bg-white border border-slate-200 rounded-lg hover:bg-red-50 hover:border-red-300 transition-colors"
          title="Delete"
        >
          <svg className="w-3 h-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      )}
    </div>
  );
}
