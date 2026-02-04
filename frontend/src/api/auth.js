/**
 * Authentication API
 */
import apiClient from './client';

export const authAPI = {
  /**
   * Login user
   */
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email); // OAuth2 uses 'username' field
    formData.append('password', password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * Register new user
   */
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  /**
   * Get current user info
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  /**
   * Logout (client-side only)
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

export default authAPI;
