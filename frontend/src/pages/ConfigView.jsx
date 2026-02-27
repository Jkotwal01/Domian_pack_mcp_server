import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getDomainPackExport, syncDomainPack, deleteDomain, updateDomain } from '../services/api';
import { mockDomainData } from '../utils/mockData';
import { useAuth } from '../context/AuthContext';
import useDomainData from '../hooks/useDomainData';

// Common components
import Header from '../components/common/Header';

// Modal components
import EntityModal from '../components/modals/EntityModal';
import RelationshipModal from '../components/modals/RelationshipModal';
import PatternModal from '../components/modals/PatternModal';
import KeyTermModal from '../components/modals/KeyTermModal';

// Section components
import EntitiesSection from '../components/sections/EntitiesSection';
import RelationshipsSection from '../components/sections/RelationshipsSection';
import PatternsSection from '../components/sections/PatternsSection';
import KeyTermsSection from '../components/sections/KeyTermsSection';

// Set to true to use mock data instead of API calls
const USE_MOCK_DATA = false;

const StepIndicator = ({ currentStep }) => {
  const steps = [
    { num: 1, text: "Select", sub: "Template Selection" },
    { num: 2, text: "Design", sub: "Domain Customization" },
    { num: 3, text: "Deploy", sub: "Export & Pack" }
  ];

  return (
    <div className="bg-white/50 backdrop-blur-md border-b border-indigo-50/50 py-10">
      <div className="max-w-4xl mx-auto flex items-start justify-between relative px-6">
        {/* Modern Connecting Line */}
        <div className="absolute top-5 left-16 right-16 h-[2px] bg-slate-100/80 -z-0">
          <div 
            className="h-full bg-linear-to-r from-indigo-500 to-violet-500 transition-all duration-700 ease-out"
            style={{ width: `${(currentStep - 1) * 50}%` }}
          ></div>
        </div>
        
        {steps.map((step) => (
          <div key={step.num} className="flex flex-col items-center relative z-10">
            <div className={`w-11 h-11 rounded-2xl flex items-center justify-center font-black text-sm mb-4 transition-all duration-500 ${
              currentStep === step.num 
                ? 'bg-linear-to-br from-indigo-600 to-violet-700 text-white shadow-xl shadow-indigo-200 rotate-3 scale-110' 
                : currentStep > step.num 
                  ? 'bg-emerald-500 text-white rotate-0' 
                  : 'bg-white text-slate-400 border border-slate-100 shadow-sm'
            }`}>
              {currentStep > step.num ? '✓' : `0${step.num}`}
            </div>
            <h3 className={`font-black text-[11px] uppercase tracking-[0.2em] mb-1.5 ${currentStep === step.num ? 'text-slate-900' : 'text-slate-400'}`}>
              {step.text}
            </h3>
            <p className="text-[10px] text-slate-400 font-bold text-center max-w-[120px] leading-tight opacity-60">
              {step.sub}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function ConfigView({ onProceed, toggleSidebar, isChatOpen, onToggleChat, refreshTrigger = 0 }) {
  const navigate = useNavigate();
  const { domainId } = useParams();
  const { logout } = useAuth();
  
  const [viewMode, setViewMode] = useState('visual'); // 'visual' | 'yaml'
  const [activeTab, setActiveTab] = useState('entities');
  const [yamlContent, setYamlContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [session, setSession] = useState(null);

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Modal states
  const [showAddEntityModal, setShowAddEntityModal] = useState(false);
  const [showAddRelationshipModal, setShowAddRelationshipModal] = useState(false);
  const [showAddPatternModal, setShowAddPatternModal] = useState(false);
  const [showAddTermModal, setShowAddTermModal] = useState(false);
  
  const [editingEntity, setEditingEntity] = useState(null);
  const [editingRelationship, setEditingRelationship] = useState(null);
  const [editingPattern, setEditingPattern] = useState(null);

  // Use custom hook for domain data management
  const {
    domainData,
    setDomainData,
    handleAddEntity,
    handleEditEntity,
    handleDeleteEntity,
    handleDuplicateEntity,
    handleAddRelationship,
    handleEditRelationship,
    handleDeleteRelationship,
    handleAddPattern,
    handleEditPattern,
    handleDeletePattern,
    handleAddTerm,
    handleDeleteTerm
  } = useDomainData();

  // Fetch domain session data
  useEffect(() => {
    const fetchDomainSession = async () => {
      if (!domainId) return;
      
      setLoading(true);
      try {
        // Fetch the domain details to populate session data
        const data = await getDomainPackExport(domainId);
        setSession({
          id: domainId,
          name: data.name || 'Domain Configuration',
          description: data.description || 'Configure your domain pack',
          session_id: data.session_id,
          domain_name: data.name
        });
      } catch (error) {
        console.error('Error fetching domain session:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDomainSession();
  }, [domainId, refreshTrigger]); // Add refreshTrigger to sync

  // Fetch domain data
  useEffect(() => {
    const fetchDomainData = async () => {
      if (!domainId) return;

      setLoading(true);
      try {
        if (USE_MOCK_DATA) {
          const mockData = mockDomainData[domainId];
          if (mockData) {
            setDomainData(mockData.json);
            setYamlContent(mockData.yaml);
          } else {
            // Empty domain structure
            const emptyDomain = {
              entities: [],
              relationships: [],
              extraction_patterns: [],
              key_terms: []
            };
            setDomainData(emptyDomain);
            setYamlContent('# Empty domain pack\nentities: []\nrelationships: []\nextraction_patterns: []\nkey_terms: []');
          }
        } else {
          const data = await getDomainPackExport(domainId);
          setDomainData(data.json);
          setYamlContent(data.yaml);
        }
      } catch (error) {
        console.error('Error fetching domain data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDomainData();
  }, [domainId, refreshTrigger]); // Add refreshTrigger to sync

  // Save YAML content
  const handleSaveYAML = async () => {
    try {
      setSaving(true);
      await syncDomainPack(domainId, yamlContent);
      alert('Changes saved successfully!');
    } catch (error) {
      console.error('Error saving YAML:', error);
      alert('Failed to save changes: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  // Save Visual content
  const handleSaveVisual = async () => {
    try {
      setSaving(true);
      await updateDomain(domainId, domainData);
      alert('Changes saved successfully!');
    } catch (error) {
      console.error('Error saving domain:', error);
      alert('Failed to save changes: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  // Tab configuration
  const tabs = [
    { id: 'entities', label: 'Entities', icon: '🏗️' },
    { id: 'relationships', label: 'Relationships', icon: '🔗' },
    { id: 'extraction_patterns', label: 'Extraction Patterns', icon: '🔍' },
    { id: 'key_terms', label: 'Key Terms', icon: '🏷️' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-600 font-bold">Loading domain configuration...</p>
        </div>
      </div>
    );
  }

  const handleDeleteDomain = async () => {
    if (!window.confirm("Are you sure you want to delete this domain pack? This action cannot be undone and you will be returned to the dashboard.")) {
      return;
    }

    try {
      setLoading(true);
      await deleteDomain(domainId);
      // Navigate back to dashboard
      navigate('/dashboard');
    } catch (err) {
      alert("Failed to delete domain: " + err.message);
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleProceedToChat = () => {
    if (session && onProceed) {
      onProceed(domainId, session.domain_name || session.name, session.session_id);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <Header
        title={session?.name || 'Domain Configuration'}
        subtitle={session?.description || 'Build and refine your domain architecture'}
        showBackButton={true}
        onBack={handleBack}
        showSidebarToggle={true}
        toggleSidebar={toggleSidebar}
        rightActions={
          <div className="flex items-center space-x-3">
            {!isChatOpen && (
              <button
                onClick={handleProceedToChat}
                className="px-5 py-2.5 bg-linear-to-r from-indigo-600 to-violet-700 text-white font-black text-[10px] uppercase tracking-widest rounded-xl hover:from-indigo-700 hover:to-violet-800 shadow-xl shadow-indigo-100 transition-all flex items-center space-x-2 active:scale-95"
              >
                <span className="text-sm">💬</span>
                <span>Chatbot</span>
              </button>
            )}
            <button
              onClick={viewMode === 'visual' ? handleSaveVisual : handleSaveYAML}
              disabled={saving}
              className={`px-5 py-2.5 text-white font-black text-[10px] uppercase tracking-widest rounded-xl shadow-xl transition-all flex items-center space-x-2 active:scale-95 ${
                saving ? 'bg-slate-400 cursor-not-allowed shadow-none' : 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-100'
              }`}
            >
              <span>{saving ? '⏳ Saving' : '💾 Save State'}</span>
            </button>
            <button
              onClick={() => setViewMode(viewMode === 'visual' ? 'yaml' : 'visual')}
              className="px-5 py-2.5 bg-white text-slate-700 font-black text-[10px] uppercase tracking-widest rounded-xl border border-slate-200 hover:bg-slate-50 transition-all flex items-center space-x-2 shadow-sm active:scale-95"
            >
              <span>{viewMode === 'visual' ? '🛠️ YAML Mode' : '👁️ Visual Mode'}</span>
            </button>
            <button
              onClick={handleDeleteDomain}
              className="p-2.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all border border-transparent hover:border-red-100 active:scale-90"
              title="Delete this domain pack"
            >
              <span className="text-lg">🗑️</span>
            </button>
          </div>
        }
      />

      {/* Step Indicator */}
      <StepIndicator currentStep={2} />

      {/* Main Content */}
      <div className={`mx-auto p-6 transition-all ${isChatOpen ? 'max-w-[calc(100vw-450px)]' : 'max-w-7xl'}`}>
        <div className="space-y-6 max-h-[calc(100vh-280px)] overflow-y-auto pb-20">
          {viewMode === 'visual' ? (
            <>
            {/* Header Actions */}
            <div className="flex bg-white/40 backdrop-blur-sm p-1 rounded-2xl border border-indigo-50/50 shadow-sm mb-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center space-x-2.5 py-3 px-6 rounded-xl font-black text-xs uppercase tracking-[0.15em] transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-linear-to-br from-indigo-600 to-violet-700 text-white shadow-xl shadow-indigo-200 -translate-y-0.5'
                      : 'text-slate-500 hover:text-indigo-600 hover:bg-white/60'
                  }`}
                >
                  <span className="text-sm filter drop-shadow-sm">{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

              {/* Tab Content */}
              <div>
                {activeTab === 'entities' && (
                  <EntitiesSection
                    entities={domainData?.entities}
                    onAdd={() => setShowAddEntityModal(true)}
                    onEdit={(index, entity) => setEditingEntity({ index, data: entity })}
                    onDuplicate={handleDuplicateEntity}
                    onDelete={handleDeleteEntity}
                  />
                )}

                {activeTab === 'relationships' && (
                  <RelationshipsSection
                    relationships={domainData?.relationships}
                    onAdd={() => setShowAddRelationshipModal(true)}
                    onEdit={(index, relationship) => setEditingRelationship({ index, data: relationship })}
                    onDelete={handleDeleteRelationship}
                  />
                )}

                {activeTab === 'extraction_patterns' && (
                  <PatternsSection
                    patterns={domainData?.extraction_patterns}
                    onAdd={() => setShowAddPatternModal(true)}
                    onEdit={(index, pattern) => setEditingPattern({ index, data: pattern })}
                    onDelete={handleDeletePattern}
                  />
                )}

                {activeTab === 'key_terms' && (
                  <KeyTermsSection
                    keyTerms={domainData?.key_terms}
                    onAdd={() => setShowAddTermModal(true)}
                    onDelete={handleDeleteTerm}
                  />
                )}
              </div>
            </>
          ) : (
            /* YAML Editor View */
            <div className="bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden">
              <div className="px-6 py-4 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
                <h3 className="font-black text-slate-900">YAML Editor</h3>
                <button
                  onClick={handleSaveYAML}
                  className="px-6 py-2 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all"
                >
                  💾 Save Changes
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



      {/* Modals */}
      {(showAddEntityModal || editingEntity) && (
        <EntityModal
          entity={editingEntity?.data}
          onSave={(entity) => {
            if (editingEntity) {
              handleEditEntity(editingEntity.index, entity);
            } else {
              handleAddEntity(entity);
            }
            setShowAddEntityModal(false);
            setEditingEntity(null);
          }}
          onClose={() => {
            setShowAddEntityModal(false);
            setEditingEntity(null);
          }}
        />
      )}

      {(showAddRelationshipModal || editingRelationship) && (
        <RelationshipModal
          relationship={editingRelationship?.data}
          entities={domainData?.entities || []}
          onSave={(relationship) => {
            if (editingRelationship) {
              handleEditRelationship(editingRelationship.index, relationship);
            } else {
              handleAddRelationship(relationship);
            }
            setShowAddRelationshipModal(false);
            setEditingRelationship(null);
          }}
          onClose={() => {
            setShowAddRelationshipModal(false);
            setEditingRelationship(null);
          }}
        />
      )}

      {(showAddPatternModal || editingPattern) && (
        <PatternModal
          pattern={editingPattern?.data}
          entities={domainData?.entities || []}
          onSave={(pattern) => {
            if (editingPattern) {
              handleEditPattern(editingPattern.index, pattern);
            } else {
              handleAddPattern(pattern);
            }
            setShowAddPatternModal(false);
            setEditingPattern(null);
          }}
          onClose={() => {
            setShowAddPatternModal(false);
            setEditingPattern(null);
          }}
        />
      )}

      {showAddTermModal && (
        <KeyTermModal
          onSave={(term) => {
            handleAddTerm(term);
            setShowAddTermModal(false);
          }}
          onClose={() => setShowAddTermModal(false)}
        />
      )}
    </div>
  );
}
