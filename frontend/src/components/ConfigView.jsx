import React, { useState, useEffect } from 'react';
import { getDomainPackExport, syncDomainPack } from '../services/api';

const StepIndicator = ({ currentStep }) => {
  const steps = [
    { num: 1, text: "Select Domain", sub: "Choose from existing or create a new template" },
    { num: 2, text: "Customize Domain", sub: "Define entities, attributes and relationships" },
    { num: 3, text: "Export & Generate", sub: "Generate final pack and export for use" }
  ];

  return (
    <div className="bg-white border-b border-slate-100 py-8">
      <div className="max-w-5xl mx-auto flex items-start justify-between relative px-4">
        {/* Connecting Line */}
        <div className="absolute top-5 left-12 right-12 h-0.5 bg-slate-100 -z-0"></div>
        
        {steps.map((step) => (
          <div key={step.num} className="flex flex-col items-center relative z-10 w-1/3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm mb-3 transition-colors ${
              currentStep === step.num 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' 
                : currentStep > step.num ? 'bg-emerald-500 text-white' : 'bg-blue-50 text-blue-600'
            }`}>
              {currentStep > step.num ? '✓' : step.num}
            </div>
            <h3 className={`font-bold text-sm mb-1 ${currentStep === step.num ? 'text-slate-900' : 'text-slate-400'}`}>
              {step.text}
            </h3>
            <p className="text-[10px] text-slate-400 text-center max-w-[150px] leading-tight px-2">
              {step.sub}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function ConfigView({ session, onProceed, toggleSidebar, isChatOpen, onToggleChat, onBack }) {
  const [viewMode, setViewMode] = useState('visual'); // 'visual' | 'yaml'
  const [domainData, setDomainData] = useState(null);
  const [yamlContent, setYamlContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [isEntitiesOpen, setIsEntitiesOpen] = useState(true);

  const domainId = session?.session_id || session?.id;

  useEffect(() => {
    if (domainId) {
      fetchDomainData();
    }
  }, [domainId]);

  const fetchDomainData = async () => {
    setLoading(true);
    try {
      const data = await getDomainPackExport(domainId);
      setDomainData(data.json);
      setYamlContent(data.yaml);
    } catch (err) {
      console.error("Failed to fetch domain data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveYaml = async () => {
    setLoading(true);
    try {
      await syncDomainPack(domainId, { yaml: yamlContent });
      await fetchDomainData();
      setViewMode('visual');
    } catch (err) {
      alert("Failed to save: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !domainData) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-50 overflow-y-auto">
      {/* Step Indicator Header */}
      <StepIndicator currentStep={2} />

      <div className="px-8 max-w-6xl mx-auto w-full py-8 space-y-6">
        {/* Navigation Actions */}
        <div className="flex items-center justify-between">
          <button 
            onClick={onBack}
            className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-bold text-slate-600 hover:bg-slate-50 transition-all shadow-sm"
          >
            Back to Dashboard
          </button>
          
          <button 
            onClick={() => setViewMode(viewMode === 'visual' ? 'yaml' : 'visual')}
            className={`px-6 py-2.5 font-bold rounded-lg text-sm transition-all shadow-md flex items-center space-x-2 ${
              viewMode === 'visual' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            <span>{viewMode === 'visual' ? 'Edit Configuration (YAML) →' : 'Switch to Visual View'}</span>
          </button>
        </div>

        {/* Configuration Card Container */}
        <div className="bg-white rounded-[1.5rem] border border-slate-100 shadow-sm overflow-hidden min-h-[500px]">
          {/* Internal Header */}
          <div className="px-8 py-6 border-b border-slate-50 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-rose-50 rounded-xl flex items-center justify-center text-2xl">
                🚗
              </div>
              <div className="space-y-0.5">
                <h1 className="text-xl font-black text-slate-900 leading-tight">
                  {domainData?.name || 'Domain'} Configuration
                </h1>
                <p className="text-slate-400 text-sm font-medium">
                  {viewMode === 'visual' ? 'Read-only view of domain configuration details' : 'Edit mode for domain configuration'}
                </p>
              </div>
            </div>
            <button className="text-slate-300 hover:text-slate-500 transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Subheader Information */}
          <div className="mx-8 mt-6">
            <div className="bg-blue-50/50 border border-blue-100 rounded-2xl p-4 flex items-center justify-between">
              <div>
                <h3 className="text-blue-900 font-bold text-sm">{domainData?.name} Domain</h3>
                <p className="text-blue-600 text-xs font-semibold">Base Template</p>
              </div>
              <div className="text-blue-600 text-xs font-bold uppercase tracking-wider">
                {viewMode === 'visual' ? 'Read-Only View' : 'Editing Mode'}
              </div>
            </div>
          </div>

          {/* Content Area */}
          <div className="p-8">
            {viewMode === 'visual' ? (
              <div className="space-y-6">
                {/* Entities Section */}
                <div className="border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
                  <button 
                    onClick={() => setIsEntitiesOpen(!isEntitiesOpen)}
                    className="w-full px-6 py-4 bg-slate-50/50 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span className="font-black text-slate-900">Entities</span>
                      <span className="bg-white border border-slate-100 text-slate-600 px-2.5 py-0.5 rounded-full text-xs font-bold">
                        {domainData?.entities?.length || 0}
                      </span>
                    </div>
                    <svg className={`w-5 h-5 text-slate-400 transition-transform ${isEntitiesOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {isEntitiesOpen && (
                    <div className="p-6 space-y-4 bg-white">
                      {domainData?.entities?.length > 0 ? (
                        domainData.entities.map((entity, idx) => (
                          <div key={idx} className="border border-slate-50 rounded-xl p-6 hover:shadow-sm transition-shadow">
                            <h4 className="text-lg font-black text-slate-900 mb-4 tracking-tight uppercase">
                              {entity.name}
                            </h4>
                            <div className="space-y-3">
                              <p className="text-slate-400 text-xs font-bold uppercase">Attributes:</p>
                              <div className="flex flex-wrap gap-2">
                                {entity.attributes.map((attr, aIdx) => (
                                  <span key={aIdx} className="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-xs font-bold border border-blue-100">
                                    {attr}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-3">
                          <p className="font-bold">No entities defined yet.</p>
                          <p className="text-xs">Use the editor or chatbot to add entities.</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                {/* Relationships Section */}
                <div className="border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
                  <button 
                    onClick={() => setViewMode('relationships_open')} // Using a simple state toggle or local state
                    className="w-full px-6 py-4 bg-slate-50/50 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                      </svg>
                      <span className="font-black text-slate-900">Relationships</span>
                      <span className="bg-white border border-slate-100 text-slate-600 px-2.5 py-0.5 rounded-full text-xs font-bold">
                        {domainData?.relationships?.length || 0}
                      </span>
                    </div>
                  </button>
                  <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4 bg-white">
                    {domainData?.relationships?.map((rel, idx) => (
                      <div key={idx} className="p-4 border border-slate-50 rounded-xl bg-slate-50/30">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-black text-blue-600 uppercase tracking-wider">{rel.from}</span>
                          <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                          </svg>
                          <span className="text-[10px] font-black text-blue-600 uppercase tracking-wider">{rel.to}</span>
                        </div>
                        <h5 className="text-sm font-bold text-slate-800 text-center">{rel.name}</h5>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Extraction Patterns Section */}
                <div className="border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
                  <div className="px-6 py-4 bg-slate-50/50 flex items-center space-x-3">
                    <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <span className="font-black text-slate-900">Extraction Patterns</span>
                    <span className="bg-white border border-slate-100 text-slate-600 px-2.5 py-0.5 rounded-full text-xs font-bold">
                      {domainData?.extraction_patterns?.length || 0}
                    </span>
                  </div>
                  <div className="divide-y divide-slate-50 bg-white">
                    {domainData?.extraction_patterns?.map((pattern, idx) => (
                      <div key={idx} className="p-4 flex items-center justify-between group hover:bg-slate-50/50 transition-colors">
                        <div className="space-y-1">
                          <code className="text-xs font-mono text-rose-600 bg-rose-50 px-2 py-0.5 rounded">
                            {pattern.pattern}
                          </code>
                          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">
                            Extracts <span className="text-slate-600">{pattern.attribute}</span> for <span className="text-slate-600">{pattern.entity_type}</span>
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500" style={{ width: `${(pattern.confidence || 0) * 100}%` }}></div>
                          </div>
                          <span className="text-[10px] font-black text-slate-400">{(pattern.confidence || 0) * 100}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6 h-full">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-black text-slate-900 uppercase text-sm tracking-wider">YAML Configuration Editor</h3>
                  <button 
                    onClick={handleSaveYaml}
                    disabled={loading}
                    className="px-6 py-2 bg-emerald-600 text-white font-bold rounded-xl text-sm hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-100 flex items-center space-x-2"
                  >
                    {loading ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white animate-spin rounded-full"></div>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                    <span>Save Configuration</span>
                  </button>
                </div>
                <textarea
                  value={yamlContent}
                  onChange={(e) => setYamlContent(e.target.value)}
                  className="w-full h-[600px] p-6 font-mono text-sm bg-slate-900 text-blue-100 rounded-2xl border-none focus:ring-4 focus:ring-blue-500/20 transition-all outline-none"
                  spellCheck="false"
                  placeholder="Paste or write your domain pack YAML here..."
                />
              </div>
            )}
          </div>
        </div>

        {/* Chatbot Toggle Button */}
        {!isChatOpen && (
          <div className="flex justify-center pt-4">
            <button 
              onClick={onProceed}
              className="px-8 py-3 bg-white border border-slate-200 text-slate-900 font-black rounded-2xl hover:bg-slate-50 shadow-xl shadow-slate-200 transition-all flex items-center space-x-3 group"
            >
              <span className="text-xl">💬</span>
              <span>Open Chatbot for Enhancement</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
