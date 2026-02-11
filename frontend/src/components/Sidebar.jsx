import React from "react";
import { useAuth } from "../context/AuthContext";

export default function Sidebar({
  isOpen,
  toggleSidebar,
  activeView,
  onShowDashboard,
  onShowChat,
}) {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    if (confirm("Are you sure you want to log out?")) {
      logout();
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-20 md:hidden backdrop-blur-sm transition-opacity"
          onClick={toggleSidebar}
        />
      )}

      <div
        className={`
            fixed inset-y-0 left-0 z-30 bg-white border-r border-slate-200 transition-all duration-300 ease-in-out
            md:relative flex flex-col
            ${isOpen ? "w-[260px] translate-x-0" : "w-[260px] md:w-[0px] -translate-x-full md:translate-x-0 overflow-hidden"}
        `}
      >
        <div className="flex flex-col h-full overflow-hidden w-full">
          {/* Brand/Header */}
          <div className="p-6 flex items-center justify-between">
            <h1 className="text-xl font-bold text-slate-900 leading-tight">
              Data Discovery<br />Platform
            </h1>
            <button 
              onClick={toggleSidebar}
              className="p-2 rounded-lg hover:bg-slate-50 text-slate-400 hover:text-slate-600 transition-all border border-transparent hover:border-slate-100"
              title="Close Sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7M20 12H4" />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 space-y-1">
            <button
              onClick={onShowDashboard}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                activeView === 'dashboard' 
                  ? 'bg-slate-50 text-indigo-600 font-medium' 
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span>Overview</span>
            </button>

            {/* Chatbot button removed */}
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-slate-100">
            <div 
              className="flex items-center space-x-3 p-2 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer group"
              onClick={handleLogout}
              title="Click to logout"
            >
              <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center border border-slate-300 overflow-hidden">
                <svg className="w-6 h-6 text-slate-500" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900 truncate">
                  {user?.email?.split('@')[0] || "User"}
                </p>
                <p className="text-xs text-slate-500 truncate">{user?.email || "No email"}</p>
              </div>
              <svg className="w-4 h-4 text-slate-400 group-hover:text-red-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
