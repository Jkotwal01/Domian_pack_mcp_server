import React from 'react';

/**
 * Key term badge component with delete action
 */
export default function KeyTermBadge({ term, index, onDelete }) {
  return (
    <span className="group px-4 py-2 bg-gradient-to-r from-amber-50 to-orange-50 text-amber-700 rounded-xl text-sm font-bold border border-amber-200 shadow-sm hover:shadow-md transition-all flex items-center gap-2">
      {term}
      {onDelete && (
        <button
          onClick={() => onDelete(index)}
          className="opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-600"
          title="Delete"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </span>
  );
}
