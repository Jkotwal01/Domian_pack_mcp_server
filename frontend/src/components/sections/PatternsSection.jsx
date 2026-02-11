import React from 'react';
import SectionHeader from '../common/SectionHeader';
import PatternCard from '../domain/PatternCard';

/**
 * Extraction patterns section component - displays all patterns with add/edit/delete functionality
 */
export default function PatternsSection({
  patterns,
  onAdd,
  onEdit,
  onDelete
}) {
  return (
    <div className="border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
      <SectionHeader
        icon={
          <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        }
        title="Extraction Patterns"
        count={patterns?.length || 0}
        onAdd={onAdd}
        addButtonText="Add Pattern"
        addButtonColor="emerald"
      />
      
      <div className="divide-y divide-slate-50 bg-white">
        {patterns && patterns.length > 0 ? (
          patterns.map((pattern, idx) => (
            <PatternCard
              key={idx}
              pattern={pattern}
              index={idx}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))
        ) : (
          <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-3">
            <p className="font-bold">No extraction patterns defined yet.</p>
            <p className="text-xs">Click "Add Pattern" to create your first extraction pattern.</p>
          </div>
        )}
      </div>
    </div>
  );
}
