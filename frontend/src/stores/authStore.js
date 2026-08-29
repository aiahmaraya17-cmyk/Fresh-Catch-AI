import { defineStore } from 'pinia';
import ApiService from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('freshcatch_token') || null,
    language: localStorage.getItem('freshcatch_lang') || 'en',
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    isResearcher: (state) => state.user?.role === 'researcher' || state.user?.role === 'admin',
    isVendor: (state) => state.user?.role === 'vendor',
    userName: (state) => state.user?.name || 'Guest User',
    userRole: (state) => state.user?.role || 'guest'
  },

  actions: {
    async initialize() {
      if (this.token) {
        try {
          this.isLoading = true;
          const res = await ApiService.getProfile();
          if (res.success) {
            this.user = res.user;
          } else {
            this.logout();
          }
        } catch (err) {
          console.warn('Failed to restore session:', err);
          this.logout();
        } finally {
          this.isLoading = false;
        }
      }
    },

    async login(email, password) {
      this.isLoading = true;
      this.error = null;
      try {
        const res = await ApiService.login({ email, password });
        if (res.success) {
          this.token = res.token;
          this.user = res.user;
          localStorage.setItem('freshcatch_token', res.token);
          return { success: true };
        }
        throw new Error(res.message || 'Login failed');
      } catch (err) {
        this.error = err.message;
        return { success: false, message: err.message };
      } finally {
        this.isLoading = false;
      }
    },

    async register(name, email, password, role) {
      this.isLoading = true;
      this.error = null;
      try {
        const res = await ApiService.register({ name, email, password, role });
        if (res.success) {
          this.token = res.token;
          this.user = res.user;
          localStorage.setItem('freshcatch_token', res.token);
          return { success: true };
        }
        throw new Error(res.message || 'Registration failed');
      } catch (err) {
        this.error = err.message;
        return { success: false, message: err.message };
      } finally {
        this.isLoading = false;
      }
    },

    logout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('freshcatch_token');
    },

    setLanguage(lang) {
      this.language = lang;
      localStorage.setItem('freshcatch_lang', lang);
    }
  }
});
