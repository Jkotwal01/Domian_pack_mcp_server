import React from 'react';
import SectionHeader from '../common/SectionHeader';
import KeyTermBadge from '../domain/KeyTermBadge';

/**
 * Key terms section component - displays all key terms with add/delete functionality
 */
export default function KeyTermsSection({
  keyTerms,
  onAdd,
  onDelete
}) {
  return (
    <div className="border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
      <SectionHeader
        icon={
          <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        }
        title="Key Terms"
        count={keyTerms?.length || 0}
        onAdd={onAdd}
        addButtonText="Add Term"
        addButtonColor="amber"
      />
      
      <div className="p-6 bg-white">
        {keyTerms && keyTerms.length > 0 ? (
          <div className="flex flex-wrap gap-3">
            {keyTerms.map((term, idx) => (
              <KeyTermBadge
                key={idx}
                term={term}
                index={idx}
                onDelete={onDelete}
              />
            ))}
          </div>
        ) : (
          <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-3">
            <p className="font-bold">No key terms defined yet.</p>
            <p className="text-xs">Click "Add Term" to create your first key term.</p>
          </div>
        )}
      </div>
    </div>
  );
}
