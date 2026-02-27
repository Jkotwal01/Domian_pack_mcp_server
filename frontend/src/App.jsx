import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import Dashboard from './pages/Dashboard';
import ConfigView from './pages/ConfigView';
import Monitoring from './pages/Monitoring';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ProtectedRoute from './components/ProtectedRoute';
import GuestRoute from './components/GuestRoute';
import { AuthProvider } from './context/AuthContext';
import { useChat } from './hooks/useChat';
import { useChatSessions } from './hooks/useChatSessions';
import { listVersions, rollbackVersion, deleteVersion, getDownloadUrl } from './services/api';

function AppContent() {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [versions, setVersions] = useState([]);
  const [currentVersion, setCurrentVersion] = useState(null);

  const {
    sessions,
    activeSessionId,
    activeSession,
    addSession,
    deleteSession: deleteSessionHook,
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

  const handleProceedToEnhancement = (domainId, domainName, sessionId) => {
    // Look for existing session that matches this domain
    // Critical fix: Ensure we don't accidentally match on undefined/null session IDs
    let existingSession = sessions.find(s => 
      (domainId && s.domainConfigId === domainId) || 
      (sessionId && s.mcpSessionId === sessionId)
    );
    
    if (!existingSession) {
      addSession({
        title: domainName,
        domainConfigId: domainId,
        mcpSessionId: sessionId || null
      });
    } else {
      switchSession(existingSession.id);
    }
    
    setIsChatOpen(true);
  };

  const [configUpdateTrigger, setConfigUpdateTrigger] = useState(0);

  const refreshDomainConfig = () => {
    console.log('[App] Refreshing domain configuration...');
    setConfigUpdateTrigger(prev => prev + 1);
  };

  const { 
    messages, 
    isTyping, 
    uploadingFiles, 
    sendMessage, 
    handleConfirmIntent, 
    deleteCurrentSession, 
    messagesEndRef 
  } = useChat(
    activeSessionId,
    activeSession?.domainConfigId || null,
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
    (domainId) => {
      fetchVersions(activeSession?.mcpSessionId);
      refreshDomainConfig(); // Trigger config refresh on any change
    }
  );

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden text-slate-900 font-sans">
      <Sidebar 
        isOpen={sidebarOpen} 
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <main className={`flex-1 flex flex-col h-full relative transition-all duration-300 ease-in-out bg-white overflow-y-auto`}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          <Route 
            path="/dashboard" 
            element={
              <Dashboard 
                sidebarOpen={sidebarOpen}
                toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
              />
            } 
          />

          <Route 
            path="/monitoring" 
            element={
              <Monitoring 
                sidebarOpen={sidebarOpen}
                toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
              />
            } 
          />
          
          <Route 
            path="/configview/:domainId" 
            element={
              <div className="flex h-full w-full overflow-hidden">
                <div className={`flex-1 overflow-hidden transition-all duration-300 ${isChatOpen ? 'w-1/2' : 'w-full'}`}>
                  <ConfigView 
                    onProceed={handleProceedToEnhancement} 
                    sidebarOpen={sidebarOpen}
                    toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                    isChatOpen={isChatOpen}
                    onToggleChat={() => setIsChatOpen(!isChatOpen)}
                    refreshTrigger={configUpdateTrigger}
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
                      onDelete={deleteCurrentSession}
                      messagesEndRef={messagesEndRef}
                      sidebarOpen={false}
                      toggleSidebar={() => {}} 
                      isEnhancementView={true}
                      onClose={() => setIsChatOpen(false)}
                    />
                  </div>
                )}
              </div>
            } 
          />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
          <Route path="/signup" element={<GuestRoute><Signup /></GuestRoute>} />
          {/* Proper route protection restored */}
          <Route 
            path="/*" 
            element={
              <ProtectedRoute>
                <AppContent />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

