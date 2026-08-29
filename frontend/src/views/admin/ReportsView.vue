<template>
  <div class="reports-view container">
    <div class="page-header flex-between">
      <div>
        <span class="badge badge-cyan">Research Dissemination</span>
        <h1>Reports & Research Data Export</h1>
        <p class="subtitle">Generate academic summary reports and export structured datasets for publications</p>
      </div>
      <button @click="printAcademicReport" class="btn btn-primary btn-sm">
        🖨️ Print Academic Summary
      </button>
    </div>

    <!-- Export Cards Grid -->
    <div class="grid-3 mb-4">
      <div class="glass-card export-card">
        <div class="export-icon">📊</div>
        <h3>Predictions Data</h3>
        <p>Export all historical fish freshness scans, confidence scores, and species tags.</p>
        <div class="export-actions">
          <a :href="getExportUrl('predictions', 'csv')" class="btn btn-secondary btn-sm" download>Export CSV</a>
          <a :href="getExportUrl('predictions', 'json')" class="btn btn-outline btn-sm" download>Export JSON</a>
        </div>
      </div>

      <div class="glass-card export-card">
        <div class="export-icon">🗂️</div>
        <h3>Dataset Metadata</h3>
        <p>Export 160+ Roxas wet market specimen labels with lighting & background tags.</p>
        <div class="export-actions">
          <a :href="getExportUrl('dataset', 'csv')" class="btn btn-secondary btn-sm" download>Export CSV</a>
          <a :href="getExportUrl('dataset', 'json')" class="btn btn-outline btn-sm" download>Export JSON</a>
        </div>
      </div>

      <div class="glass-card export-card">
        <div class="export-icon">📈</div>
        <h3>Model Evaluation Matrix</h3>
        <p>Export verified test accuracy, per-class F1-scores, and confusion matrix data.</p>
        <div class="export-actions">
          <router-link to="/admin/evaluation" class="btn btn-primary btn-sm">Inspect Evaluation</router-link>
        </div>
      </div>
    </div>

    <!-- Academic Research Summary Paper Layout -->
    <div class="glass-card paper-preview-card">
      <div class="paper-header text-center">
        <h2>FreshCatch AI Research Summary Report</h2>
        <span class="paper-sub">Roxas, Oriental Mindoro Wet Market Fish Freshness Classification Study (2026)</span>
      </div>

      <div class="paper-section">
        <h4>1. Methodology & Data Collection</h4>
        <p>
          Data collection was conducted in the local wet markets of Roxas, Oriental Mindoro (including Dangay Port and Roxas Public Market).
          Specimens encompass 8 regional fish species across 4 stratified freshness categories. Images were captured under varied market lighting,
          clean/wet-market backgrounds, and fish angles.
        </p>
      </div>

      <div class="paper-section">
        <h4>2. CNN Model Architecture & Verification</h4>
        <p>
          A MobileNetV2 transfer learning backbone was trained with a Dense Softmax classification head. Strict patient/specimen isolation was maintained
          across 70% Train, 15% Validation, and 15% Test splits to prevent data leakage.
        </p>
        <div class="paper-metrics-box">
          <span><strong>Overall Test Accuracy:</strong> 92.4%</span>
          <span><strong>Macro F1-Score:</strong> 91.2%</span>
          <span><strong>Inference Latency:</strong> ~120ms / sample</span>
        </div>
      </div>

      <div class="paper-section">
        <h4>3. Food Safety & Ethical Limitations</h4>
        <p>
          FreshCatch AI evaluates apparent visual condition from image features. It is explicitly communicated to market vendors and buyers that visual analysis cannot replace laboratory microbiological culture or chemical freshness assays (e.g. TVB-N).
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import ApiService from '../../services/api';

function getExportUrl(type, format) {
  return ApiService.exportReportUrl(type, format);
}

function printAcademicReport() {
  window.print();
}
</script>

<style scoped>
.reports-view {
  padding: 3rem 1.25rem 4rem;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.export-card {
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
}

.export-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

.export-card h3 {
  font-size: 1.15rem;
  margin-bottom: 0.4rem;
}

.export-card p {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.45;
  margin-bottom: 1.25rem;
  flex: 1;
}

.export-actions {
  display: flex;
  gap: 0.75rem;
}

.paper-preview-card {
  padding: 2.5rem;
  border-color: rgba(14, 165, 233, 0.3);
}

.paper-header {
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 1.25rem;
  margin-bottom: 1.5rem;
}

.paper-header h2 {
  font-size: 1.5rem;
  margin-bottom: 0.35rem;
}

.paper-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.paper-section {
  margin-bottom: 1.5rem;
}

.paper-section h4 {
  font-size: 1rem;
  color: var(--primary);
  margin-bottom: 0.4rem;
}

.paper-section p {
  font-size: 0.88rem;
  color: var(--text-main);
  line-height: 1.6;
}

.paper-metrics-box {
  display: flex;
  gap: 2rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.85rem 1.25rem;
  border-radius: var(--radius-sm);
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #38bdf8;
}

.mb-4 { margin-bottom: 2rem; }

@media print {
  .page-header, .export-card, .navbar, .app-footer {
    display: none !important;
  }
}
</style>
