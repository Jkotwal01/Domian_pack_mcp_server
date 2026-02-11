import React, { useState, useEffect } from 'react';
import { getVersionYAML, compareVersions } from '../services/api';

export default function VersionComparison({ session1, version1, session2, version2, onClose }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);

  useEffect(() => {
    loadComparison();
  }, [session1, version1, session2, version2]);

  const loadComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await compareVersions(session1, version1, session2, version2);
      setComparisonData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getChangeColor = (changeType) => {
    switch (changeType) {
      case 'added':
        return 'bg-emerald-900/30 border-l-4 border-emerald-500';
      case 'removed':
        return 'bg-red-900/30 border-l-4 border-red-500';
      case 'modified':
        return 'bg-amber-900/30 border-l-4 border-amber-500';
      default:
        return 'bg-slate-800';
    }
  };

  const getChangeIcon = (changeType) => {
    switch (changeType) {
      case 'added':
        return (
          <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        );
      case 'removed':
        return (
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        );
      case 'modified':
        return (
          <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div>
            <h2 className="text-xl font-semibold text-white">Version Comparison</h2>
            {comparisonData && (
              <p className="text-sm text-slate-400 mt-1">
                {comparisonData.domain_1} v{version1} ↔ {comparisonData.domain_2} v{version2}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors"
            title="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 text-red-200">
              <p className="font-semibold">Error loading comparison</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {comparisonData && !loading && (
            <div className="space-y-4">
              {/* Summary */}
              <div className="bg-slate-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {comparisonData.total_changes} {comparisonData.total_changes === 1 ? 'Change' : 'Changes'} Found
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                      Comparing version {version1} with version {version2}
                    </p>
                  </div>
                  <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-emerald-500 rounded"></div>
                      <span className="text-slate-300">Added</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded"></div>
                      <span className="text-slate-300">Removed</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-amber-500 rounded"></div>
                      <span className="text-slate-300">Modified</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Differences List */}
              {comparisonData.differences.length > 0 ? (
                <div className="space-y-2">
                  {comparisonData.differences.map((diff, index) => (
                    <div
                      key={index}
                      className={`rounded-lg p-4 ${getChangeColor(diff.change_type)}`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 mt-0.5">
                          {getChangeIcon(diff.change_type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <code className="text-sm font-mono text-indigo-300 bg-slate-900/50 px-2 py-1 rounded">
                              {diff.field}
                            </code>
                            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-900/50 text-slate-300 uppercase font-semibold">
                              {diff.change_type}
                            </span>
                          </div>
                          <div className="space-y-1 text-sm">
                            {diff.old_value !== null && (
                              <div className="flex gap-2">
                                <span className="text-red-400 font-mono">-</span>
                                <span className="text-slate-300 font-mono break-all">
                                  {typeof diff.old_value === 'object' 
                                    ? JSON.stringify(diff.old_value, null, 2)
                                    : String(diff.old_value)}
                                </span>
                              </div>
                            )}
                            {diff.new_value !== null && (
                              <div className="flex gap-2">
                                <span className="text-emerald-400 font-mono">+</span>
                                <span className="text-slate-300 font-mono break-all">
                                  {typeof diff.new_value === 'object'
                                    ? JSON.stringify(diff.new_value, null, 2)
                                    : String(diff.new_value)}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">
                  <svg className="w-16 h-16 mx-auto mb-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-lg font-medium">No differences found</p>
                  <p className="text-sm mt-1">These versions are identical</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
