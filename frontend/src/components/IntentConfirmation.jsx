import React from 'react';

/**
 * Component for user to review and confirm/reject a proposed operation
 */
export default function IntentConfirmation({ operations, onConfirm, disabled }) {
  if (!operations || operations.length === 0) return null;

  return (
    <div className="mt-4 border border-indigo-100 bg-indigo-50/30 rounded-lg overflow-hidden shadow-sm">
      <div className="px-4 py-2 bg-indigo-50 border-b border-indigo-100 flex items-center justify-between">
        <h4 className="text-xs font-bold text-indigo-700 uppercase tracking-wider flex items-center">
          <span className="mr-2">🔧</span> Proposed Operations
        </h4>
        <span className="text-[10px] text-indigo-500 font-medium bg-white px-2 py-0.5 rounded-full border border-indigo-100">
          {operations.length} {operations.length === 1 ? 'Action' : 'Actions'}
        </span>
      </div>
      
      <div className="p-4 space-y-3">
        <div className="space-y-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
          {operations.map((op, i) => (
            <div key={i} className="text-xs font-mono bg-white p-2 rounded border border-indigo-50 text-indigo-900 break-all whitespace-pre-wrap shadow-sm">
              <span className="text-pink-600 font-bold">{op.action.toUpperCase()}</span>{' '}
              <span className="text-slate-400">at</span>{' '}
              <span className="text-indigo-600">/{op.path.join('/')}</span>
              {op.value && (
                <div className="mt-1 text-slate-500 pl-4 border-l-2 border-slate-100">
                  {typeof op.value === 'object' ? JSON.stringify(op.value, null, 2) : String(op.value)}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center space-x-3 pt-2">
          <button
            onClick={() => onConfirm(true)}
            disabled={disabled}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-md transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none shadow-sm shadow-indigo-200"
          >
            Approve & Apply
          </button>
          <button
            onClick={() => onConfirm(false)}
            disabled={disabled}
            className="bg-white hover:bg-slate-50 text-slate-600 font-semibold py-2 px-4 rounded-md border border-slate-200 transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none shadow-sm"
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}
