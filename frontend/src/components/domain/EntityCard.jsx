import React from 'react';
import ActionButtons from '../common/ActionButtons';

/**
 * Entity card component displaying entity information with edit/duplicate/delete actions
 */
export default function EntityCard({ entity, index, onEdit, onDuplicate, onDelete }) {
  return (
    <div className="p-7 border border-slate-100 rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,0,0,0.02)] hover:shadow-[0_20px_50px_rgba(79,70,229,0.08)] transition-all duration-500 group relative hover:-translate-y-1">
      {/* Glow Effect on Hover */}
      <div className="absolute inset-0 bg-linear-to-br from-indigo-50/0 to-purple-50/0 group-hover:from-indigo-50/30 group-hover:to-purple-50/30 rounded-3xl transition-all duration-500 -z-0"></div>


      <div className="relative z-10">
        {/* Entity header */}
        <div className="flex items-start justify-between mb-5">
          <div className="flex-1">
            <h4 className="text-xl font-black text-slate-900 mb-2 tracking-tight group-hover:text-indigo-600 transition-colors">
              {entity.name}
            </h4>
            {entity.type && (
              <span className="inline-block px-3 py-1 bg-indigo-50 text-indigo-600 rounded-xl text-[10px] font-black uppercase tracking-widest border border-indigo-100/50">
                {entity.type}
              </span>
            )}
          </div>
        </div>

        {/* Description */}
        {entity.description && (
          <p className="text-[13px] text-slate-500 mb-6 leading-relaxed font-medium">
            {entity.description}
          </p>
        )}

        {/* Attributes */}
        {entity.attributes && entity.attributes.length > 0 && (
          <div className="mb-6">
            <p className="text-[9px] font-black text-slate-300 uppercase tracking-[0.2em] mb-3">
              Core Attributes
            </p>
            <div className="flex flex-wrap gap-2">
              {entity.attributes.map((attr, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 bg-slate-50/80 text-slate-600 rounded-lg text-[11px] font-bold border border-slate-100/50 hover:bg-white hover:shadow-sm transition-all"
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
            <p className="text-[9px] font-black text-slate-300 uppercase tracking-[0.2em] mb-3">
              Contextual Synonyms
            </p>
            <div className="flex flex-wrap gap-2">
              {entity.synonyms.map((syn, sIdx) => (
                <span
                  key={sIdx}
                  className="px-3 py-1.5 bg-emerald-50 text-emerald-600 rounded-lg text-[11px] font-bold border border-emerald-100/30 hover:bg-emerald-100/20 transition-all"
                >
                  {syn}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action buttons - positioned elegantly on top */}
      <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 z-20 font-bold">
        <ActionButtons
          onEdit={() => onEdit(index, entity)}
          onDuplicate={() => onDuplicate(index)}
          onDelete={() => onDelete(index)}
          showDuplicate={true}
        />
      </div>
    </div>
  );
}
