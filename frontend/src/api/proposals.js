/**
 * Proposals API
 */
import apiClient from './client';

export const proposalsAPI = {
  /**
   * Get proposal by ID
   */
  getProposal: async (proposalId) => {
    const response = await apiClient.get(`/proposals/${proposalId}`);
    return response.data;
  },

  /**
   * List proposals for session
   */
  listSessionProposals: async (sessionId, skip = 0, limit = 50) => {
    const response = await apiClient.get(`/proposals/sessions/${sessionId}/proposals`, {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Confirm proposal
   */
  confirmProposal: async (proposalId, userResponse = null) => {
    const response = await apiClient.post(`/proposals/${proposalId}/confirm`, {
      user_response: userResponse,
    });
    return response.data;
  },

  /**
   * Reject proposal
   */
  rejectProposal: async (proposalId, reason = null) => {
    const response = await apiClient.post(`/proposals/${proposalId}/reject`, {
      reason,
    });
    return response.data;
  },
};

export default proposalsAPI;
