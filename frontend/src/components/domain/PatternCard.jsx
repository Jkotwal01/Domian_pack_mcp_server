import React from 'react';
import ActionButtons from '../common/ActionButtons';

/**
 * Extraction pattern card component displaying pattern information with edit/delete actions
 */
export default function PatternCard({ pattern, index, onEdit, onDelete }) {
  return (
    <div className="p-4 flex items-center justify-between group hover:bg-slate-50/50 transition-colors relative">
      {/* Action buttons */}
      <ActionButtons
        onEdit={() => onEdit(index, pattern)}
        onDelete={() => onDelete(index)}
      />

      {/* Pattern info */}
      <div className="space-y-1 pr-20">
        <code className="text-xs font-mono text-rose-600 bg-rose-50 px-2 py-0.5 rounded">
          {pattern.pattern}
        </code>
        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">
          Extracts <span className="text-slate-600">{pattern.attribute}</span> for{' '}
          <span className="text-slate-600">{pattern.entity_type}</span>
        </p>
      </div>

      {/* Confidence indicator */}
      <div className="flex items-center space-x-2">
        <div className="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500"
            style={{ width: `${(pattern.confidence || 0) * 100}%` }}
          ></div>
        </div>
        <span className="text-[10px] font-black text-slate-400">
          {(pattern.confidence || 0) * 100}%
        </span>
      </div>
    </div>
  );
}
