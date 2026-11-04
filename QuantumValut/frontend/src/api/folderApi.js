import axiosInstance from './axios';

export const folderApi = {
  getRootFolders: async () => {
    const response = await axiosInstance.get('/folders/root');
    return response.data;
  },

  getFolderContents: async (folderId) => {
    const response = await axiosInstance.get(`/folders/${folderId}/contents`);
    return response.data;
  },

  createFolder: async (folderData) => {
    const response = await axiosInstance.post('/folders', folderData);
    return response.data;
  },

  deleteFolder: async (folderId) => {
    const response = await axiosInstance.delete(`/folders/${folderId}`);
    return response.data;
  },
};
