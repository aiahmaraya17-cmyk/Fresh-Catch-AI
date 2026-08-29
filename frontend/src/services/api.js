const API_BASE = '/api';

class ApiService {
  static getHeaders(isMultipart = false) {
    const token = localStorage.getItem('freshcatch_token');
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
    const headers = { ...this.getHeaders(isMultipart), ...options.headers };

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || `Request failed with status ${response.status}`);
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
    return `/api/reports/export?type=${type}&format=${format}&token=${token}`;
  }
}

export default ApiService;
