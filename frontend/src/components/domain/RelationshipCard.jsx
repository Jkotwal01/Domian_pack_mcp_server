import React from 'react';
import ActionButtons from '../common/ActionButtons';

/**
 * Relationship card component displaying relationship information with edit/delete actions
 */
export default function RelationshipCard({ relationship, index, onEdit, onDelete }) {
  return (
    <div className="p-6 border border-slate-100 rounded-3xl bg-white shadow-[0_4px_20px_rgba(0,0,0,0.01)] hover:shadow-[0_15px_40px_rgba(99,102,241,0.06)] transition-all duration-500 group relative hover:-translate-y-1">
      
      <div className="relative z-0">
        {/* Relationship flow */}
        <div className="flex items-center justify-center space-x-4 mb-5">
            <div className="px-3 py-1.5 bg-indigo-50/50 rounded-xl border border-indigo-100/50">
                <span className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">
                {relationship.from}
                </span>
            </div>
            
            <div className="flex flex-col items-center">
                <div className="w-12 h-[2px] bg-linear-to-r from-indigo-200 via-violet-300 to-indigo-200"></div>
                <div className="text-[8px] font-black text-slate-300 uppercase tracking-widest mt-1">FLOW</div>
            </div>

            <div className="px-3 py-1.5 bg-violet-50/50 rounded-xl border border-violet-100/50">
                <span className="text-[10px] font-black text-violet-600 uppercase tracking-widest">
                {relationship.to}
                </span>
            </div>
        </div>

        {/* Relationship name */}
        <div className="text-center mb-4">
            <h5 className="text-sm font-black text-slate-900 tracking-tight group-hover:text-indigo-600 transition-colors uppercase">
                {relationship.name}
            </h5>
            {relationship.description && (
                <p className="text-[11px] text-slate-500 mt-2 leading-relaxed font-semibold italic opacity-80">
                    "{relationship.description}"
                </p>
            )}
        </div>

        {/* Attributes */}
        {relationship.attributes && relationship.attributes.length > 0 && (
          <div className="pt-4 border-t border-slate-50 mt-4 flex flex-col items-center">
            <p className="text-[8px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2.5">Properties</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {relationship.attributes.map((attr, idx) => (
                <span key={idx} className="px-2.5 py-1 bg-slate-50 text-[10px] font-bold text-slate-500 border border-slate-100/50 rounded-lg hover:bg-white hover:shadow-sm transition-all">
                  {typeof attr === 'string' ? attr : attr.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action buttons - positioned on top at end of DOM */}
      <div className="absolute top-5 right-5 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 z-20">
        <ActionButtons
          onEdit={() => onEdit(index, relationship)}
          onDelete={() => onDelete(index)}
        />
      </div>
    </div>
  );
}
