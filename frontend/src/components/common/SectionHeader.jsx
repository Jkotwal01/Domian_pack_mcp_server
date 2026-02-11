import React from 'react';

/**
 * Reusable section header component with title, count badge, and action button
 */
export default function SectionHeader({ 
  icon, 
  title, 
  count, 
  onAdd, 
  addButtonText, 
  addButtonColor = 'blue' 
}) {
  const colorClasses = {
    blue: 'bg-blue-600 hover:bg-blue-700',
    purple: 'bg-purple-600 hover:bg-purple-700',
    emerald: 'bg-emerald-600 hover:bg-emerald-700',
    amber: 'bg-amber-600 hover:bg-amber-700'
  };

  return (
    <div className="px-6 py-4 bg-slate-50/50 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        {icon}
        <span className="font-black text-slate-900">{title}</span>
        <span className="bg-white border border-slate-100 text-slate-600 px-2.5 py-0.5 rounded-full text-xs font-bold">
          {count}
        </span>
      </div>
      {onAdd && (
        <button
          onClick={onAdd}
          className={`px-4 py-2 ${colorClasses[addButtonColor]} text-white text-xs font-bold rounded-lg transition-colors flex items-center space-x-2`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>{addButtonText}</span>
        </button>
      )}
    </div>
  );
}
