import { useState, useEffect } from 'react';
import { 
  sendChatIntent, 
  confirmChatIntent, 
  checkHealth,
  createSession,
  createChatSession,
  deleteChatSession
} from '../services/api';

/**
 * Hook for integrating with Domain Pack Backend v1
 */
export const useBackend = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  /**
   * Check if backend is healthy
   */
  const checkBackendHealth = async () => {
    try {
      const health = await checkHealth();
      if (health.status === 'healthy') {
        setIsConnected(true);
        setError(null);
      } else {
        setIsConnected(false);
        setError(health.error || 'Backend is not healthy');
      }
    } catch (err) {
      setIsConnected(false);
      setError(err.message);
    }
  };

  /**
   * Start a new chat session if none exists for the given domain
   */
  const ensureSession = async (domainConfigId) => {
    console.log('[useBackend] ensureSession called with domainConfigId:', domainConfigId);
    if (domainConfigId) {
      try {
        const data = await createChatSession(domainConfigId);
        console.log('[useBackend] session created/retrieved:', data);
        return data.id; 
      } catch (err) {
        console.error('[useBackend] Failed to create chat session:', err);
        setError("Failed to create chat session: " + err.message);
        return null;
      }
    }
    console.warn('[useBackend] No domainConfigId provided to ensureSession');
    return null;
  };

  /**
   * Send a message to the backend and get an intent or suggestion
   */
  const getIntent = async (message, domainConfigId) => {
    console.log('[useBackend] getIntent called:', { message, domainConfigId });
    try {
      const chatSessionId = await ensureSession(domainConfigId);
      if (!chatSessionId) throw new Error("Could not initialize chat session");

      console.log('[useBackend] sending message to session:', chatSessionId);
      const result = await sendChatIntent(chatSessionId, message);
      setError(null);
      return {
        ...result,
        sessionId: chatSessionId
      };
    } catch (err) {
      console.error('[useBackend] getIntent error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  /**
   * Confirm and apply a proposed intent
   */
  const confirmIntent = async (sessionId, intentId, approved = true) => {
    try {
      const result = await confirmChatIntent(sessionId, intentId, approved);
      setError(null);
      return result;
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      await deleteChatSession(sessionId);
      setError(null);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  return {
    isConnected,
    error,
    getIntent,
    confirmIntent,
    deleteSession,
    connect: checkBackendHealth
  };
};
