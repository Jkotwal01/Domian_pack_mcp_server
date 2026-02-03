import React, { useState } from 'react';
import YAMLViewer from './YAMLViewer';
import { getVersionYAML } from '../services/api';

/**
 * Enhanced Version History Component
 * - View YAML for each version
 * - Delete specific versions
 * - Rollback functionality
 * - Responsive design
 */
export default function VersionHistory({ 
  versions, 
  onRollback, 
  activeVersion,
  sessionId,
  onDeleteVersion 
}) {
  const [yamlViewerOpen, setYamlViewerOpen] = useState(false);
  const [yamlContent, setYamlContent] = useState('');
  const [yamlTitle, setYamlTitle] = useState('');
  const [loadingYaml, setLoadingYaml] = useState(false);

  if (!versions || versions.length === 0) {
    return (
      <div className="px-4 py-8 text-center text-slate-500 italic text-xs">
        No version history available for this session.
      </div>
    );
  }

  const handleViewYAML = async (version) => {
    if (!sessionId) {
      alert('Session ID not available');
      return;
    }

    try {
      setLoadingYaml(true);
      const data = await getVersionYAML(sessionId, version.version);
      setYamlContent(data.yaml_content);
      setYamlTitle(`Version ${version.version} - ${data.domain_name}`);
      setYamlViewerOpen(true);
    } catch (error) {
      console.error('Failed to load YAML:', error);
      alert('Failed to load YAML content');
    } finally {
      setLoadingYaml(false);
    }
  };

  const handleDeleteVersion = (version) => {
    if (version.version === activeVersion) {
      alert('Cannot delete the current active version');
      return;
    }

    if (window.confirm(`Are you sure you want to delete Version ${version.version}?\n\nReason: ${version.reason || 'No description'}`)) {
      onDeleteVersion(version.version);
    }
  };

  return (
    <>
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
              
              <p className="text-[12px] text-slate-300 leading-relaxed mb-3">
                {v.reason || 'No description provided'}
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-2 pt-1">
                {/* View Button */}
                <button
                  onClick={() => handleViewYAML(v)}
                  disabled={loadingYaml}
                  className="flex-1 py-1.5 bg-emerald-600/20 hover:bg-emerald-600 text-emerald-400 hover:text-white rounded text-[10px] font-bold uppercase tracking-wider transition-all disabled:opacity-50 flex items-center justify-center gap-1.5 border border-emerald-500/20"
                  title="View YAML content"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span>View</span>
                </button>

                {/* Rollback Button */}
                <button
                  onClick={() => onRollback(v.version)}
                  disabled={v.version === activeVersion}
                  className={`
                    flex-1 py-1.5 rounded text-[10px] font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-1.5
                    ${v.version === activeVersion
                      ? 'bg-indigo-500/10 text-indigo-400 cursor-default border border-indigo-500/20'
                      : 'bg-slate-600 hover:bg-indigo-600 text-slate-200 hover:text-white border border-slate-500/30'}
                  `}
                  title={v.version === activeVersion ? 'Current version' : 'Rollback to this version'}
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>{v.version === activeVersion ? 'Current' : 'Rollback'}</span>
                </button>

                {/* Delete Button (Small icon-only to focus on View/Rollback) */}
                {onDeleteVersion && v.version !== activeVersion && (
                  <button
                    onClick={() => handleDeleteVersion(v)}
                    className="p-1.5 bg-slate-700 hover:bg-red-600 text-slate-400 hover:text-white rounded border border-slate-600 transition-colors"
                    title="Delete this version"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* YAML Viewer Modal */}
      {yamlViewerOpen && (
        <YAMLViewer
          yamlContent={yamlContent}
          title={yamlTitle}
          onClose={() => setYamlViewerOpen(false)}
        />
      )}
    </>
  );
}
