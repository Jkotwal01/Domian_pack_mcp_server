import React, { useState, useEffect } from 'react';
import { listDomainPacks, createDomainPack } from '../services/api';

export default function Dashboard({ onSelectDomain, onCreateDomain, sidebarOpen, toggleSidebar }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState(null);
  const [showMetadataForm, setShowMetadataForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    version: '1.0.0'
  });

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await listDomainPacks();
      setSessions(data);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    } finally {
      setLoading(false);
    }
  };

  const domainIcons = {
    Automotive: "🚗",
    Manufacturing: "🏭",
    Healthcare: "🏥",
    Legal: "⚖️",
    SaaS: "💻",
  };

  const handleSaveMetadata = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const newDomain = await createDomainPack(formData.name, formData.description);
      onCreateDomain({
        id: newDomain.id,
        name: newDomain.name,
        description: formData.description,
        version: formData.version,
        isTemplate: true
      });
      setShowMetadataForm(false);
    } catch (err) {
      alert("Failed to create domain: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white overflow-y-auto">
      {/* Selection Header */}
      <div className="px-8 py-4 flex items-center justify-between border-b border-slate-100">
        <div className="flex items-center space-x-4">
          {!sidebarOpen && (
            <button 
              onClick={toggleSidebar}
              className="p-2 rounded-xl hover:bg-slate-50 text-slate-500 transition-all border border-transparent hover:border-slate-100"
              title="Open Sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}
          <h1 className="text-xl font-bold text-slate-800">Select Your Domain</h1>
        </div>
        <div className="text-sm font-medium text-slate-400">Step 1 of 2</div>
      </div>

      <div className="p-12 max-w-7xl mx-auto w-full space-y-20">
        
        {/* Section 1: Create New */}
        <section className="space-y-12">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center text-3xl mx-auto shadow-sm border border-blue-100">
              ⚡
            </div>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Choose Your Base Template</h2>
            <p className="text-slate-500 max-w-2xl mx-auto leading-relaxed">
              Start fresh with our universal base template that includes all essential keys for any domain pack.
            </p>
          </div>

          <div className="flex justify-center">
            <button 
              onClick={() => setShowMetadataForm(true)}
              className="group relative bg-white border-2 border-blue-500 rounded-[2.5rem] p-10 hover:shadow-2xl hover:shadow-blue-100 transition-all duration-300 max-w-md w-full text-center space-y-6"
            >
              <div className="w-20 h-20 bg-blue-600 text-white rounded-[1.5rem] flex items-center justify-center text-4xl mx-auto shadow-lg group-hover:scale-110 transition-transform">
                🏗️
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-black text-slate-900">Standard Base Template</h3>
                <p className="text-slate-500 font-medium tracking-tight">Includes universal entities, relations, and patterns</p>
              </div>
              <div className="flex items-center justify-center space-x-2 text-blue-600 font-bold">
                <span>Select & Configure</span>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </div>
            </button>
          </div>
        </section>

        {/* Section 2: Existing Packs */}
        <section className="space-y-12 pb-20">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Existing Domain Packs</h2>
            <p className="text-slate-500 max-w-2xl mx-auto leading-relaxed">
              Continue refining your previously generated and saved domain configurations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {sessions.map((session) => (
              <div 
                key={session.id}
                className={`relative bg-white rounded-[2rem] border-2 p-8 transition-all duration-300 cursor-pointer group ${
                  selectedSession?.id === session.id 
                    ? 'border-blue-500 ring-4 ring-blue-50 shadow-xl scale-[1.02]' 
                    : 'border-slate-100 hover:border-blue-200 hover:shadow-lg'
                }`}
                onClick={() => setSelectedSession(session)}
              >
                {/* Radio Circle */}
                <div className={`absolute top-6 right-6 w-7 h-7 rounded-full border-2 flex items-center justify-center transition-colors ${
                  selectedSession?.id === session.id ? 'border-blue-500 bg-blue-500' : 'border-slate-200 bg-white'
                }`}>
                  {selectedSession?.id === session.id && (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>

                {/* Icon & Title */}
                <div className="flex items-center space-x-6 mb-8">
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-3xl shadow-sm border ${
                    selectedSession?.id === session.id ? 'bg-white border-blue-100' : 'bg-slate-50 border-slate-100'
                  }`}>
                    {domainIcons[session.name] || "📦"}
                  </div>
                  <div>
                    <h3 className="text-xl font-extrabold text-slate-900">{session.name}</h3>
                    <p className="text-sm text-slate-500 font-medium">
                      Version: {session.version}
                    </p>
                  </div>
                </div>

                <div className="space-y-4 mt-8">
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Configuration Overview</h4>
                  <div className="flex flex-wrap gap-2">
                    {['6 Entities', '6 Relations', '2 Patterns'].map(tag => (
                      <span key={tag} className="px-3 py-1 bg-slate-50 text-slate-600 text-[10px] font-bold rounded-lg border border-slate-100">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {selectedSession && (
            <div className="flex justify-center pt-8">
              <button 
                onClick={() => onSelectDomain(selectedSession)}
                className="px-12 py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 shadow-xl shadow-blue-200 transition-all flex items-center space-x-3 group"
              >
                <span>Continue Enhancing Existing</span>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          )}
        </section>
      </div>

      {/* Metadata Form Modal */}
      {showMetadataForm && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="bg-white rounded-[2.5rem] w-full max-w-lg shadow-2xl animate-fadeIn overflow-hidden">
            <header className="px-10 py-8 border-b border-slate-50 bg-slate-50/50">
              <h3 className="text-2xl font-black text-slate-900">New Domain Setup</h3>
              <p className="text-slate-500 font-medium">Define your new domain pack metadata</p>
            </header>
            <form onSubmit={handleSaveMetadata} className="p-10 space-y-8">
              <div className="space-y-3">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest pl-1">Domain Name</label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g. Retail Supply Chain"
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all font-medium text-slate-900"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div className="space-y-3">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest pl-1">Description</label>
                <textarea 
                  rows="3"
                  placeholder="Describe what this domain pack should cover..."
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all font-medium text-slate-900 resize-none"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
              <div className="space-y-3">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest pl-1">Version</label>
                <input 
                  type="text" 
                  placeholder="1.0.0"
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all font-medium text-slate-900"
                  value={formData.version}
                  onChange={(e) => setFormData({...formData, version: e.target.value})}
                />
              </div>
              <div className="flex items-center space-x-4 pt-4">
                <button 
                  type="button"
                  onClick={() => setShowMetadataForm(false)}
                  className="flex-1 py-4 bg-slate-100 text-slate-600 font-bold rounded-2xl hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="flex-[2] py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all"
                >
                  Save & Configure
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto px-8 py-4 border-t border-slate-50 flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
        <p>Data Discovery Platform</p>
        <div className="flex items-center space-x-6">
          <p>v1.9.9</p>
          <div className="flex items-center space-x-2 text-emerald-500">
            <span className="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
            <span>Live System</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
