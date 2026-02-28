import React, { useState, useEffect, useCallback } from 'react';
import { listChatSessions, deleteChatSession, getNodeCallLogs } from '../services/api';
import Header from '../components/common/Header';

// Node badge color mapping
const NODE_COLORS = {
  classify_intent:        'bg-blue-100 text-blue-700 border-blue-200',
  generate_patch:         'bg-purple-100 text-purple-700 border-purple-200',
  generate_response_info: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  generate_response_error:'bg-red-100 text-red-700 border-red-200',
  general_knowledge:      'bg-amber-100 text-amber-700 border-amber-200',
};
const NODE_DEFAULT_COLOR = 'bg-slate-100 text-slate-700 border-slate-200';

const NODE_LABELS = {
  classify_intent:        'Classify Intent',
  generate_patch:         'Generate Patch',
  generate_response_info: 'Info Response',
  generate_response_error:'Error Response',
  general_knowledge:      'General Knowledge',
};

function NodeBadge({ name }) {
  const color = NODE_COLORS[name] || NODE_DEFAULT_COLOR;
  const label = NODE_LABELS[name] || name.replace(/_/g, ' ');
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${color}`}>
      {label}
    </span>
  );
}

function TokenBar({ value, max, color }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="flex items-center gap-2 min-w-0">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-slate-600 w-12 text-right shrink-0">{value.toLocaleString()}</span>
    </div>
  );
}

function NodeCallsPanel({ sessionId }) {
  const [logs, setLogs] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getNodeCallLogs(sessionId).then(data => {
      if (!cancelled) { setLogs(data); setLoading(false); }
    });
    return () => { cancelled = true; };
  }, [sessionId]);

  if (loading) return (
    <div className="flex items-center justify-center py-6 text-slate-400 text-sm gap-2">
      <svg className="w-4 h-4 animate-spin text-indigo-400" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      Loading node logs…
    </div>
  );

  if (!logs || logs.length === 0) return (
    <div className="text-center py-6 text-slate-400 text-sm">No node calls recorded for this session yet.</div>
  );

  // Group by turn
  const turns = logs.reduce((acc, log) => {
    const t = log.turn;
    if (!acc[t]) acc[t] = [];
    acc[t].push(log);
    return acc;
  }, {});

  const maxTokens = Math.max(...logs.map(l => Math.max(l.input_tokens, l.output_tokens)), 1);

  return (
    <div className="divide-y divide-slate-100">
      {Object.entries(turns).map(([turn, entries]) => {
        const turnIn  = entries.reduce((s, e) => s + e.input_tokens, 0);
        const turnOut = entries.reduce((s, e) => s + e.output_tokens, 0);
        const turnMs  = entries.reduce((s, e) => s + e.response_time_ms, 0);
        return (
          <div key={turn} className="px-6 py-3">
            {/* Turn header */}
            <div className="flex items-center gap-3 mb-2">
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Turn {parseInt(turn) + 1}</span>
              <div className="flex-1 border-t border-dashed border-slate-200" />
              <span className="text-[11px] text-slate-400">{turnIn + turnOut} tok · {Math.round(turnMs)} ms total</span>
            </div>

            {/* Node rows */}
            <div className="space-y-1.5">
              {entries.map((log) => (
                <div key={log.id} className="grid grid-cols-[180px_1fr_1fr_90px_120px] gap-3 items-center text-xs py-1.5 px-3 rounded-lg bg-slate-50 border border-slate-100 hover:border-indigo-100 hover:bg-indigo-50/30 transition-colors">
                  {/* Node badge */}
                  <div className="flex items-center gap-1.5">
                    <NodeBadge name={log.node_name} />
                  </div>

                  {/* Input tokens bar */}
                  <div>
                    <div className="text-[10px] text-slate-400 mb-0.5">Input</div>
                    <TokenBar value={log.input_tokens} max={maxTokens} color="bg-emerald-400" />
                  </div>

                  {/* Output tokens bar */}
                  <div>
                    <div className="text-[10px] text-slate-400 mb-0.5">Output</div>
                    <TokenBar value={log.output_tokens} max={maxTokens} color="bg-amber-400" />
                  </div>

                  {/* Response time */}
                  <div className="text-center">
                    <div className="text-[10px] text-slate-400 mb-0.5">Time</div>
                    <span className={`font-mono font-semibold text-xs ${log.response_time_ms > 3000 ? 'text-red-500' : log.response_time_ms > 1500 ? 'text-amber-500' : 'text-emerald-600'}`}>
                      {Math.round(log.response_time_ms)} ms
                    </span>
                  </div>

                  {/* Intent (for classify_intent node) */}
                  <div className="text-center">
                    {log.intent ? (
                      <span className="text-[10px] font-mono bg-indigo-50 text-indigo-600 px-1.5 py-0.5 rounded border border-indigo-100 truncate block max-w-full" title={log.intent}>
                        {log.intent}
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-300">—</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function Monitoring({ sidebarOpen, toggleSidebar }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => { fetchSessions(); }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data = await listChatSessions();
      setSessions(data);
      setError(null);
    } catch (err) {
      setError('Failed to load chat sessions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) return;
    try {
      await deleteChatSession(sessionId);
      if (expandedId === sessionId) setExpandedId(null);
      await fetchSessions();
    } catch (err) {
      alert('Failed to delete the session: ' + err.message);
    }
  };

  const toggleExpand = (id) => setExpandedId(prev => prev === id ? null : id);

  const formatDate = (d) => new Date(d).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Header
        title="Monitoring"
        subtitle="LLM call details per session and graph node"
        showSidebarToggle={true}
        toggleSidebar={toggleSidebar}
        rightActions={
          <button
            onClick={fetchSessions}
            className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 hover:border-slate-300 shadow-sm transition-all font-bold text-[11px] uppercase tracking-wider flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
        }
      />

      <div className="flex-1 overflow-auto p-6 md:p-8">
        <div className="max-w-6xl mx-auto space-y-6">

          {/* Legend */}
          <div className="flex flex-wrap gap-2 items-center text-xs text-slate-500">
            <span className="font-semibold mr-1">Node types:</span>
            {Object.entries(NODE_LABELS).map(([key, label]) => (
              <NodeBadge key={key} name={key} />
            ))}
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
              <div className="flex items-center text-red-700">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            </div>
          )}

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            {loading ? (
              <div className="flex flex-col items-center justify-center p-12 space-y-4 text-slate-400">
                <svg className="w-8 h-8 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <p>Loading sessions…</p>
              </div>
            ) : sessions.length === 0 ? (
              <div className="flex flex-col items-center justify-center p-16 text-center">
                <div className="w-16 h-16 bg-slate-50 text-slate-300 rounded-2xl flex items-center justify-center mb-4">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-slate-800">No sessions found</h3>
                <p className="text-slate-500 mt-2 max-w-sm">No chat sessions available to monitor yet.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {sessions.map((session) => {
                  const isOpen = expandedId === session.id;
                  return (
                    <div key={session.id}>
                      {/* Session row */}
                      <div className="grid grid-cols-[1fr_auto_auto_auto_auto_auto] gap-4 px-6 py-4 items-center hover:bg-slate-50/60 transition-colors group">

                        {/* Session info */}
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="w-9 h-9 flex items-center justify-center rounded-lg bg-indigo-50 text-indigo-500 shrink-0">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                          </div>
                          <div className="min-w-0">
                            <div className="text-sm font-semibold text-slate-800 truncate">
                              {session.session_metadata?.title || 'Chat Session'}
                            </div>
                            <div className="text-[11px] text-slate-400 font-mono truncate">{session.id}</div>
                          </div>
                        </div>

                        {/* Calls */}
                        <div className="text-center">
                          <div className="text-[10px] text-slate-400 mb-0.5 uppercase tracking-wide">Calls</div>
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">{session.total_llm_calls}</span>
                        </div>

                        {/* Input tokens */}
                        <div className="text-center">
                          <div className="text-[10px] text-slate-400 mb-0.5 uppercase tracking-wide">Input</div>
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700">{session.total_input_tokens.toLocaleString()}</span>
                        </div>

                        {/* Output tokens */}
                        <div className="text-center">
                          <div className="text-[10px] text-slate-400 mb-0.5 uppercase tracking-wide">Output</div>
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700">{session.total_output_tokens.toLocaleString()}</span>
                        </div>

                        {/* Last activity */}
                        <div className="text-center">
                          <div className="text-[10px] text-slate-400 mb-0.5 uppercase tracking-wide">Last Active</div>
                          <span className="text-xs text-slate-500">{formatDate(session.last_activity_at)}</span>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-1">
                          {/* Expand / collapse details button */}
                          <button
                            onClick={() => toggleExpand(session.id)}
                            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-semibold transition-all border
                              ${isOpen
                                ? 'bg-indigo-50 text-indigo-600 border-indigo-200 hover:bg-indigo-100'
                                : 'bg-white text-slate-500 border-slate-200 hover:text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50'}`}
                            title={isOpen ? 'Hide node calls' : 'Show node calls'}
                          >
                            <svg className={`w-3.5 h-3.5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                            {isOpen ? 'Hide' : 'Details'}
                          </button>

                          {/* Delete button */}
                          <button
                            onClick={() => handleDelete(session.id)}
                            className="p-1.5 text-slate-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                            title="Delete Session"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>

                      {/* Expandable node call detail panel */}
                      {isOpen && (
                        <div className="bg-slate-50/70 border-t border-slate-100">
                          {/* Column headers */}
                          <div className="grid grid-cols-[180px_1fr_1fr_90px_120px] gap-3 px-9 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                            <span>Node</span>
                            <span>Input Tokens</span>
                            <span>Output Tokens</span>
                            <span className="text-center">Time</span>
                            <span className="text-center">Intent</span>
                          </div>
                          <NodeCallsPanel sessionId={session.id} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
