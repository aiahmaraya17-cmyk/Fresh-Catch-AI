<template>
  <div class="models-view container">
    <div class="page-header flex-between">
      <div>
        <span class="badge badge-cyan">CNN Architecture Registry</span>
        <h1>Model Registry & Training Hub</h1>
        <p class="subtitle">Manage transfer-learning CNN versions, track checkpoints, and trigger pipeline training</p>
      </div>
      <button @click="triggerTraining" class="btn btn-primary btn-sm" :disabled="isTraining">
        <span v-if="isTraining">Training Pipeline in Progress...</span>
        <span v-else>⚡ Train New CNN Model</span>
      </button>
    </div>

    <!-- Active Model Highlight Banner -->
    <div v-if="activeModel" class="glass-card active-model-banner mb-4">
      <div class="banner-badge-row">
        <span class="badge badge-fresh">Active Production Model</span>
        <span class="tflite-pill">✓ Mobile-Ready Export</span>
      </div>
      <div class="banner-body">
        <div class="banner-left">
          <h2>{{ activeModel.model_name }}</h2>
          <span class="model-code">{{ activeModel.version }}</span>
          <p class="arch-desc">{{ activeModel.architecture }} with GlobalAveragePooling2D, Batch Normalization, and Softmax Head.</p>
        </div>
        <div class="banner-metrics">
          <div class="b-stat">
            <span class="b-num text-emerald">{{ (activeModel.accuracy * 100).toFixed(1) }}%</span>
            <span class="b-lbl">Accuracy</span>
          </div>
          <div class="b-stat">
            <span class="b-num text-cyan">{{ (activeModel.f1_score * 100).toFixed(1) }}%</span>
            <span class="b-lbl">F1-Score</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Training Terminal Logs Box if Training -->
    <div v-if="trainingLogs" class="glass-card terminal-box mb-4">
      <div class="terminal-header">
        <span>CNN Pipeline Terminal Output</span>
        <span class="text-cyan">Python Execution Logs</span>
      </div>
      <pre class="terminal-code">{{ trainingLogs }}</pre>
    </div>

    <!-- Models List Table -->
    <div class="glass-card table-card">
      <h3>Model Versions History</h3>
      <table class="models-table">
        <thead>
          <tr>
            <th>Version Tag</th>
            <th>Architecture</th>
            <th>Test Accuracy</th>
            <th>Macro F1</th>
            <th>Status</th>
            <th>Created</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in modelsList" :key="m.id">
            <td>
              <strong>{{ m.version }}</strong>
            </td>
            <td>{{ m.architecture }}</td>
            <td class="text-emerald font-bold">{{ (m.accuracy * 100).toFixed(1) }}%</td>
            <td>{{ (m.f1_score * 100).toFixed(1) }}%</td>
            <td>
              <span class="badge" :class="m.status === 'active' ? 'badge-fresh' : 'badge-less-fresh'">
                {{ m.status.toUpperCase() }}
              </span>
            </td>
            <td class="text-dim">{{ formatDate(m.created_at) }}</td>
            <td>
              <button 
                v-if="m.status !== 'active'" 
                @click="activateModel(m.id)" 
                class="btn btn-outline btn-sm"
              >
                Set Active
              </button>
              <span v-else class="text-emerald font-bold text-sm">Active</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '../../services/api';

const modelsList = ref([]);
const activeModel = ref(null);
const isTraining = ref(false);
const trainingLogs = ref('');

function formatDate(dStr) {
  if (!dStr) return '';
  return new Date(dStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

async function loadModels() {
  try {
    const res = await ApiService.getModels();
    if (res.success) {
      modelsList.value = res.models || [];
      activeModel.value = modelsList.value.find(m => m.status === 'active') || modelsList.value[0];
    }
  } catch (e) {
    console.error('Failed to load models:', e);
  }
}

async function activateModel(id) {
  try {
    const res = await ApiService.activateModel(id);
    if (res.success) {
      await loadModels();
    }
  } catch (e) {
    alert('Error activating model: ' + e.message);
  }
}

async function triggerTraining() {
  isTraining.value = true;
  trainingLogs.value = '>>> Spawning Python CNN training pipeline on Roxas wet market dataset...\n>>> Applying stratified 70/15/15 split & anti-leakage filters...\n';
  try {
    const res = await ApiService.trainModel();
    if (res.success) {
      trainingLogs.value += res.trainOutput + '\n' + res.evalOutput + '\n>>> Model checkpoint saved successfully!';
      await loadModels();
    }
  } catch (e) {
    trainingLogs.value += '\n[ERROR] ' + e.message;
  } finally {
    isTraining.value = false;
  }
}

onMounted(() => {
  loadModels();
});
</script>

<style scoped>
.models-view {
  padding: clamp(1.5rem, 4vw, 3rem) 1.25rem;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.flex-between > div { flex: 1; min-width: 0; }

.flex-between h1 {
  font-size: clamp(1.35rem, 4vw, 2rem);
}

.active-model-banner {
  padding: clamp(1.25rem, 3vw, 2rem);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(20, 184, 166, 0.08));
}

.banner-badge-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.tflite-pill {
  background: rgba(20, 184, 166, 0.15);
  color: var(--accent-teal);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  border: 1px solid rgba(20, 184, 166, 0.3);
}

.banner-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .banner-body {
    flex-direction: column;
    align-items: flex-start;
  }
}

.banner-left h2 {
  font-size: clamp(1.1rem, 3vw, 1.6rem);
  margin-bottom: 0.2rem;
}

.model-code {
  font-size: 0.85rem;
  color: var(--primary);
  font-weight: 600;
}

.arch-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 0.4rem;
}

.banner-metrics {
  display: flex;
  gap: 2rem;
}

.b-stat { text-align: center; }
.b-num  { font-size: clamp(1.2rem, 4vw, 1.8rem); font-weight: 800; font-family: var(--font-heading); display: block; }
.b-lbl  { font-size: 0.75rem; color: var(--text-dim); }

.terminal-box {
  background: #020617;
  border: 1px solid rgba(14, 165, 233, 0.3);
  padding: 1.25rem;
  border-radius: var(--radius-sm);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.5rem;
}

.terminal-code {
  font-family: monospace;
  font-size: 0.82rem;
  color: #38bdf8;
  white-space: pre-wrap;
  max-height: 220px;
  overflow-y: auto;
}

/* Table card scrolls horizontally */
.table-card {
  padding: 1.75rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-card h3 {
  font-size: 1.2rem;
  margin-bottom: 1.25rem;
}

.models-table {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  font-size: 0.88rem;
  text-align: left;
}

.models-table th {
  padding: 0.75rem 1rem;
  color: var(--text-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-glass);
  white-space: nowrap;
}

.models-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  vertical-align: middle;
  white-space: nowrap;
}

.mb-4 { margin-bottom: 2rem; }
.text-emerald { color: var(--color-fresh); }
.text-cyan    { color: var(--primary); }
</style>
