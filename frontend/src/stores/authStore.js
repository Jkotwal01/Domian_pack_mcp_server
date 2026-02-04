/**
 * Authentication Store
 * Manages user authentication state
 */
import { create } from 'zustand';
import { authAPI } from '../api/auth';

const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authAPI.login(email, password);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      // Get user info
      const user = await authAPI.getCurrentUser();
      
      set({
        user,
        token: data.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
      
      return { success: true };
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      });
      return { success: false, error: error.response?.data?.detail };
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      await authAPI.register(userData);
      set({ isLoading: false });
      return { success: true };
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      });
      return { success: false, error: error.response?.data?.detail };
    }
  },

  logout: () => {
    authAPI.logout();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  loadUser: async () => {
    if (!get().token) return;
    
    set({ isLoading: true });
    try {
      const user = await authAPI.getCurrentUser();
      set({ user, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      get().logout();
    }
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
