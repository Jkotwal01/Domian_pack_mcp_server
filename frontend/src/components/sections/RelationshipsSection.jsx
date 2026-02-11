import React from 'react';
import SectionHeader from '../common/SectionHeader';
import RelationshipCard from '../domain/RelationshipCard';

/**
 * Relationships section component - displays all relationships with add/edit/delete functionality
 */
export default function RelationshipsSection({
  relationships,
  onAdd,
  onEdit,
  onDelete
}) {
  return (
    <div className="border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
      <SectionHeader
        icon={
          <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        }
        title="Relationships"
        count={relationships?.length || 0}
        onAdd={onAdd}
        addButtonText="Add Relationship"
        addButtonColor="purple"
      />
      
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4 bg-white">
        {relationships && relationships.length > 0 ? (
          relationships.map((rel, idx) => (
            <RelationshipCard
              key={idx}
              relationship={rel}
              index={idx}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))
        ) : (
          <div className="col-span-2 py-12 flex flex-col items-center justify-center text-slate-400 space-y-3">
            <p className="font-bold">No relationships defined yet.</p>
            <p className="text-xs">Click "Add Relationship" to create your first relationship.</p>
          </div>
        )}
      </div>
    </div>
  );
}
