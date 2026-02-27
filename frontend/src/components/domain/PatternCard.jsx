import React from 'react';
import ActionButtons from '../common/ActionButtons';

/**
 * Extraction pattern card component displaying pattern information with edit/delete actions
 */
export default function PatternCard({ pattern, index, onEdit, onDelete }) {
  return (
    <div className="p-5 flex items-center justify-between group bg-white border border-slate-100 rounded-2xl hover:shadow-[0_10px_25px_rgba(0,0,0,0.03)] transition-all duration-300 relative hover:-translate-y-0.5 mb-2 last:mb-0">

      {/* Pattern info */}
      <div className="space-y-2 pr-24 flex-1">
        <div className="flex items-center space-x-3">
            <code className="text-[11px] font-mono font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-lg border border-rose-100/50">
            {pattern.pattern}
            </code>
            <span className="text-[8px] font-black text-rose-300 uppercase tracking-widest bg-rose-50/50 px-1.5 py-0.5 rounded border border-rose-100/20">Regex</span>
        </div>
        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
          Extracts <span className="text-indigo-600 font-black tracking-widest">{pattern.attribute}</span> for{' '}
          <span className="text-violet-600 font-black tracking-widest">{pattern.entity_type}</span>
        </p>
      </div>

      {/* Confidence indicator */}
      <div className="flex flex-col items-center space-y-1.5 min-w-[80px]">
        <div className="w-16 h-1.5 bg-slate-100/80 rounded-full overflow-hidden border border-slate-200/20">
          <div
            className="h-full bg-linear-to-r from-emerald-400 to-emerald-600 shadow-[0_0_8px_rgba(16,185,129,0.3)] transition-all duration-700"
            style={{ width: `${(pattern.confidence || 0) * 100}%` }}
          ></div>
        </div>
        <span className="text-[10px] font-black text-slate-400 tracking-tighter">
          {Math.round((pattern.confidence || 0) * 100)}% CONFIDENCE
        </span>
      </div>

      {/* Action buttons - positioned on top at end of DOM */}
      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 z-20">
        <ActionButtons
            onEdit={() => onEdit(index, pattern)}
            onDelete={() => onDelete(index)}
        />
      </div>
    </div>
  );
}
