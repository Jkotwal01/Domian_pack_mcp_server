import React from 'react';
import ActionButtons from '../common/ActionButtons';

/**
 * Relationship card component displaying relationship information with edit/delete actions
 */
export default function RelationshipCard({ relationship, index, onEdit, onDelete }) {
  return (
    <div className="p-4 border border-slate-100 rounded-xl bg-slate-50/30 space-y-3 group relative hover:shadow-md transition-shadow">
      {/* Action buttons */}
      <ActionButtons
        onEdit={() => onEdit(index, relationship)}
        onDelete={() => onDelete(index)}
      />

      {/* Relationship flow */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-black text-blue-600 uppercase tracking-wider">
          {relationship.from}
        </span>
        <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
        <span className="text-[10px] font-black text-blue-600 uppercase tracking-wider">
          {relationship.to}
        </span>
      </div>

      {/* Relationship name */}
      <h5 className="text-sm font-black text-slate-800 text-center tracking-tight">{relationship.name}</h5>

      {/* Description */}
      {relationship.description && (
        <p className="text-[11px] text-slate-500 text-center leading-relaxed">
          {relationship.description}
        </p>
      )}

      {/* Attributes */}
      {relationship.attributes && relationship.attributes.length > 0 && (
        <div className="pt-2 border-t border-slate-100 mt-2">
          <div className="flex flex-wrap gap-1.5 justify-center">
            {relationship.attributes.map((attr, idx) => (
              <span key={idx} className="px-2 py-0.5 bg-white text-[9px] font-bold text-slate-400 border border-slate-100 rounded-md">
                {typeof attr === 'string' ? attr : attr.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
