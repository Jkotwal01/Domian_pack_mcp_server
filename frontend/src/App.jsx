import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import Dashboard from './components/Dashboard';
import { useChat } from './hooks/useChat';
import { useChatSessions } from './hooks/useChatSessions';
import { listVersions, rollbackVersion, deleteVersion, getDownloadUrl } from './services/api';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState('chat'); // 'chat' or 'dashboard'
  
  const [versions, setVersions] = useState([]);
  const [currentVersion, setCurrentVersion] = useState(null);

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
      const result = await rollbackVersion(activeSession.mcpSessionId, targetVersion);
      // Refresh versions
      await fetchVersions(activeSession.mcpSessionId);
      // Optional: Add a system message about successful rollback
      // It will show up in the next chat fetch or we can manually push it
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
  };

  const handleShowChat = () => {
    setActiveView('chat');
  };

  const { messages, isTyping, uploadingFiles, sendMessage, handleConfirmIntent, messagesEndRef } = useChat(
    activeSessionId,
    activeSession?.mcpSessionId || null,  // Pass MCP session ID to backend
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
    (mcpId) => fetchVersions(mcpId) // Refresh versions callback
  );

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen} 
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onNewChat={() => {
          addSession();
          setActiveView('chat');
        }}
        onSelectSession={(id) => {
          switchSession(id);
          setActiveView('chat');
        }}
        onDeleteSession={deleteSession}
        onRenameSession={renameSession}
        onDownload={handleDownload}
        versions={versions}
        currentVersion={currentVersion}
        onRollback={handleRollback}
        onShowDashboard={handleShowDashboard}
        onDeleteVersion={handleDeleteVersion}
        mcpSessionId={activeSession?.mcpSessionId}
      />
      
      {/* Main Content */}
      <main className={`flex-1 flex flex-col h-full relative transition-all duration-300 ease-in-out`}>
        {activeView === 'chat' ? (
          <ChatArea 
            messages={messages} 
            isTyping={isTyping}
            uploadingFiles={uploadingFiles}
            onSendMessage={sendMessage} 
            onConfirmIntent={handleConfirmIntent}
            messagesEndRef={messagesEndRef}
            sidebarOpen={sidebarOpen}
            toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />
        ) : (
          <Dashboard />
        )}
      </main>
    </div>
  );
}

export default App;

