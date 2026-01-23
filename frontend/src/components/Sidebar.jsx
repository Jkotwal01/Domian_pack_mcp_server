import React, { useState } from 'react';

export default function Sidebar({ 
  isOpen, 
  toggleSidebar, 
  sessions = [], 
  activeSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onRenameSession
}) {
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleRename = (sessionId) => {
    if (editTitle.trim()) {
      onRenameSession(sessionId, editTitle);
    }
    setEditingSessionId(null);
    setEditTitle('');
  };

  const startEditing = (session) => {
    setEditingSessionId(session.id);
    setEditTitle(session.title);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      className={`
                fixed inset-y-0 left-0 z-20 w-72 bg-slate-800 text-slate-100 transform transition-transform duration-300 ease-in-out
                ${isOpen ? "translate-x-0" : "-translate-x-full"}
                md:relative md:translate-x-0 md:w-64 lg:w-72
                flex flex-col border-r border-slate-700
            `}
    >
      {/* Header */}
      <div className="p-4 flex items-center justify-between border-b border-slate-700/50">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center text-white font-bold shadow-lg">
            C
          </div>
          <span className="font-semibold text-lg tracking-tight">
            Domain Pack Generator
          </span>
        </div>
        {/* Mobile close */}
        <button
          onClick={toggleSidebar}
          className="md:hidden p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-white"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* New Chat Action */}
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full bg-slate-700 hover:bg-indigo-600 text-white py-3 px-4 rounded-xl flex items-center justify-start space-x-3 transition-all duration-200 shadow-sm hover:shadow-md group"
        >
          <span className="p-1 bg-slate-600 group-hover:bg-indigo-500 rounded-full transition-colors">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          </span>
          <span className="font-medium">New chat</span>
        </button>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2 scrollbar-thin scrollbar-thumb-slate-700">
        {sessions.length > 0 ? (
          <>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 ml-2">
              Recent
            </h3>
            <ul className="space-y-1">
              {sessions.map((session) => (
                <li
                  key={session.id}
                  className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-colors ${
                    session.id === activeSessionId
                      ? 'bg-slate-700 text-slate-100'
                      : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-100'
                  }`}
                  onClick={() => onSelectSession(session.id)}
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <svg
                      className="w-4 h-4 flex-shrink-0 text-slate-500 group-hover:text-slate-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                      />
                    </svg>
                    
                    {editingSessionId === session.id ? (
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onBlur={() => handleRename(session.id)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleRename(session.id);
                          if (e.key === 'Escape') {
                            setEditingSessionId(null);
                            setEditTitle('');
                          }
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className="flex-1 bg-slate-600 text-white text-sm px-2 py-1 rounded outline-none focus:ring-2 focus:ring-indigo-500"
                        autoFocus
                      />
                    ) : (
                      <div className="flex-1 min-w-0">
                        <span className="text-sm truncate block">{session.title}</span>
                        <span className="text-xs text-slate-500">{formatDate(session.updatedAt)}</span>
                      </div>
                    )}
                  </div>

                  {/* Action buttons */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        startEditing(session);
                      }}
                      className="p-1 hover:bg-slate-600 rounded"
                      title="Rename"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                      </svg>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (window.confirm('Delete this chat?')) {
                          onDeleteSession(session.id);
                        }
                      }}
                      className="p-1 hover:bg-red-600 rounded"
                      title="Delete"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <div className="text-center text-slate-500 text-sm py-8">
            No chat sessions yet.<br />Start a new chat!
          </div>
        )}
      </div>

      {/* User Profile */}
      <div className="p-4 border-t border-slate-700 bg-slate-800/50">
        <div className="flex items-center space-x-3 cursor-pointer hover:bg-slate-700 p-2 rounded-lg transition-colors">
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-medium text-sm shadow-sm">
            JD
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-slate-200">John Doe</span>
            <span className="text-xs text-slate-400">Pro Plan</span>
          </div>
        </div>
      </div>
    </div>
  );
}
