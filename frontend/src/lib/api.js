import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5000/api'),
  timeout: 30000, // 30 seconds for video uploads
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post('/api/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  refresh: () => api.post('/auth/refresh'),
  getCurrentUser: () => api.get('/auth/me'),
  changePassword: (passwords) => api.post('/auth/change-password', passwords),
};

// Videos API
export const videosAPI = {
  getVideos: (params = {}) => api.get('/videos', { params }),
  getVideo: (id) => api.get(`/videos/${id}`),
  uploadVideo: (formData, onUploadProgress) => 
    api.post('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    }),
  updateVideo: (id, data) => api.put(`/videos/${id}`, data),
  deleteVideo: (id) => api.delete(`/videos/${id}`),
  getStreamUrl: (id, resolution = 'original') => 
    `${api.defaults.baseURL}/videos/${id}/stream/${resolution}`,
  getDownloadUrl: (id, resolution = 'original') => 
    `${api.defaults.baseURL}/videos/${id}/download/${resolution}`,
  getThumbnailUrl: (id) => 
    `${api.defaults.baseURL}/videos/${id}/thumbnail`,
};

// Categories API
export const categoriesAPI = {
  getCategories: () => api.get('/categories'),
  getCategory: (id) => api.get(`/categories/${id}`),
  createCategory: (data) => api.post('/categories', data),
  updateCategory: (id, data) => api.put(`/categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/categories/${id}`),
  toggleSharing: (id, isShared) => api.post(`/categories/${id}/share`, { is_shared: isShared }),
};

// Users API
export const usersAPI = {
  getUsers: (params = {}) => api.get('/users', { params }),
  getUser: (id) => api.get(`/users/${id}`),
  getUserStats: (id) => api.get(`/users/${id}/stats`),
  toggleUserStatus: (id) => api.post(`/users/${id}/toggle-status`),
  promoteUser: (id) => api.post(`/users/${id}/promote`),
  demoteUser: (id) => api.post(`/users/${id}/demote`),
  deleteUser: (id) => api.delete(`/users/${id}`),
};

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getSystemInfo: () => api.get('/admin/system-info'),
  cleanup: () => api.post('/admin/cleanup'),
  reprocessFailedVideos: () => api.post('/admin/reprocess-failed'),
  bulkShareCategories: (categoryIds, isShared) => 
    api.post('/admin/categories/bulk-share', { category_ids: categoryIds, is_shared: isShared }),
};

export default api;
