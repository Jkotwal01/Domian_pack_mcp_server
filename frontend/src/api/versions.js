/**
 * Versions API
 */
import apiClient from './client';

export const versionsAPI = {
  /**
   * List versions for domain pack
   */
  listVersions: async (domainPackId, skip = 0, limit = 50) => {
    const response = await apiClient.get(`/versions/domain-packs/${domainPackId}/versions`, {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Get version by ID
   */
  getVersion: async (versionId) => {
    const response = await apiClient.get(`/versions/${versionId}`);
    return response.data;
  },

  /**
   * Get version diff
   */
  getVersionDiff: async (versionId) => {
    const response = await apiClient.get(`/versions/${versionId}/diff`);
    return response.data;
  },

  /**
   * Create rollback
   */
  createRollback: async (domainPackId, targetVersionId, reason = null) => {
    const response = await apiClient.post(`/versions/domain-packs/${domainPackId}/rollback`, {
      target_version_id: targetVersionId,
      reason,
    });
    return response.data;
  },
};

export default versionsAPI;
