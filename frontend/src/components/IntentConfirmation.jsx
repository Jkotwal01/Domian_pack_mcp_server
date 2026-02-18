import React from 'react';

/**
 * Component for user to review and confirm/reject a proposed operation
 * Optimized for showing the raw payload clearly
 */
export default function IntentConfirmation({ operations, onConfirm, disabled, readOnly = false }) {
  // Handle both array of operations and the PatchList object
  const patchList = (operations && operations.patches) ? operations.patches : (Array.isArray(operations) ? operations : []);
  
  if (patchList.length === 0) return null;

  return (
    <div className="mt-6 border border-slate-200 bg-white rounded-xl overflow-hidden shadow-sm transition-all hover:shadow-md">
      <div className="px-5 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
        <h4 className="text-[11px] font-bold text-slate-600 uppercase tracking-widest flex items-center">
          <span className="mr-2 text-indigo-500">⚡</span> 
          {readOnly ? 'Proposed Configuration Changes' : 'Review Proposed Changes'}
        </h4>
        <span className="text-[10px] text-slate-400 font-bold bg-white px-2.5 py-1 rounded-lg border border-slate-200 uppercase tracking-tighter">
          {patchList.length} {patchList.length === 1 ? 'Patch' : 'Patches'}
        </span>
      </div>
      
      <div className="p-0 divide-y divide-slate-50">
        <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
          {patchList.map((op, i) => (
            <div key={i} className="p-5 hover:bg-slate-50/50 transition-colors">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider shadow-xs ${
                    op.type?.startsWith('add') ? 'bg-emerald-500 text-white' : 
                    op.type?.startsWith('delete') ? 'bg-rose-500 text-white' : 'bg-indigo-500 text-white'
                  }`}>
                    {op.type?.replace(/_/g, ' ')}
                  </span>
                  {op.target_name && (
                    <span className="text-[11px] font-bold text-slate-700 truncate max-w-[150px]">
                      {op.target_name}
                    </span>
                  )}
                  {op.parent_name && (
                    <span className="text-[10px] text-slate-400">in {op.parent_name}</span>
                  )}
                </div>
              </div>
              
              {op.payload && (
                <div className="rounded-lg overflow-hidden border border-slate-200/60 bg-slate-900 shadow-inner group relative">
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => navigator.clipboard.writeText(JSON.stringify(op.payload, null, 2))}
                      className="text-[9px] bg-slate-800 text-slate-400 hover:text-white px-2 py-1 rounded border border-slate-700 transition-colors"
                    >
                      COPY PAYLOAD
                    </button>
                  </div>
                  <pre className="p-4 text-[11px] leading-relaxed font-mono overflow-x-auto text-indigo-200">
                    <code className="text-emerald-400">
                      {JSON.stringify(op.payload, null, 2)}
                    </code>
                  </pre>
                </div>
              )}

              {!op.payload && (op.new_value !== undefined) && (
                <div className="p-3 bg-indigo-50/50 rounded-lg border border-indigo-100 flex items-center justify-between">
                   <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Update Value</span>
                   <span className="text-[13px] font-mono text-indigo-700 font-bold">{String(op.new_value)}</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {!readOnly && (
          <div className="p-5 bg-slate-50/80 backdrop-blur-sm border-t border-slate-100 flex items-center space-x-4">
            <button
              onClick={() => onConfirm(true)}
              disabled={disabled}
              className="flex-1 bg-linear-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white font-bold py-3 px-6 rounded-xl transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none shadow-[0_4px_12px_rgba(79,70,229,0.3)] hover:shadow-indigo-300"
            >
              Approve Changes
            </button>
            <button
              onClick={() => onConfirm(false)}
              disabled={disabled}
              className="bg-white hover:bg-slate-50 text-slate-500 font-bold py-3 px-6 rounded-xl border border-slate-200 transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none hover:text-rose-500 hover:border-rose-100"
            >
              Reject
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
