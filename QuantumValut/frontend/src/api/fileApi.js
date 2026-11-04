/**
 * File API Layer
 * Handles all HTTP requests to the backend file endpoints
 * Follows the same pattern as authApi.js
 */

import axiosInstance from './axios';

export const fileApi = {
  /**
   * Upload a file to QuantumVault
   * @param {File} file - File object from input
   * @param {string} folderId - Target folder ID (optional)
   * @param {string} description - File description (optional)
   * @param {boolean} isFavorite - Mark as favorite (optional)
   * @returns {Promise} File response with metadata
   */
  uploadFile: async (file, folderId = null, description = null, isFavorite = false) => {
    const formData = new FormData();
    formData.append('file', file);
    if (folderId) formData.append('folder_id', folderId);
    if (description) formData.append('description', description);
    formData.append('is_favorite', isFavorite);

    const response = await axiosInstance.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Get file details by ID
   * @param {string} fileId - File ID
   * @returns {Promise} File metadata
   */
  getFileById: async (fileId) => {
    const response = await axiosInstance.get(`/files/${fileId}`);
    return response.data;
  },

  /**
   * Preview a file inline
   * @param {string} fileId - File ID
   * @returns {Promise} File response blob
   */
  previewFile: async (fileId) => {
    const response = await axiosInstance.get(`/files/${fileId}/preview`, {
      responseType: 'blob',
    });
    return response;
  },

  /**
   * Download a file
   * @param {string} fileId - File ID
   * @returns {Promise} File content
   */
  downloadFile: async (fileId) => {
    const response = await axiosInstance.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    });
    return response;
  },

  /**
   * Delete a file (soft delete)
   * @param {string} fileId - File ID
   * @returns {Promise} Success response
   */
  deleteFile: async (fileId) => {
    const response = await axiosInstance.delete(`/files/${fileId}`);
    return response.data;
  },

  /**
   * Rename a file
   * @param {string} fileId - File ID
   * @param {string} newFilename - New filename
   * @returns {Promise} Updated file metadata
   */
  renameFile: async (fileId, newFilename) => {
    const response = await axiosInstance.patch(`/files/${fileId}/rename`, {
      new_filename: newFilename,
    });
    return response.data;
  },

  /**
   * Move file to another folder
   * @param {string} fileId - File ID
   * @param {string|null} newFolderId - Target folder ID (null for root)
   * @returns {Promise} Updated file metadata
   */
  moveFile: async (fileId, newFolderId = null) => {
    const response = await axiosInstance.patch(`/files/${fileId}/move`, {
      folder_id: newFolderId,
      new_folder_id: newFolderId,
    });
    return response.data;
  },

  /**
   * Toggle file favorite status
   * @param {string} fileId - File ID
   * @returns {Promise} Updated file metadata
   */
  toggleFavorite: async (fileId) => {
    const response = await axiosInstance.patch(`/files/${fileId}/favorite`);
    return response.data;
  },

  /**
   * List files in a folder with pagination
   * @param {string|null} folderId - Folder ID (null for root)
   * @param {number} page - Page number
   * @param {number} pageSize - Items per page
   * @returns {Promise} Paginated file list
   */
  listFolderFiles: async (folderId = null, page = 1, pageSize = 20) => {
    const response = await axiosInstance.get('/files/folder/' + (folderId || 'null'), {
      params: {
        page,
        page_size: pageSize,
      },
    });
    return response.data;
  },

  /**
   * Search files by filename
   * @param {string} query - Search query
   * @param {number} page - Page number
   * @param {number} pageSize - Items per page
   * @returns {Promise} Search results
   */
  searchFiles: async (query, page = 1, pageSize = 20) => {
    const response = await axiosInstance.get('/files/search/files', {
      params: {
        query,
        page,
        page_size: pageSize,
      },
    });
    return response.data;
  },

  /**
   * Get recently uploaded files
   * @param {number} limit - Number of recent files
   * @returns {Promise} List of recent files
   */
  getRecentFiles: async (limit = 10) => {
    const response = await axiosInstance.get('/dashboard/recent-files');
    return response.data;
  },

  /**
   * Get storage usage statistics
   * @returns {Promise} Storage stats including quota and used space
   */
  getStorageStats: async () => {
    const response = await axiosInstance.get('/files/stats/storage');
    return response.data;
  },

  /**
   * Restore a soft-deleted file
   * @param {string} fileId - File ID of deleted file
   * @returns {Promise} Restored file metadata
   */
  restoreFile: async (fileId) => {
    const response = await axiosInstance.post(`/files/${fileId}/restore`);
    return response.data;
  },
};
