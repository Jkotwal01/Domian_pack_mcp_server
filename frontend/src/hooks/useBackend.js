import { useState, useEffect } from 'react';
import { 
  sendChatIntent, 
  confirmChatIntent, 
  checkHealth,
  createSession 
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
   * Start a new session if none exists
   */
  const ensureSession = async (sessionId, initialContent = "{}", file = null) => {
    // If no ID or if it's a frontend-only temporary ID, create a real session
    if (!sessionId || sessionId.startsWith('temp_')) {
      try {
        const data = await createSession(file || initialContent, 'yaml', { source: 'frontend' });
        return data.session_id;
      } catch (err) {
        setError("Failed to create session: " + err.message);
        return null;
      }
    }
    return sessionId;
  };

  /**
   * Send a message to the backend and get an intent or suggestion
   */
  const getIntent = async (message, sessionId, file = null) => {
    try {
      // Ensure we have a session
      const validSessionId = await ensureSession(sessionId, "{}", file);
      if (!validSessionId) throw new Error("Could not initialize session");

      const result = await sendChatIntent(validSessionId, message);
      setError(null);
      return {
        ...result,
        sessionId: validSessionId
      };
    } catch (err) {
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

  return {
    isConnected,
    error,
    getIntent,
    confirmIntent,
    connect: checkBackendHealth
  };
};
