import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/**
 * Common header component for all pages
 * Includes sidebar toggle, back button, title, and logout button
 */
export default function Header({ 
  title = 'Domain Pack Generator',
  subtitle,
  showBackButton = false,
  onBack,
  showSidebarToggle = true,
  toggleSidebar,
  rightActions
}) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="bg-white border-b border-slate-100 shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Sidebar Toggle - Always visible to prevent layout shifts */}
          {showSidebarToggle && toggleSidebar ? (
            <button
              onClick={toggleSidebar}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              title="Toggle Sidebar"
            >
              <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          ) : (
            <div className="w-9 h-9"></div>
          )}
          
          {/* Back Button */}
          {showBackButton && onBack && (
            <button
              onClick={onBack}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              title="Back"
            >
              <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          )}
          
          {/* Title */}
          <div>
            <h1 className="text-2xl font-black text-slate-900">{title}</h1>
            {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
          </div>
        </div>
        
        {/* Right Actions */}
        <div className="flex items-center space-x-3">
          {/* Custom right actions */}
          {rightActions}
          
          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-50 text-red-600 font-bold rounded-xl hover:bg-red-100 border border-red-200 transition-all flex items-center space-x-2"
            title="Logout"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </div>
  );
}
