import { defineStore } from 'pinia';
import ApiService from '../services/api';

export const useDatasetStore = defineStore('dataset', {
  state: () => ({
    images: [],
    stats: null,
    isLoading: false,
    error: null,
    total: 0
  }),

  actions: {
    async fetchDataset(params = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const res = await ApiService.getDataset(params);
        if (res.success) {
          this.images = res.images || [];
          this.total = res.total || this.images.length;
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchStats() {
      try {
        const res = await ApiService.getDatasetStats();
        if (res.success) {
          this.stats = res.stats;
        }
      } catch (err) {
        this.error = err.message;
      }
    },

    async deleteImage(id) {
      try {
        const res = await ApiService.deleteDatasetImage(id);
        if (res.success) {
          this.images = this.images.filter(img => img.id !== id);
        }
        return res;
      } catch (err) {
        this.error = err.message;
        throw err;
      }
    }
  }
});
