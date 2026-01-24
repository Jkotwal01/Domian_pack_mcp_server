import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { useChat } from './hooks/useChat';
import { useChatSessions } from './hooks/useChatSessions';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
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

  const { messages, isTyping, uploadingFiles, sendMessage, messagesEndRef } = useChat(
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
    }
  );

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen} 
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onNewChat={addSession}
        onSelectSession={switchSession}
        onDeleteSession={deleteSession}
        onRenameSession={renameSession}
      />
      
      {/* Main Content */}
      <main className={`flex-1 flex flex-col h-full relative transition-all duration-300 ease-in-out`}>
         <ChatArea 
           messages={messages} 
           isTyping={isTyping}
           uploadingFiles={uploadingFiles}
           onSendMessage={sendMessage} 
           messagesEndRef={messagesEndRef}
           sidebarOpen={sidebarOpen}
           toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
         />
      </main>
    </div>
  );
}

export default App;
