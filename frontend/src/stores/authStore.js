import { defineStore } from 'pinia';
import { onAuthStateChanged, signInWithEmailAndPassword, createUserWithEmailAndPassword, updateProfile, updatePassword, signOut } from 'firebase/auth';
import { firebaseAuth } from '../services/firebase';
import { getOrCreateUserProfile, updateUserProfile } from '../services/firebaseUsers';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('freshcatch_token') || null,
    language: localStorage.getItem('freshcatch_lang') || 'en',
    isLoading: false,
    initialized: false,
    error: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    isResearcher: (state) => ['researcher', 'admin'].includes(state.user?.role),
    isVendor: (state) => state.user?.role === 'vendor',
    userName: (state) => state.user?.name || 'Guest User',
    userRole: (state) => state.user?.role || 'guest'
  },
  actions: {
    async setFirebaseUser(firebaseUser, displayName = '') {
      if (!firebaseUser) {
        this.user = null;
        this.token = null;
        localStorage.removeItem('freshcatch_token');
        return;
      }
      const [token, profile] = await Promise.all([
        firebaseUser.getIdToken(), getOrCreateUserProfile(firebaseUser, displayName)
      ]);
      this.token = token;
      this.user = { id: firebaseUser.uid, ...profile };
      localStorage.setItem('freshcatch_token', token);
    },
    initialize() {
      if (this._authReady) return this._authReady;
      this._authReady = new Promise((resolve) => {
        onAuthStateChanged(firebaseAuth, async (firebaseUser) => {
          try {
            await this.setFirebaseUser(firebaseUser);
          } catch (error) {
            console.error('Could not load Firebase profile:', error);
            this.user = null;
            this.token = null;
            localStorage.removeItem('freshcatch_token');
          } finally {
            this.initialized = true;
            this.isLoading = false;
            resolve();
          }
        });
      });
      return this._authReady;
    },
    async login(email, password) {
      this.isLoading = true;
      this.error = null;
      try {
        const credential = await signInWithEmailAndPassword(firebaseAuth, email.trim(), password);
        await this.setFirebaseUser(credential.user);
        return { success: true };
      } catch (error) {
        this.error = error.message;
        return { success: false, message: error.message };
      } finally { this.isLoading = false; }
    },
    async register(name, email, password) {
      this.isLoading = true;
      this.error = null;
      try {
        const credential = await createUserWithEmailAndPassword(firebaseAuth, email.trim(), password);
        await updateProfile(credential.user, { displayName: name.trim() });
        await this.setFirebaseUser(credential.user, name.trim());
        return { success: true };
      } catch (error) {
        this.error = error.message;
        return { success: false, message: error.message };
      } finally { this.isLoading = false; }
    },
    async updateProfile(name, password) {
      const firebaseUser = firebaseAuth.currentUser;
      if (!firebaseUser) return { success: false, message: 'Please sign in again.' };
      try {
        if (name.trim() !== firebaseUser.displayName) await updateProfile(firebaseUser, { displayName: name.trim() });
        if (password) await updatePassword(firebaseUser, password);
        const profile = await updateUserProfile(firebaseUser, { name: name.trim() });
        this.user = { ...this.user, ...profile, name: name.trim() };
        return { success: true };
      } catch (error) { return { success: false, message: error.message }; }
    },
    async logout() {
      await signOut(firebaseAuth);
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
