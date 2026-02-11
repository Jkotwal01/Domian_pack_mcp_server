import React from 'react';
import SectionHeader from '../common/SectionHeader';
import EntityCard from '../domain/EntityCard';

/**
 * Entities section component - displays all entities with add/edit/delete functionality
 */
export default function EntitiesSection({
  entities,
  onAdd,
  onEdit,
  onDuplicate,
  onDelete
}) {
  return (
    <div className="border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
      <SectionHeader
        icon={
          <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        }
        title="Entities"
        count={entities?.length || 0}
        onAdd={onAdd}
        addButtonText="Add Entity"
        addButtonColor="blue"
      />
      
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 bg-white">
        {entities && entities.length > 0 ? (
          entities.map((entity, idx) => (
            <EntityCard
              key={idx}
              entity={entity}
              index={idx}
              onEdit={onEdit}
              onDuplicate={onDuplicate}
              onDelete={onDelete}
            />
          ))
        ) : (
          <div className="col-span-2 py-12 flex flex-col items-center justify-center text-slate-400 space-y-3">
            <p className="font-bold">No entities defined yet.</p>
            <p className="text-xs">Click "Add Entity" to create your first entity.</p>
          </div>
        )}
      </div>
    </div>
  );
}
