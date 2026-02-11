import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
  const { logout } = useAuth();
  
  const [viewMode, setViewMode] = useState('visual'); // 'visual' | 'yaml'
  const [activeTab, setActiveTab] = useState('entities');
  const [yamlContent, setYamlContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

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

  const domainId = session?.id;

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
  }, [domainId]);

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
      onBack(); // Navigate back to dashboard
    } catch (err) {
      alert("Failed to delete domain: " + err.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <Header
        title={session?.name || 'Domain Configuration'}
        subtitle={session?.description || 'Configure your domain pack'}
        showBackButton={true}
        onBack={onBack}
        showSidebarToggle={true}
        toggleSidebar={toggleSidebar}
        rightActions={
          <>
            {!isChatOpen && (
              <button
                onClick={onProceed}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-xl hover:from-purple-700 hover:to-blue-700 shadow-lg shadow-purple-200 transition-all flex items-center space-x-2"
              >
                <span className="text-lg">💬</span>
                <span>Open Chatbot</span>
              </button>
            )}
            <button
              onClick={viewMode === 'visual' ? handleSaveVisual : handleSaveYAML}
              disabled={saving}
              className={`px-4 py-2 text-white font-bold rounded-xl shadow-lg transition-all flex items-center space-x-2 ${
                saving ? 'bg-slate-400 cursor-not-allowed shadow-none' : 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-200'
              }`}
            >
              <span>{saving ? '⏳ Saving...' : '💾 Save Changes'}</span>
            </button>
            <button
              onClick={() => setViewMode(viewMode === 'visual' ? 'yaml' : 'visual')}
              className="px-4 py-2 bg-slate-100 text-slate-700 font-bold rounded-xl hover:bg-slate-200 transition-colors flex items-center space-x-2"
            >
              <span>{viewMode === 'visual' ? '📝 YAML Editor' : '👁️ Visual View'}</span>
            </button>
            <button
              onClick={handleDeleteDomain}
              className="px-4 py-2 bg-red-50 text-red-600 font-bold rounded-xl hover:bg-red-600 hover:text-white transition-all flex items-center space-x-2 border border-red-100"
              title="Delete this domain pack"
            >
              <span>🗑️ Delete Pack</span>
            </button>
          </>
        }
      />

      {/* Step Indicator */}
      <StepIndicator currentStep={2} />

      {/* Main Content */}
      <div className={`mx-auto p-6 transition-all ${isChatOpen ? 'max-w-[calc(100vw-450px)]' : 'max-w-7xl'}`}>
        <div className="space-y-6 max-h-[calc(100vh-280px)] overflow-y-auto pb-20">
          {viewMode === 'visual' ? (
            <>
              {/* Tab Navigation */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-2 flex space-x-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm transition-all ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-200'
                        : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.label}
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
