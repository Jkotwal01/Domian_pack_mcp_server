import React, { useState, useEffect } from 'react';
import { getAllSessions, getAllVersions, listVersions, getVersionYAML, deleteVersion, deleteSession } from '../services/api';
import YAMLViewer from './YAMLViewer';
import VersionComparison from './VersionComparison';

export default function Dashboard() {
  const [activeView, setActiveView] = useState('overview'); // 'overview' or 'session-detail'
  const [sessions, setSessions] = useState([]);
  const [allVersions, setAllVersions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionVersions, setSessionVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  // YAML Viewer state
  const [yamlViewerOpen, setYamlViewerOpen] = useState(false);
  const [yamlContent, setYamlContent] = useState('');
  const [yamlTitle, setYamlTitle] = useState('');
  
  // Comparison state
  const [comparisonOpen, setComparisonOpen] = useState(false);
  const [compareSession1, setCompareSession1] = useState(null);
  const [compareVersion1, setCompareVersion1] = useState(null);
  const [compareSession2, setCompareSession2] = useState(null);
  const [compareVersion2, setCompareVersion2] = useState(null);
  const [selectedForComparison, setSelectedForComparison] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [sessionsData, versionsData] = await Promise.all([
        getAllSessions(),
        getAllVersions()
      ]);
      setSessions(sessionsData.sessions);
      setAllVersions(versionsData.versions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSessionClick = async (session) => {
    setSelectedSession(session);
    setActiveView('session-detail');
    try {
      const versions = await listVersions(session.session_id);
      setSessionVersions(versions);
    } catch (err) {
      console.error('Failed to load session versions:', err);
    }
  };

  const handleViewYAML = async (sessionId, version, domainName) => {
    try {
      const data = await getVersionYAML(sessionId, version);
      setYamlContent(data.yaml_content);
      setYamlTitle(`${domainName} - Version ${version}`);
      setYamlViewerOpen(true);
    } catch (err) {
      console.error('Failed to load YAML:', err);
    }
  };

  const handleSelectForComparison = (sessionId, version) => {
    const selection = { sessionId, version };
    
    if (selectedForComparison.length === 0) {
      setSelectedForComparison([selection]);
    } else if (selectedForComparison.length === 1) {
      setSelectedForComparison([...selectedForComparison, selection]);
      // Auto-open comparison
      setCompareSession1(selectedForComparison[0].sessionId);
      setCompareVersion1(selectedForComparison[0].version);
      setCompareSession2(selection.sessionId);
      setCompareVersion2(selection.version);
      setComparisonOpen(true);
      setSelectedForComparison([]);
    } else {
      setSelectedForComparison([selection]);
    }
  };

  const isSelectedForComparison = (sessionId, version) => {
    return selectedForComparison.some(
      s => s.sessionId === sessionId && s.version === version
    );
  };

  const filteredSessions = sessions.filter(session =>
    session.domain_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 max-w-md">
          <h3 className="text-red-200 font-semibold text-lg mb-2">Error Loading Dashboard</h3>
          <p className="text-red-300 text-sm">{error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-900">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <svg className="w-8 h-8 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Version Dashboard
            </h1>
            <p className="text-slate-400 mt-1">
              Manage and compare domain pack versions across all sessions
            </p>
          </div>
          {activeView === 'session-detail' && (
            <button
              onClick={() => setActiveView('overview')}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Overview
            </button>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-700/50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Sessions</p>
                <p className="text-3xl font-bold text-white mt-1">{sessions.length}</p>
              </div>
              <div className="w-12 h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
            </div>
          </div>
          <div className="bg-slate-700/50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Versions</p>
                <p className="text-3xl font-bold text-white mt-1">{allVersions.length}</p>
              </div>
              <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
              </div>
            </div>
          </div>
          <div className="bg-slate-700/50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Avg Versions/Session</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {sessions.length > 0 ? (allVersions.length / sessions.length).toFixed(1) : 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeView === 'overview' ? (
          <>
            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search by domain name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-800 text-white px-4 py-3 pl-12 rounded-lg border border-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                />
                <svg className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            {/* Sessions Grid */}
            {filteredSessions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredSessions.map((session) => (
                  <div
                    key={session.session_id}
                    onClick={() => handleSessionClick(session)}
                    className="bg-slate-800 rounded-lg p-5 border border-slate-700 hover:border-indigo-500 transition-all cursor-pointer group hover:shadow-lg hover:shadow-indigo-500/10 relative"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-white truncate group-hover:text-indigo-400 transition-colors pr-2">
                          {session.domain_name}
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">
                          {session.session_id.substring(0, 8)}...
                        </p>
                      </div>

                      {/* Managed Action Area (Icon or Delete Button) */}
                      <div className="relative w-10 h-10 flex-shrink-0">
                        {/* Indicator Icon (Hidden on hover) */}
                        <div className="absolute inset-0 bg-indigo-500/20 rounded-lg flex items-center justify-center group-hover:opacity-0 transition-opacity duration-200">
                          <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        
                        {/* Delete Button (Visible on hover) */}
                        <button
                          onClick={async (e) => {
                            e.stopPropagation();
                            if (window.confirm(`Delete entire session for "${session.domain_name}" and all its versions?`)) {
                              try {
                                await deleteSession(session.session_id);
                                loadDashboardData();
                              } catch (err) {
                                alert("Failed to delete session: " + err.message);
                              }
                            }
                          }}
                          className="absolute inset-0 flex items-center justify-center bg-red-600 hover:bg-red-500 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 shadow-lg"
                          title="Delete Session"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm mb-3">
                      <div className="flex items-center gap-1.5 text-slate-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                        </svg>
                        <span>v{session.current_version}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>{session.total_versions} versions</span>
                      </div>
                    </div>
                    
                    <div className="pt-3 border-t border-slate-700">
                      <p className="text-xs text-slate-500">
                        Updated {formatDate(session.updated_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p className="text-slate-400 text-lg">No sessions found</p>
                <p className="text-slate-500 text-sm mt-1">
                  {searchTerm ? 'Try a different search term' : 'Create a new chat to get started'}
                </p>
              </div>
            )}
          </>
        ) : (
          /* Session Detail View */
          selectedSession && (
            <div>
              <div className="bg-slate-800 rounded-lg p-6 mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">{selectedSession.domain_name}</h2>
                <div className="flex items-center gap-6 text-sm text-slate-400">
                  <span>Session ID: {selectedSession.session_id}</span>
                  <span>•</span>
                  <span>Current Version: {selectedSession.current_version}</span>
                  <span>•</span>
                  <span>Total Versions: {selectedSession.total_versions}</span>
                </div>
              </div>

              {/* Version Timeline */}
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Version History</h3>
                  {selectedForComparison.length > 0 && (
                    <div className="text-sm text-indigo-400">
                      {selectedForComparison.length} selected for comparison
                    </div>
                  )}
                </div>
                
                {sessionVersions.map((version, index) => (
                  <div
                    key={version.version}
                    className={`bg-slate-800 rounded-lg p-4 border transition-all ${
                      isSelectedForComparison(selectedSession.session_id, version.version)
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : 'border-slate-700 hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="px-3 py-1 bg-indigo-500/20 text-indigo-300 text-sm font-semibold rounded-full">
                            Version {version.version}
                          </span>
                          {index === 0 && (
                            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 text-xs font-semibold rounded-full">
                              LATEST
                            </span>
                          )}
                        </div>
                        <p className="text-slate-300 text-sm mb-2">{version.reason}</p>
                        <p className="text-slate-500 text-xs">{formatDate(version.created_at)}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleViewYAML(selectedSession.session_id, version.version, selectedSession.domain_name)}
                          className="px-3 py-1.5 bg-slate-700 hover:bg-indigo-600 text-white text-sm rounded-lg transition-colors"
                          title="View YAML"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleSelectForComparison(selectedSession.session_id, version.version)}
                          className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                            isSelectedForComparison(selectedSession.session_id, version.version)
                              ? 'bg-indigo-600 text-white'
                              : 'bg-slate-700 hover:bg-slate-600 text-white'
                          }`}
                          title="Select for comparison"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                        </button>
                        
                        {/* Delete Version Button */}
                        <button
                          onClick={async () => {
                            if (version.version === selectedSession.current_version) {
                              alert("Cannot delete the current active version");
                              return;
                            }
                            if (window.confirm(`Delete version ${version.version}? This cannot be undone.`)) {
                              try {
                                await deleteVersion(selectedSession.session_id, version.version);
                                // Refresh current view
                                handleSessionClick(selectedSession);
                                loadDashboardData();
                              } catch (err) {
                                alert("Failed to delete version: " + err.message);
                              }
                            }
                          }}
                          disabled={version.version === selectedSession.current_version}
                          className="px-3 py-1.5 bg-slate-700 hover:bg-red-600 text-white text-sm rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                          title="Delete Version"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        )}
      </div>

      {/* Modals */}
      {yamlViewerOpen && (
        <YAMLViewer
          yamlContent={yamlContent}
          title={yamlTitle}
          onClose={() => setYamlViewerOpen(false)}
        />
      )}

      {comparisonOpen && (
        <VersionComparison
          session1={compareSession1}
          version1={compareVersion1}
          session2={compareSession2}
          version2={compareVersion2}
          onClose={() => setComparisonOpen(false)}
        />
      )}
    </div>
  );
}
