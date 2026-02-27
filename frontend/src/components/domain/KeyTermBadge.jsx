import React from 'react';

/**
 * Key term badge component with delete action
 */
export default function KeyTermBadge({ term, index, onDelete }) {
  return (
    <span className="group px-5 py-2.5 bg-white text-slate-700 rounded-2xl text-[11px] font-black uppercase tracking-[0.15em] border border-slate-100 shadow-[0_4px_15px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_25px_rgba(79,70,229,0.06)] hover:border-indigo-100/50 hover:text-indigo-600 transition-all duration-300 flex items-center gap-3 hover:-translate-y-0.5">
      <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full group-hover:scale-125 transition-transform"></span>
      {term}
      {onDelete && (
        <button
          onClick={() => onDelete(index)}
          className="opacity-0 group-hover:opacity-100 transition-all hover:text-red-500 transform translate-x-2 group-hover:translate-x-0"
          title="Delete"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </span>
  );
}
