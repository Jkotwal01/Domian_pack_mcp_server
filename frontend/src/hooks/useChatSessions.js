import { useState, useEffect } from 'react';

const STORAGE_KEY = 'chat_sessions';

export const useChatSessions = () => {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);

  // Load sessions from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setSessions(parsed);
        // Set the most recent session as active
        if (parsed.length > 0) {
          setActiveSessionId(parsed[0].id);
        }
      } catch (error) {
        console.error('Failed to parse sessions:', error);
        initializeDefaultSession();
      }
    } else {
      initializeDefaultSession();
    }
  }, []);

  // Save sessions to localStorage whenever they change
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    }
  }, [sessions]);

  const initializeDefaultSession = () => {
    const defaultSession = createNewSession();
    setSessions([defaultSession]);
    setActiveSessionId(defaultSession.id);
  };

  const createNewSession = (title = 'New Chat') => {
    // Generate a temporary ID for frontend tracking
    // The actual MCP session ID will come from the backend
    const tempId = `temp_${Date.now()}`;
    return {
      id: tempId,
      mcpSessionId: null,  // This will be the REAL ChatSession database ID
      domainConfigId: null, // The ID of the DomainConfig being worked on
      title,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  };

  const addSession = (initialData = {}) => {
    const newSession = {
      ...createNewSession(initialData.title || 'New Chat'),
      ...initialData
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    return newSession.id;
  };

  const deleteSession = (sessionId) => {
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== sessionId);
      // If we deleted the active session, switch to the first available
      if (sessionId === activeSessionId && filtered.length > 0) {
        setActiveSessionId(filtered[0].id);
      }
      return filtered;
    });
  };

  const renameSession = (sessionId, newTitle) => {
    setSessions(prev =>
      prev.map(s =>
        s.id === sessionId
          ? { ...s, title: newTitle, updatedAt: new Date().toISOString() }
          : s
      )
    );
  };

  const updateSessionMessages = (sessionId, messages) => {
    setSessions(prev => {
      const updated = prev.map(s =>
        s.id === sessionId
          ? { 
              ...s, 
              messages, 
              updatedAt: new Date().toISOString(),
              // Auto-generate title from first user message if still "New Chat"
              title: s.title === 'New Chat' && messages.length > 0 && messages[0].role === 'user'
                ? messages[0].content.substring(0, 50) + (messages[0].content.length > 50 ? '...' : '')
                : s.title === 'New Chat' && messages.length > 1 && messages[1].role === 'user'
                ? messages[1].content.substring(0, 50) + (messages[1].content.length > 50 ? '...' : '')
                : s.title
            }
          : s
      );
      
      // Sort by updatedAt (most recent first)
      return updated.sort((a, b) => 
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      );
    });
  };

  const switchSession = (sessionId) => {
    setActiveSessionId(sessionId);
  };

  const updateMcpSessionId = (sessionId, mcpSessionId) => {
    setSessions(prev =>
      prev.map(s =>
        s.id === sessionId
          ? { ...s, mcpSessionId }
          : s
      )
    );
  };

  const getActiveSession = () => {
    return sessions.find(s => s.id === activeSessionId);
  };

  return {
    sessions,
    activeSessionId,
    activeSession: getActiveSession(),
    addSession,
    deleteSession,
    renameSession,
    updateSessionMessages,
    updateMcpSessionId,
    switchSession
  };
};
