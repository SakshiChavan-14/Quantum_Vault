import axiosInstance from './axios';

export const auditApi = {
  /**
   * Get audit logs for current user
   * @param {Object} params - Query params (limit, skip, category, status)
   * @returns {Promise} AuditLogListResponse
   */
  getMyAuditLogs: async (params = {}) => {
    const response = await axiosInstance.get('/audit/me', { params });
    return response.data;
  },

  /**
   * Get audit logs for a specific file
   * @param {string} fileId - Target file ID
   * @returns {Promise} List of audit logs
   */
  getFileAuditLogs: async (fileId) => {
    const response = await axiosInstance.get(`/audit/file/${fileId}`);
    return response.data;
  },
};
