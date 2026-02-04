/**
 * Chat/Session API
 */
import apiClient from './client';

export const chatAPI = {
  /**
   * Create new session
   */
  createSession: async (domainPackId, metadata = {}) => {
    const response = await apiClient.post('/chat/sessions', {
      domain_pack_id: domainPackId,
      metadata,
    });
    return response.data;
  },

  /**
   * Get all sessions
   */
  getSessions: async () => {
    const response = await apiClient.get('/chat/sessions');
    return response.data;
  },

  /**
   * Get session by ID
   */
  getSession: async (sessionId) => {
    const response = await apiClient.get(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  /**
   * Send message in session
   */
  sendMessage: async (sessionId, message, domainPackId) => {
    const response = await apiClient.post(`/chat/sessions/${sessionId}/messages`, {
      message,
      domain_pack_id: domainPackId,
    });
    return response.data;
  },
};

export default chatAPI;
