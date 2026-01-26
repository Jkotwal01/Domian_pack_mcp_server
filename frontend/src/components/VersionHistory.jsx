/**
 * Component to display the list of versions and allow rollbacks
 */
export default function VersionHistory({ versions, onRollback, activeVersion }) {
  if (!versions || versions.length === 0) {
    return (
      <div className="px-4 py-8 text-center text-slate-500 italic text-xs">
        No version history available for this session.
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-hidden flex flex-col">
      <div className="px-4 py-2 border-b border-slate-700/50 flex items-center justify-between">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
          Version History
        </h3>
        <span className="text-[10px] text-slate-400 bg-slate-700/50 px-1.5 py-0.5 rounded">
          {versions.length}
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar px-2 py-3 space-y-2">
        {versions.map((v) => (
          <div 
            key={v.version} 
            className={`
              p-2.5 rounded-lg border transition-all duration-200 group
              ${v.version === activeVersion 
                ? 'bg-indigo-500/10 border-indigo-500/30' 
                : 'bg-slate-700/30 border-slate-700 hover:border-slate-600'}
            `}
          >
            <div className="flex items-center justify-between mb-1">
              <span className={`text-xs font-bold ${v.version === activeVersion ? 'text-indigo-400' : 'text-slate-300'}`}>
                Version {v.version}
              </span>
              <span className="text-[9px] text-slate-500">
                {new Date(v.created_at).toLocaleDateString()}
              </span>
            </div>
            
            <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-2 italic">
              "{v.reason || 'No description'}"
            </p>

            <button
              onClick={() => onRollback(v.version)}
              disabled={v.version === activeVersion}
              className={`
                w-full py-1 rounded text-[10px] font-bold uppercase tracking-tight transition-colors
                ${v.version === activeVersion
                  ? 'bg-indigo-500/20 text-indigo-400 cursor-default'
                  : 'bg-slate-600 hover:bg-indigo-600 text-slate-200 hover:text-white'}
              `}
            >
              {v.version === activeVersion ? 'Current Version' : 'Rollback to here'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
