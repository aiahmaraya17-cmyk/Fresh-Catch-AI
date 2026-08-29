<template>
  <div class="settings-admin-view container container-narrow">
    <div class="page-header">
      <span class="badge badge-cyan">System Diagnostics & Configuration</span>
      <h1>System Settings</h1>
      <p class="subtitle">Image quality thresholds, AI inference engine parameters, and API health monitoring</p>
    </div>

    <!-- API Health Status -->
    <div class="glass-card status-card mb-4">
      <div class="status-top">
        <div class="status-title">
          <div class="status-dot"></div>
          <h3>System Backend & AI Engine Operational</h3>
        </div>
        <span class="badge badge-fresh">Healthy</span>
      </div>
      <div class="status-meta-grid">
        <div class="m-item">
          <span class="m-lbl">Target Domain:</span>
          <span class="m-val">Roxas, Oriental Mindoro</span>
        </div>
        <div class="m-item">
          <span class="m-lbl">Active Architecture:</span>
          <span class="m-val text-cyan">MobileNetV2 CNN</span>
        </div>
        <div class="m-item">
          <span class="m-lbl">Backend Engine:</span>
          <span class="m-val">Node.js Express + SQLite3</span>
        </div>
        <div class="m-item">
          <span class="m-lbl">AI Runtime:</span>
          <span class="m-val">Python 3.12+ (Scikit-Learn, OpenCV)</span>
        </div>
      </div>
    </div>

    <!-- Threshold Settings Form -->
    <div class="glass-card form-card">
      <h3>Image Quality & Certainty Thresholds</h3>
      <form @submit.prevent="saveSettings" class="settings-form">
        <div class="form-group">
          <label>Minimum Sharpness / Laplacian Variance Threshold</label>
          <input v-model.number="settings.minBlurVar" type="number" step="1" class="input-field" />
          <span class="hint-text">Images with variance below this value will be flagged as out-of-focus blur.</span>
        </div>

        <div class="grid-2">
          <div class="form-group">
            <label>Min Luminance (HSV V-Channel)</label>
            <input v-model.number="settings.minBrightness" type="number" class="input-field" />
          </div>
          <div class="form-group">
            <label>Max Luminance (HSV V-Channel)</label>
            <input v-model.number="settings.maxBrightness" type="number" class="input-field" />
          </div>
        </div>

        <div class="form-group">
          <label>High Confidence Threshold</label>
          <input v-model.number="settings.highConfidenceThreshold" type="number" step="0.05" min="0.5" max="1.0" class="input-field" />
          <span class="hint-text">Minimum softmax probability required to report "High Certainty".</span>
        </div>

        <button type="submit" class="btn btn-primary btn-lg">
          Save Configuration
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const settings = ref({
  minBlurVar: 20,
  minBrightness: 25,
  maxBrightness: 240,
  highConfidenceThreshold: 0.85
});

function saveSettings() {
  localStorage.setItem('freshcatch_settings', JSON.stringify(settings.value));
  alert('System settings updated successfully!');
}
</script>

<style scoped>
.settings-admin-view {
  padding: clamp(1.5rem, 4vw, 3rem) 1.25rem;
}

.page-header {
  margin-bottom: 2.5rem;
}

.page-header h1 {
  font-size: clamp(1.4rem, 4vw, 2rem);
  margin: 0.5rem 0;
}

.status-card {
  padding: 1.75rem;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(14, 165, 233, 0.08));
}

.status-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.status-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.status-title h3 {
  font-size: clamp(0.88rem, 2.5vw, 1.1rem);
}

.status-dot {
  width: 12px;
  height: 12px;
  background: var(--color-fresh);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--color-fresh);
  flex-shrink: 0;
}

/* Single column on all screens ≤ 560px */
.status-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  font-size: 0.85rem;
}

@media (max-width: 560px) {
  .status-meta-grid {
    grid-template-columns: 1fr;
  }
}

.m-item {
  display: flex;
  flex-direction: column;
}

.m-lbl { color: var(--text-muted); font-size: 0.75rem; }
.m-val { font-weight: 600; color: var(--text-white); }
.text-cyan { color: var(--primary); }

.form-card {
  padding: clamp(1.25rem, 3vw, 2rem);
}

.form-card h3 {
  font-size: 1.25rem;
  margin-bottom: 1.25rem;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-white);
  margin-bottom: 0.35rem;
}

.hint-text {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-top: 0.25rem;
  display: block;
}

/* Stack the luminance grid on very narrow screens */
@media (max-width: 400px) {
  .settings-form .grid-2 {
    grid-template-columns: 1fr !important;
  }
}

.mb-4 { margin-bottom: 2rem; }
</style>
