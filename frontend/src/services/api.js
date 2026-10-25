// Base URL for the backend.
//  - In local dev, leave VITE_API_BASE_URL empty → uses the Vite proxy (/api → localhost:5000).
//  - In production (Vercel), set VITE_API_BASE_URL to the Render backend origin,
//    e.g. https://freshcatch-api.onrender.com  (no trailing slash, no /api).
import { firebaseAuth } from './firebase';

export const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const API_BASE = `${API_ORIGIN}/api`;

/**
 * Builds an absolute URL for a media path served by the backend
 * (uploaded images at /uploads/... and dataset images at /dataset/...).
 * Relative paths are prefixed with the backend origin so images load
 * from Render in production instead of the Vercel static domain.
 */
export function mediaUrl(pathOrUrl) {
  if (!pathOrUrl) return pathOrUrl;
  // Already absolute (http/https/data URI) → return as-is.
  if (/^(https?:|data:|blob:)/i.test(pathOrUrl)) return pathOrUrl;
  const clean = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`;
  return `${API_ORIGIN}${clean}`;
}

class ApiService {
  static async getHeaders(isMultipart = false) {
    const token = firebaseAuth.currentUser
      ? await firebaseAuth.currentUser.getIdToken()
      : localStorage.getItem('freshcatch_token');
    const headers = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  static async request(endpoint, options = {}) {
    const isMultipart = options.body instanceof FormData;
    const headers = { ...await this.getHeaders(isMultipart), ...options.headers };

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      const data = await response.json();
      if (!response.ok) {
        const err = new Error(data.message || `Request failed with status ${response.status}`);
        err.status = response.status;
        err.body = data;              // preserve full structured response (not_fish, quality_check, reasons)
        throw err;
      }
      return data;
    } catch (err) {
      console.error(`API Error on [${endpoint}]:`, err);
      throw err;
    }
  }

  // Auth Endpoints
  static login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
  }

  static register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  static getProfile() {
    return this.request('/auth/profile');
  }

  static updateProfile(profileData) {
    return this.request('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  }

  static listUsers() {
    return this.request('/auth/users');
  }

  static updateUserRole(userId, role) {
    return this.request(`/auth/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role })
    });
  }

  // Prediction Endpoints
  static analyzeImage(formDataOrBase64) {
    if (formDataOrBase64 instanceof FormData) {
      return this.request('/predict', {
        method: 'POST',
        body: formDataOrBase64
      });
    } else {
      return this.request('/predict', {
        method: 'POST',
        body: JSON.stringify({ image_data: formDataOrBase64 })
      });
    }
  }

  static getPredictions(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/predictions${query ? '?' + query : ''}`);
  }

  static getRecentPredictions() {
    return this.request('/predictions/recent');
  }

  static getPredictionById(id) {
    return this.request(`/predictions/${id}`);
  }

  // Recipe suggestions (live from TheMealDB, freshness-filtered)
  static getRecipes(classification, species = '', limit = 6) {
    const params = new URLSearchParams({ classification, limit: String(limit) });
    if (species) params.set('species', species);
    return this.request(`/recipes?${params.toString()}`);
  }

  // Vendor Stalls (freshness reputation layer)
  static getStalls() {
    return this.request('/stalls');
  }

  static getStallById(id) {
    return this.request(`/stalls/${id}`);
  }

  static getMyStall() {
    return this.request('/stalls/me/mine');
  }

  static createStall(stallData) {
    return this.request('/stalls', {
      method: 'POST',
      body: JSON.stringify(stallData)
    });
  }

  static updateStall(id, stallData) {
    return this.request(`/stalls/${id}`, {
      method: 'PUT',
      body: JSON.stringify(stallData)
    });
  }

  static deletePrediction(id) {
    return this.request(`/predictions/${id}`, {
      method: 'DELETE'
    });
  }

  // Fish Species & Categories
  static getSpecies() {
    return this.request('/fish-species');
  }

  static createSpecies(speciesData) {
    return this.request('/fish-species', {
      method: 'POST',
      body: JSON.stringify(speciesData)
    });
  }

  static getCategories() {
    return this.request('/freshness-categories');
  }

  static updateCategory(id, categoryData) {
    return this.request(`/freshness-categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(categoryData)
    });
  }

  // Dataset Endpoints
  static getDataset(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/dataset${query ? '?' + query : ''}`);
  }

  static getDatasetStats() {
    return this.request('/dataset/stats');
  }

  static uploadDatasetImage(formData) {
    return this.request('/dataset', {
      method: 'POST',
      body: formData
    });
  }

  static updateDatasetImage(id, data) {
    return this.request(`/dataset/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  static deleteDatasetImage(id) {
    return this.request(`/dataset/${id}`, {
      method: 'DELETE'
    });
  }

  // Models & Evaluation Endpoints
  static getModels() {
    return this.request('/models');
  }

  static getActiveModel() {
    return this.request('/models/active');
  }

  static activateModel(id) {
    return this.request(`/models/activate/${id}`, {
      method: 'POST'
    });
  }

  static trainModel() {
    return this.request('/models/train', {
      method: 'POST'
    });
  }

  static getEvaluationMetrics() {
    return this.request('/evaluation');
  }

  static getTrainingHistory() {
    return this.request('/evaluation/history');
  }

  static getEnvironmentalBenchmarks() {
    return this.request('/environmental-testing');
  }

  // Reports & Error Analysis
  static getErrorAnalysis() {
    return this.request('/error-analysis');
  }

  static addResearcherReview(reviewData) {
    return this.request('/error-analysis/review', {
      method: 'POST',
      body: JSON.stringify(reviewData)
    });
  }

  static getStatistics() {
    return this.request('/statistics');
  }

  static exportReportUrl(type = 'predictions', format = 'csv') {
    const token = localStorage.getItem('freshcatch_token') || '';
    return `${API_ORIGIN}/api/reports/export?type=${type}&format=${format}&token=${token}`;
  }
}

export default ApiService;
