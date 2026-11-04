/**
 * File Service Layer
 * Wraps fileApi with business logic and state management
 * Handles file operations and transformations
 */

import { fileApi } from '../api/fileApi';
import toast from 'react-hot-toast';

export const fileService = {
  /**
   * Upload a file with error handling
   * @param {File} file - File object
   * @param {string} folderId - Target folder ID
   * @param {Object} metadata - Optional metadata (description, isFavorite)
   * @returns {Promise} Uploaded file data or null
   */
  uploadFile: async (file, folderId = null, metadata = {}) => {
    try {
      if (!file) {
        throw new Error('No file selected');
      }

      // Validate file size (100 MB limit)
      const MAX_SIZE = 100 * 1024 * 1024;
      if (file.size > MAX_SIZE) {
        throw new Error(`File size exceeds maximum limit (100 MB)`);
      }

      // Show loading toast
      const loadingToastId = toast.loading('Uploading file...');

      try {
        const result = await fileApi.uploadFile(
          file,
          folderId,
          metadata.description,
          metadata.isFavorite || false
        );

        toast.dismiss(loadingToastId);
        toast.success(`File "${file.name}" uploaded successfully`);
        return result;
      } catch (error) {
        toast.dismiss(loadingToastId);
        throw error;
      }
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'Upload failed';
      toast.error(message);
      console.error('Upload error:', error);
      return null;
    }
  },

  /**
   * Download a file
   * @param {string} fileId - File ID
   * @param {string} filename - Original filename for download
   */
  downloadFile: async (fileId, filename) => {
    try {
      const loadingToastId = toast.loading('Downloading...');

      const response = await fileApi.downloadFile(fileId);

      toast.dismiss(loadingToastId);

      // Create blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || 'download');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('File downloaded successfully');
    } catch (error) {
      toast.error(error.response?.data?.message || 'Download failed');
      console.error('Download error:', error);
    }
  },

  /**
   * Delete a file with confirmation
   * @param {string} fileId - File ID
   * @param {string} filename - Filename for confirmation message
   * @returns {Promise} Success boolean
   */
  deleteFile: async (fileId, filename) => {
    try {
      // In a real app, you might want a confirmation dialog here
      // For now, just delete
      const loadingToastId = toast.loading('Deleting file...');

      await fileApi.deleteFile(fileId);

      toast.dismiss(loadingToastId);
      toast.success(`"${filename}" deleted`);
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Deletion failed');
      console.error('Delete error:', error);
      return false;
    }
  },

  /**
   * Rename a file
   * @param {string} fileId - File ID
   * @param {string} newFilename - New filename
   * @returns {Promise} Updated file or null
   */
  renameFile: async (fileId, newFilename) => {
    try {
      const loadingToastId = toast.loading('Renaming file...');

      const result = await fileApi.renameFile(fileId, newFilename);

      toast.dismiss(loadingToastId);
      toast.success('File renamed successfully');
      return result;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Rename failed');
      console.error('Rename error:', error);
      return null;
    }
  },

  /**
   * Move file to another folder
   * @param {string} fileId - File ID
   * @param {string|null} newFolderId - Target folder ID
   * @returns {Promise} Updated file or null
   */
  moveFile: async (fileId, newFolderId) => {
    try {
      const loadingToastId = toast.loading('Moving file...');

      const result = await fileApi.moveFile(fileId, newFolderId);

      toast.dismiss(loadingToastId);
      toast.success('File moved successfully');
      return result;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Move failed');
      console.error('Move error:', error);
      return null;
    }
  },

  /**
   * Toggle file favorite status
   * @param {string} fileId - File ID
   * @returns {Promise} Updated file or null
   */
  toggleFavorite: async (fileId) => {
    try {
      const result = await fileApi.toggleFavorite(fileId);
      const action = result.is_favorite ? 'added to' : 'removed from';
      toast.success(`File ${action} favorites`);
      return result;
    } catch (error) {
      toast.error('Failed to update favorite status');
      console.error('Favorite toggle error:', error);
      return null;
    }
  },

  /**
   * List files in folder
   * @param {string|null} folderId - Folder ID
   * @param {number} page - Page number
   * @param {number} pageSize - Items per page
   * @returns {Promise} File list response
   */
  listFolderFiles: async (folderId = null, page = 1, pageSize = 20) => {
    try {
      return await fileApi.listFolderFiles(folderId, page, pageSize);
    } catch (error) {
      console.error('List files error:', error);
      toast.error('Failed to load files');
      return { items: [], total: 0, page, page_size: pageSize, total_pages: 0 };
    }
  },

  /**
   * Search for files
   * @param {string} query - Search query
   * @param {number} page - Page number
   * @param {number} pageSize - Items per page
   * @returns {Promise} Search results
   */
  searchFiles: async (query, page = 1, pageSize = 20) => {
    try {
      if (!query || query.trim().length === 0) {
        return { items: [], total: 0, page, page_size: pageSize, total_pages: 0 };
      }

      return await fileApi.searchFiles(query, page, pageSize);
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Search failed');
      return { items: [], total: 0, page, page_size: pageSize, total_pages: 0 };
    }
  },

  /**
   * Get recent files
   * @param {number} limit - Number of recent files
   * @returns {Promise} List of recent files
   */
  getRecentFiles: async (limit = 10) => {
    try {
      const data = await fileApi.getRecentFiles(limit);
      return Array.isArray(data) ? data : (data?.files || []);
    } catch (error) {
      console.error('Get recent files error:', error);
      return [];
    }
  },

  /**
   * Get storage statistics
   * @returns {Promise} Storage stats
   */
  getStorageStats: async () => {
    try {
      return await fileApi.getStorageStats();
    } catch (error) {
      console.error('Get storage stats error:', error);
      return {
        total_storage_bytes: 0,
        used_storage_bytes: 0,
        available_storage_bytes: 0,
        file_count: 0,
        percentage_used: 0,
      };
    }
  },

  /**
   * Restore a deleted file
   * @param {string} fileId - File ID
   * @param {string} filename - Filename for message
   * @returns {Promise} Restored file or null
   */
  restoreFile: async (fileId, filename) => {
    try {
      const loadingToastId = toast.loading('Restoring file...');

      const result = await fileApi.restoreFile(fileId);

      toast.dismiss(loadingToastId);
      toast.success(`"${filename}" restored successfully`);
      return result;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Restore failed');
      console.error('Restore error:', error);
      return null;
    }
  },

  /**
   * Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size (e.g., "2.5 MB")
   */
  formatFileSize: (bytes) => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  },

  /**
   * Get file icon based on MIME type or extension
   * @param {string} mimeType - MIME type
   * @param {string} extension - File extension
   * @returns {string} Icon name
   */
  getFileIcon: (mimeType, extension) => {
    const ext = extension?.toLowerCase() || '';

    // Documents
    if (ext === 'pdf' || mimeType?.includes('pdf')) return '📄';
    if (ext === 'doc' || ext === 'docx' || mimeType?.includes('word')) return '📝';
    if (ext === 'xls' || ext === 'xlsx' || mimeType?.includes('spreadsheet')) return '📊';
    if (ext === 'ppt' || ext === 'pptx' || mimeType?.includes('presentation')) return '🎬';

    // Images
    if (ext === 'jpg' || ext === 'jpeg' || ext === 'png' || ext === 'gif' || mimeType?.includes('image')) return '🖼️';

    // Videos
    if (ext === 'mp4' || ext === 'avi' || ext === 'mov' || mimeType?.includes('video')) return '🎥';

    // Audio
    if (ext === 'mp3' || ext === 'wav' || ext === 'flac' || mimeType?.includes('audio')) return '🎵';

    // Archives
    if (ext === 'zip' || ext === 'rar' || ext === '7z' || ext === 'tar' || ext === 'gz') return '📦';

    // Code
    if (ext === 'py' || ext === 'js' || ext === 'java' || ext === 'cpp' || ext === 'html' || ext === 'css') return '💻';

    // Text
    if (ext === 'txt' || mimeType?.includes('text')) return '📋';

    // Default
    return '📎';
  },

  /**
   * Format date for display
   * @param {string|Date} date - Date to format
   * @returns {string} Formatted date
   */
  formatDate: (date) => {
    const d = new Date(date);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (d.toDateString() === today.toDateString()) {
      return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }

    if (d.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    }

    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: d.getFullYear() !== today.getFullYear() ? 'numeric' : undefined });
  },
};
