import { defineStore } from 'pinia';
import ApiService from '../services/api';

export const usePredictionStore = defineStore('prediction', {
  state: () => ({
    predictions: [],
    currentResult: null,
    isLoading: false,
    error: null,
    total: 0
  }),

  getters: {
    hasPredictions: (state) => state.predictions.length > 0
  },

  actions: {
    async fetchPredictions(params = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const res = await ApiService.getPredictions(params);
        if (res.success) {
          this.predictions = res.predictions || [];
          this.total = res.total || this.predictions.length;
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchById(id) {
      this.isLoading = true;
      try {
        const res = await ApiService.getPredictionById(id);
        if (res.success) {
          this.currentResult = res.prediction;
          return res.prediction;
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.isLoading = false;
      }
    },

    setCurrentResult(result) {
      this.currentResult = result;
    },

    async deletePrediction(id) {
      try {
        const res = await ApiService.deletePrediction(id);
        if (res.success) {
          this.predictions = this.predictions.filter(p => p.id !== id);
        }
        return res;
      } catch (err) {
        this.error = err.message;
        throw err;
      }
    }
  }
});
