import { useState, useEffect } from 'react';
import { sendChatMessage, callMCPTool, checkHealth } from '../services/api';

/**
 * Hook for integrating with MCP (Model Context Protocol) server via backend
 */
export const useMCPServer = () => {
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
   * Send a message to the backend/LLM and get tool calls
   * @param {string} message - The user message
   * @param {Array} files - Optional file attachments (not yet implemented in backend)
   * @param {string|null} sessionId - Optional session ID
   * @param {Array} conversationHistory - Previous messages
   * @returns {Promise<Object>} Response with tool calls
   */
  const sendToMCP = async (message, files = [], sessionId = null, conversationHistory = []) => {
    try {
      // Send chat message to backend
      const result = await sendChatMessage(message, files, sessionId, conversationHistory);

      if (!result.success) {
        setError(result.error);
        return {
          success: false,
          error: result.error,
          toolCalls: []
        };
      }

      setError(null);
      return {
        success: true,
        response: result.response,
        sessionId: result.sessionId,
        toolCalls: result.toolCalls || []
      };
    } catch (err) {
      setError(err.message);
      return {
        success: false,
        error: err.message,
        toolCalls: []
      };
    }
  };

  /**
   * Execute a specific MCP tool directly
   * @param {string} toolName - Name of the tool
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Tool execution result
   */
  const executeTool = async (toolName, args) => {
    try {
      const result = await callMCPTool(toolName, args);

      if (!result.success) {
        return {
          success: false,
          error: result.error
        };
      }

      return {
        success: true,
        output: `Tool "${toolName}" executed successfully`,
        data: result.result
      };
    } catch (err) {
      return {
        success: false,
        error: err.message
      };
    }
  };

  /**
   * Connect to backend (check health)
   */
  const connect = async () => {
    await checkBackendHealth();
  };

  /**
   * Disconnect from backend
   */
  const disconnect = () => {
    setIsConnected(false);
  };

  return {
    isConnected,
    error,
    sendToMCP,
    executeTool,
    connect,
    disconnect
  };
};

