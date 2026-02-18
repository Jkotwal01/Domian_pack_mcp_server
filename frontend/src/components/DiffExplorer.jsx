import React from 'react';

/**
 * Component to visualize the results of a change (the diff)
 */
export default function DiffExplorer({ diff, version }) {
  if (!diff || !diff.summary || !diff.summary.has_changes) return null;

  const { added, removed, changed, type_changes } = diff;

  const renderSection = (title, items, bgColor, textColor, label) => {
    const keys = Object.keys(items || {});
    if (keys.length === 0) return null;

    return (
      <div className="space-y-1 w-full min-w-0">
        <h5 className={`text-[10px] font-bold uppercase tracking-tight ${textColor}`}>{title}</h5>
        <div className="space-y-1 w-full min-w-0">
          {keys.map(path => (
            <div key={path} className={`text-xs p-1.5 rounded ${bgColor} border-l-2 border-current font-mono break-all w-full min-w-0 overflow-hidden shadow-xs`}>
              <span className="opacity-50 text-[10px] block border-b border-black/5 mb-1 truncate" title={path}>{path}</span>
              {label === 'Δ' ? (
                <div className="flex flex-col space-y-1 w-full min-w-0">
                  <div className="text-red-500 line-through opacity-70 break-all">-{JSON.stringify(items[path].old)}</div>
                  <div className="text-green-600 break-all">+{JSON.stringify(items[path].new)}</div>
                </div>
              ) : (
                <div className={`${textColor} break-all w-full min-w-0`}>{label} {JSON.stringify(items[path])}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="mt-4 border border-emerald-100 bg-emerald-50/20 rounded-lg overflow-hidden">
      <div className="px-3 py-1.5 bg-emerald-50/50 border-b border-emerald-100 flex items-center justify-between">
        <h4 className="text-[10px] font-bold text-emerald-700 uppercase tracking-widest flex items-center">
          <span className="mr-1.5 uppercase">v{version}</span> Change Log
        </h4>
        <span className="text-[10px] text-emerald-600 font-medium">
          {diff.summary.total_changes} Changes
        </span>
      </div>
      
      <div className="p-3 space-y-4 max-h-64 overflow-y-auto overflow-x-hidden custom-scrollbar w-full">
        {renderSection("Added", added, "bg-green-50/50", "text-green-700", "+")}
        {renderSection("Removed", removed, "bg-red-50/50", "text-red-700", "-")}
        {renderSection("Changed", changed, "bg-amber-50/50", "text-amber-700", "Δ")}
        {renderSection("Type Changes", type_changes, "bg-purple-50/50", "text-purple-700", "±")}
      </div>
    </div>
  );
}
