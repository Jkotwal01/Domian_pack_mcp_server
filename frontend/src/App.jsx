import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import Dashboard from './components/Dashboard';
import ConfigView from './components/ConfigView';
import { useChat } from './hooks/useChat';
import { useChatSessions } from './hooks/useChatSessions';
import { listVersions, rollbackVersion, deleteVersion, getDownloadUrl } from './services/api';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard', 'config', 'chat'
  
  const [versions, setVersions] = useState([]);
  const [currentVersion, setCurrentVersion] = useState(null);
  const [configSession, setConfigSession] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);

  const {
    sessions,
    activeSessionId,
    activeSession,
    addSession,
    deleteSession,
    renameSession,
    updateSessionMessages,
    updateMcpSessionId,
    switchSession
  } = useChatSessions();

  // Fetch versions when session ID changes
  useEffect(() => {
    if (activeSession?.mcpSessionId) {
      fetchVersions(activeSession.mcpSessionId);
    } else {
      setVersions([]);
      setCurrentVersion(null);
    }
  }, [activeSession?.mcpSessionId]);

  const fetchVersions = async (mcpId) => {
    try {
      const data = await listVersions(mcpId);
      setVersions(data);
      if (data.length > 0) setCurrentVersion(data[0].version);
    } catch (err) {
      console.error("Failed to fetch versions:", err);
    }
  };

  const handleRollback = async (targetVersion) => {
    if (!activeSession?.mcpSessionId) return;
    try {
      await rollbackVersion(activeSession.mcpSessionId, targetVersion);
      await fetchVersions(activeSession.mcpSessionId);
    } catch (err) {
      console.error("Rollback failed:", err);
    }
  };

  const handleDeleteVersion = async (vNum) => {
    if (!activeSession?.mcpSessionId) return;
    try {
      await deleteVersion(activeSession.mcpSessionId, vNum);
      await fetchVersions(activeSession.mcpSessionId);
    } catch (err) {
      console.error("Delete version failed:", err);
      alert(err.message);
    }
  };
  
  const handleDownload = () => {
    if (!activeSession?.mcpSessionId) return;
    const url = getDownloadUrl(activeSession.mcpSessionId, 'yaml');
    window.open(url, '_blank');
  };

  const handleShowDashboard = () => {
    setActiveView('dashboard');
    setIsChatOpen(false);
  };

  const handleShowChat = () => {
    // This is now handled within the config view
    setIsChatOpen(true);
  };

  const handleSelectDomain = (session) => {
    setConfigSession(session);
    setActiveView('config');
    setIsChatOpen(false);
  };

  const handleCreateDomain = (newDomain) => {
    // newDomain: {id, name, description, version, isTemplate}
    const session = {
      id: newDomain.id,
      name: newDomain.name,
      description: newDomain.description,
      version: newDomain.version,
      isTemplate: true,
      stats: { entities: 0, relations: 0 }
    };
    setConfigSession(session);
    setActiveView('config');
  };

  const handleProceedToEnhancement = () => {
    if (!configSession) return;
    
    // Check if session exists in our hook sessions
    let existingSession = sessions.find(s => s.mcpSessionId === configSession.session_id);
    
    if (!existingSession) {
      // If it's a new template session, initialize it in our hook
      addSession({
        title: configSession.domain_name,
      });
    } else {
      switchSession(existingSession.id);
    }
    
    setIsChatOpen(true);
  };

  const { messages, isTyping, uploadingFiles, sendMessage, handleConfirmIntent, messagesEndRef } = useChat(
    activeSessionId,
    activeSession?.mcpSessionId || null,
    activeSession?.messages || [],
    (newMessages) => {
      if (activeSessionId) {
        updateSessionMessages(activeSessionId, newMessages);
      }
    },
    (mcpSessionId) => {
      if (activeSessionId) {
        updateMcpSessionId(activeSessionId, mcpSessionId);
      }
    },
    (mcpId) => fetchVersions(mcpId)
  );

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden text-slate-900 font-sans">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen} 
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        activeView={activeView}
        onShowDashboard={handleShowDashboard}
        onShowChat={handleShowChat}
      />
      
      {/* Main Content */}
      <main className={`flex-1 flex flex-col h-full relative transition-all duration-300 ease-in-out bg-white`}>
        {activeView === 'config' && (
          <div className="flex h-full w-full overflow-hidden">
            <div className={`flex-1 overflow-hidden transition-all duration-300 ${isChatOpen ? 'w-1/2' : 'w-full'}`}>
              <ConfigView 
                session={configSession} 
                onProceed={handleProceedToEnhancement} 
                sidebarOpen={sidebarOpen}
                toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                isChatOpen={isChatOpen}
                onToggleChat={() => setIsChatOpen(!isChatOpen)}
                onBack={handleShowDashboard}
              />
            </div>
            {isChatOpen && (
              <div className="w-1/2 border-l border-slate-200 animate-slideInRight h-full overflow-hidden">
                <ChatArea 
                  messages={messages} 
                  isTyping={isTyping}
                  uploadingFiles={uploadingFiles}
                  onSendMessage={sendMessage} 
                  onConfirmIntent={handleConfirmIntent}
                  messagesEndRef={messagesEndRef}
                  sidebarOpen={false} // Chat sidebar is fixed in this view
                  toggleSidebar={() => {}} // No toggle in this view
                  isEnhancementView={true}
                  configSession={configSession}
                  onClose={() => setIsChatOpen(false)}
                />
              </div>
            )}
          </div>
        )}
        
        {activeView === 'dashboard' && (
          <Dashboard 
            onSelectDomain={handleSelectDomain} 
            onCreateDomain={handleCreateDomain}
            sidebarOpen={sidebarOpen}
            toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />
        )}
      </main>
    </div>
  );
}

export default App;

