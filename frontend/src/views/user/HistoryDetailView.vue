<template>
  <div class="history-detail-view container container-narrow">
    <div class="page-header flex-between">
      <router-link to="/history" class="btn btn-secondary btn-sm">
        &larr; Back to History
      </router-link>
      <button @click="printRecord" class="btn btn-outline btn-sm">
        🖨️ Print Slip
      </button>
    </div>

    <div v-if="prediction" class="glass-card detail-card">
      <div class="detail-header">
        <div>
          <span class="badge badge-cyan">{{ prediction.model_version }}</span>
          <h2>Assessment Record #{{ prediction.id }}</h2>
          <span class="date-lbl">{{ formatDate(prediction.created_at) }}</span>
        </div>
        <FreshnessBadge :classification="prediction.classification" />
      </div>

      <div class="specimen-img-box">
        <img :src="prediction.image_url" alt="Analyzed Fish" class="specimen-img" />
      </div>

      <div class="meta-section">
        <div class="meta-row">
          <span class="meta-lbl">Fish Species:</span>
          <span class="meta-val">{{ prediction.species_local_name || prediction.species_name || 'Auto-Detected Specimen' }}</span>
        </div>
        <div class="meta-row">
          <span class="meta-lbl">AI Classification Confidence:</span>
          <span class="meta-val text-cyan font-bold">{{ Math.round(prediction.confidence * 100) }}%</span>
        </div>
      </div>

      <!-- Recommendation -->
      <div class="rec-section">
        <h4>Recommendation</h4>
        <p>{{ prediction.recommendation }}</p>
        <p v-if="prediction.recommendation_tagalog" class="text-dim">
          <em>"{{ prediction.recommendation_tagalog }}"</em>
        </p>
      </div>

      <!-- Visual Indicators -->
      <IndicatorList :indicators="prediction.visual_indicators" />

      <!-- Disclaimer -->
      <DisclaimerBanner />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import ApiService from '../../services/api';
import FreshnessBadge from '../../components/result/FreshnessBadge.vue';
import IndicatorList from '../../components/result/IndicatorList.vue';
import DisclaimerBanner from '../../components/common/DisclaimerBanner.vue';

const route = useRoute();
const prediction = ref(null);

function formatDate(dStr) {
  if (!dStr) return '';
  return new Date(dStr).toLocaleString('en-US', { dateStyle: 'full', timeStyle: 'short' });
}

function printRecord() {
  window.print();
}

onMounted(async () => {
  try {
    const res = await ApiService.getPredictionById(route.params.id);
    if (res.success) {
      prediction.value = res.prediction;
    }
  } catch (e) {
    console.error('Failed to load prediction details:', e);
  }
});
</script>

<style scoped>
.history-detail-view {
  padding: 3rem 1.25rem;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.detail-card {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.detail-header h2 {
  font-size: 1.6rem;
  margin: 0.35rem 0;
}

.date-lbl {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.specimen-img-box {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #000;
}

.specimen-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.meta-section {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  background: rgba(0, 0, 0, 0.25);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-sm);
}

.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.meta-lbl { color: var(--text-muted); }
.meta-val { color: var(--text-white); }
.text-cyan { color: var(--primary); }

.rec-section {
  background: rgba(14, 165, 233, 0.06);
  border: 1px solid rgba(14, 165, 233, 0.2);
  padding: 1.25rem;
  border-radius: var(--radius-sm);
}

.rec-section h4 {
  font-size: 0.95rem;
  margin-bottom: 0.4rem;
}

.rec-section p {
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-main);
}
</style>
