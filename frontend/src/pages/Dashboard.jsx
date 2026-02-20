import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listDomains, createDomain, deleteDomain } from '../services/api';
import { mockDomainPacks, createMockDomain } from '../utils/mockData';
import Header from '../components/common/Header';

// Set to true to use mock data instead of API calls
const USE_MOCK_DATA = false;

export default function Dashboard({ sidebarOpen, toggleSidebar }) {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false); // New state for creation loader
  const [selectedSession, setSelectedSession] = useState(null);
  const [showMetadataForm, setShowMetadataForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    version: '1.0.0',
    pdfFile: null
  });
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      if (USE_MOCK_DATA) {
        // Use mock data for UI testing
        setSessions(mockDomainPacks);
      } else {
        const data = await listDomains();
        setSessions(data);
      }
    } catch (err) {
      console.error("Failed to load sessions:", err);
      // Fallback to mock data if API fails
      setSessions(mockDomainPacks);
    } finally {
      setLoading(false);
    }
  };

  const domainIcons = {
    Automotive: "🚗",
    Manufacturing: "🏭",
    Healthcare: "🏥",
    Healhcare: "🏥",
    Legal: "⚖️",
    SaaS: "💻",
  };

  const handleSaveMetadata = async (e) => {
    e.preventDefault();
    try {
      setIsCreating(true);
      if (USE_MOCK_DATA) {
        // Create mock domain for UI testing
        const newDomain = createMockDomain(formData.name, formData.description, formData.version);
        navigate(`/configview/${newDomain.id}`);
      } else {
        const newDomain = await createDomain(
          formData.name, 
          formData.description, 
          formData.version,
          formData.pdfFile
        );
        navigate(`/configview/${newDomain.id}`);
      }
      setShowMetadataForm(false);
    } catch (err) {
      alert("Failed to create domain: " + (err.message || err.toString() || 'Unknown error'));
    } finally {
      setIsCreating(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        setFormData({ ...formData, pdfFile: file });
      } else {
        alert("Please upload a PDF file.");
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return "0 Bytes";
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDeleteDomain = async (e, domainId) => {
    e.stopPropagation(); // Prevent selecting the card
    if (!window.confirm("Are you sure you want to delete this domain pack? This action cannot be undone.")) {
      return;
    }

    try {
      setLoading(true);
      await deleteDomain(domainId);
      setSessions(prev => prev.filter(s => s.id !== domainId));
      if (selectedSession?.id === domainId) {
        setSelectedSession(null);
      }
    } catch (err) {
      alert("Failed to delete domain: " + (err.message || err.toString() || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  if (isCreating || (loading && !showMetadataForm && sessions.length > 0)) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50/50 backdrop-blur-sm fixed inset-0 z-[60]">
        <div className="text-center space-y-6 animate-fadeIn">
          <div className="relative">
            <div className="w-24 h-24 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto shadow-xl shadow-blue-100"></div>
            <div className="absolute inset-0 flex items-center justify-center text-4xl animate-bounce">🤖</div>
          </div>
          <div className="space-y-3">
            <h3 className="text-2xl font-black text-slate-900 tracking-tight">Generating Domain Intelligence</h3>
            <p className="text-slate-500 font-semibold max-w-xs mx-auto leading-relaxed">
              Our AI is crafting a specialized domain structure for <span className="text-blue-600">"{formData.name}"</span>...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (loading && sessions.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <Header
        title="Domain Pack Generator"
        subtitle="Select or create your domain pack"
        showBackButton={false}
        showSidebarToggle={true}
        toggleSidebar={toggleSidebar}
      />

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
              onClick={() => {
                setFormData({ name: '', description: '', version: '1.0.0', pdfFile: null });
                setShowMetadataForm(true);
              }}
              className="group relative bg-white border-2 border-blue-500 rounded-[2.5rem] p-8 hover:shadow-2xl hover:shadow-blue-100 transition-all duration-300 aspect-square w-full max-w-[360px] flex flex-col items-center justify-center text-center space-y-6"
            >
              <div className="w-20 h-20 bg-blue-50 rounded-3xl flex items-center justify-center text-5xl group-hover:scale-110 transition-transform duration-500">
                🏗️
              </div>
              <div className="space-y-3">
                <h3 className="text-2xl font-black text-slate-900 tracking-tight">Standard Base Template</h3>
                <p className="text-slate-500 font-semibold leading-relaxed px-4">
                  Start with universal entities, relationships, and extraction patterns.
                </p>
              </div>
              <div className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg shadow-blue-200 group-hover:bg-blue-700 transition-all">
                Select & Configure
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
            {sessions.map((session) => {
              const isActive = selectedSession?.id === session.id;
              const icon = domainIcons[session.name] || domainIcons[session.name?.replace('Healthare', 'Healthcare')] || "📦";
              
              return (
                <div 
                  key={session.id}
                  className={`relative bg-white rounded-[2.5rem] border-2 p-8 transition-all duration-300 cursor-pointer group shadow-sm ${
                    isActive 
                      ? 'border-blue-500 ring-4 ring-blue-50 shadow-xl scale-[1.02]' 
                      : 'border-slate-200 hover:border-blue-400 hover:shadow-lg'
                  }`}
                  onClick={() => setSelectedSession(session)}
                >
                  {/* Radio Circle & Delete */}
                  <div className="absolute top-6 right-6 flex items-center space-x-2">
                    <button
                      onClick={(e) => handleDeleteDomain(e, session.id)}
                      className="w-10 h-10 rounded-full bg-red-50 text-red-500 border border-red-100 flex items-center justify-center hover:bg-red-500 hover:text-white transition-all duration-200"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                    <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center transition-colors ${
                      isActive ? 'border-blue-500 bg-blue-500' : 'border-slate-200 bg-white'
                    }`}>
                      {isActive && (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>

                  {/* Icon & Title */}
                  <div className="flex flex-col items-center text-center space-y-4 mb-6">
                    <div className={`w-20 h-20 rounded-2xl flex items-center justify-center text-4xl shadow-sm border ${
                      isActive ? 'bg-white border-blue-100 text-blue-600' : 'bg-slate-50 border-slate-200 text-slate-400'
                    }`}>
                      {icon}
                    </div>
                    <div className="space-y-1">
                      <h3 className="text-xl font-black text-slate-900 tracking-tight leading-none px-2">{session.name}</h3>
                      <p className="text-[10px] text-blue-600 font-black bg-blue-50 px-3 py-1 rounded-full inline-block uppercase tracking-wider">
                        v{session.version || "N/A"}
                      </p>
                    </div>
                  </div>

                  {/* Description */}
                  <div className="mb-8 min-h-[3rem]">
                    <p className="text-sm text-slate-500 font-medium leading-relaxed text-center line-clamp-2 px-4">
                      {session.description || "No description provided"}
                    </p>
                  </div>

                  {/* Configuration Overview */}
                  <div className="space-y-4 pt-4 border-t border-slate-50">
                    <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] text-center">Configuration Overview</h4>
                    <div className="flex flex-wrap gap-2 justify-center">
                      <span className="px-3 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold rounded-lg border border-blue-100 shadow-sm">
                        {session.entity_count || 0} Entities
                      </span>
                      <span className="px-3 py-1 bg-purple-50 text-purple-600 text-[10px] font-bold rounded-lg border border-purple-100 shadow-sm">
                        {session.relationship_count || 0} Relationships
                      </span>
                      <span className="px-3 py-1 bg-amber-50 text-amber-600 text-[10px] font-bold rounded-lg border border-amber-100 shadow-sm">
                        {session.key_term_count || 0} Terms
                      </span>
                      <span className="px-3 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-bold rounded-lg border border-emerald-100 shadow-sm">
                        {session.extraction_pattern_count || 0} Patterns
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          {sessions.length === 0 && !loading && (
            <div className="text-center py-20 bg-slate-50/50 rounded-[3rem] border-2 border-dashed border-slate-200">
              <div className="text-4xl mb-4">📭</div>
              <h3 className="text-xl font-bold text-slate-900">No domain packs found</h3>
              <p className="text-slate-500">Create your first domain pack above to get started.</p>
            </div>
          )}

          {selectedSession && (
            <div className="flex justify-center pt-8">
              <button 
                onClick={() => navigate(`/configview/${selectedSession.id}`)}
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
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-white rounded-[3rem] w-full max-w-[850px] shadow-2xl animate-slideUp overflow-hidden flex flex-col">
            <header className="px-10 py-8 border-b border-slate-50 bg-white flex items-center justify-between">
              <div className="space-y-1">
                <h3 className="text-2xl font-black text-slate-900 tracking-tight">Configure Domain Intelligence</h3>
                <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">Initialize strategic knowledge parameters</p>
              </div>
              <button 
                onClick={() => setShowMetadataForm(false)}
                className="w-10 h-10 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center hover:bg-slate-200 hover:text-slate-600 transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </header>
            
            <form onSubmit={handleSaveMetadata} className="p-10 space-y-8">
              <div className="grid grid-cols-2 gap-6">
                {/* Name Card */}
                <div className="bg-slate-50 rounded-[2rem] p-6 border border-slate-100 hover:border-blue-200 hover:bg-white transition-all group shadow-sm">
                  <div className="flex items-center space-x-3 mb-3 text-blue-600">
                    <span className="text-xl">🏷️</span>
                    <label className="text-[10px] font-black uppercase tracking-[0.2em]">Domain Name</label>
                  </div>
                  <input 
                    type="text" 
                    required
                    placeholder="e.g. Retail Logistics"
                    className="w-full bg-transparent border-b border-slate-200 focus:border-blue-500 py-1 text-lg font-black text-slate-900 focus:outline-none transition-all placeholder:text-slate-300"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                  />
                </div>

                {/* Version Card */}
                <div className="bg-slate-50 rounded-[2rem] p-6 border border-slate-100 hover:border-purple-200 hover:bg-white transition-all group shadow-sm">
                  <div className="flex items-center space-x-3 mb-3 text-purple-600">
                    <span className="text-xl">🔢</span>
                    <label className="text-[10px] font-black uppercase tracking-[0.2em]">Version Control</label>
                  </div>
                  <input 
                    type="text" 
                    placeholder="1.0.0"
                    className="w-full bg-transparent border-b border-slate-200 focus:border-purple-500 py-1 text-lg font-black text-slate-900 focus:outline-none transition-all placeholder:text-slate-300"
                    value={formData.version}
                    onChange={(e) => setFormData({...formData, version: e.target.value})}
                  />
                </div>

                {/* Description Card */}
                <div className="bg-slate-50 rounded-[2rem] p-6 border border-slate-100 hover:border-amber-200 hover:bg-white transition-all group shadow-sm">
                  <div className="flex items-center space-x-3 mb-3 text-amber-600">
                    <span className="text-xl">📝</span>
                    <label className="text-[10px] font-black uppercase tracking-[0.2em]">Domain description</label>
                  </div>
                  <textarea 
                    rows="2"
                    placeholder="Describe the objective..."
                    className="w-full bg-transparent border-b border-slate-200 focus:border-amber-500 py-1 text-xs font-bold text-slate-700 focus:outline-none transition-all resize-none placeholder:text-slate-300"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                  />
                </div>

                {/* PDF Card */}
                <div 
                  className={`relative group rounded-[2rem] border-2 border-dashed transition-all duration-300 flex items-center justify-between p-6 ${
                    isDragging ? 'border-blue-500 bg-blue-50' : 
                    formData.pdfFile ? 'border-emerald-200 bg-emerald-50/50' : 'border-slate-200 bg-slate-50 hover:border-emerald-400 hover:bg-white'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <input 
                    type="file" 
                    accept=".pdf"
                    className="hidden" 
                    id="pdf-upload"
                    onChange={(e) => setFormData({...formData, pdfFile: e.target.files[0]})}
                  />
                  
                  {!formData.pdfFile ? (
                    <label htmlFor="pdf-upload" className="flex items-center space-x-4 w-full cursor-pointer">
                      <div className="w-12 h-12 bg-white rounded-2xl shadow-sm border border-slate-100 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                        📄
                      </div>
                      <div className="flex-1">
                        <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Context Source</p>
                        <p className="text-xs font-black text-slate-600">Click or drop PDF here</p>
                      </div>
                    </label>
                  ) : (
                    <div className="flex items-center space-x-4 w-full animate-fadeIn">
                      <div className="w-12 h-12 bg-white rounded-2xl shadow-sm border border-emerald-100 flex items-center justify-center text-2xl">
                        📑
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-black text-slate-900 truncate">{formData.pdfFile.name}</p>
                        <p className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">
                          {formatFileSize(formData.pdfFile.size)}
                        </p>
                      </div>
                      <button 
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFormData({...formData, pdfFile: null});
                        }}
                        className="w-8 h-8 rounded-full bg-white text-rose-500 border border-slate-100 flex items-center justify-center hover:bg-rose-500 hover:text-white transition-all"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-6 pt-4">
                <button 
                  type="button"
                  onClick={() => setShowMetadataForm(false)}
                  className="px-8 py-4 bg-slate-100 text-slate-500 font-black uppercase tracking-widest text-[10px] rounded-2xl hover:bg-slate-200 transition-all"
                >
                  Discard Changes
                </button>
                <button 
                  type="submit"
                  className="flex-1 py-4 bg-blue-600 text-white font-black uppercase tracking-widest text-[10px] rounded-2xl hover:bg-blue-700 shadow-xl shadow-blue-100 transition-all"
                >
                  Generate Intelligence Pack
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
