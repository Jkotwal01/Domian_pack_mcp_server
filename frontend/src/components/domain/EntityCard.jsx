import React from 'react';
import ActionButtons from '../common/ActionButtons';

/**
 * Entity card component displaying entity information with edit/duplicate/delete actions
 */
export default function EntityCard({ entity, index, onEdit, onDuplicate, onDelete }) {
  return (
    <div className="p-6 border border-slate-100 rounded-2xl bg-gradient-to-br from-white to-slate-50/30 shadow-sm hover:shadow-lg transition-all group relative">
      {/* Action buttons */}
      <ActionButtons
        onEdit={() => onEdit(index, entity)}
        onDuplicate={() => onDuplicate(index)}
        onDelete={() => onDelete(index)}
        showDuplicate={true}
      />

      {/* Entity header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h4 className="text-lg font-black text-slate-900 mb-1">{entity.name}</h4>
          {entity.type && (
            <span className="inline-block px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-xs font-bold border border-blue-100">
              {entity.type}
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      {entity.description && (
        <p className="text-sm text-slate-600 mb-4 leading-relaxed">
          {entity.description}
        </p>
      )}

      {/* Attributes */}
      {entity.attributes && entity.attributes.length > 0 && (
        <div className="mb-4">
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">
            Attributes
          </p>
          <div className="flex flex-wrap gap-2">
            {entity.attributes.map((attr, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-slate-50 text-slate-700 rounded-lg text-xs font-bold border border-slate-100"
              >
                {typeof attr === 'string' ? attr : attr.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Synonyms */}
      {entity.synonyms && entity.synonyms.length > 0 && (
        <div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">
            Synonyms
          </p>
          <div className="flex flex-wrap gap-2">
            {entity.synonyms.map((syn, sIdx) => (
              <span
                key={sIdx}
                className="px-3 py-1 bg-purple-50 text-purple-600 rounded-lg text-xs font-bold border border-purple-100"
              >
                {syn}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
