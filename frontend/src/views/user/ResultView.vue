<template>
  <div class="result-view container">
    <div class="result-top-bar">
      <router-link to="/analyze" class="btn btn-secondary btn-sm">
        &larr; Analyze Another Fish
      </router-link>
      <div class="top-meta">
        <span class="badge badge-cyan">{{ resultData.modelVersion || 'FreshCatch-CNN-v1.0-MobileNetV2' }}</span>
        <button @click="printSlip" class="btn btn-outline btn-sm">
          🖨️ Print Slip
        </button>
      </div>
    </div>

    <!-- Main Results Grid -->
    <div class="result-main-grid">
      <!-- Left Column: Image Snapshot & Quality Diagnostics -->
      <div class="left-col">
        <div class="glass-card image-card">
          <div class="img-frame">
            <img :src="resultData.imageUrl || defaultSampleImage" alt="Analyzed Fish" class="analyzed-img" />
          </div>
          <div class="img-caption">
            <span class="caption-date">Analyzed on {{ formatTimestamp(resultData.createdAt) }}</span>
            <span class="caption-loc">Roxas Wet Market, Oriental Mindoro</span>
          </div>
        </div>

        <!-- Image Quality Diagnostics -->
        <div v-if="resultData.quality_metrics && Object.keys(resultData.quality_metrics).length" class="glass-card quality-card">
          <h4>Image Quality Diagnostics</h4>
          <div class="quality-metrics-list">
            <div class="q-metric-item">
              <span class="q-lbl">Sharpness / Focus Index:</span>
              <span class="q-val text-cyan">{{ resultData.quality_metrics.blur_variance }}</span>
            </div>
            <div class="q-metric-item">
              <span class="q-lbl">Luminance / Brightness:</span>
              <span class="q-val">{{ resultData.quality_metrics.brightness_mean }}/255</span>
            </div>
            <div class="q-metric-item">
              <span class="q-lbl">Contrast Standard Dev:</span>
              <span class="q-val">{{ resultData.quality_metrics.contrast_std }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Freshness Classification & Details -->
      <div class="right-col">
        <div class="glass-card classification-header-card">
          <span class="result-tag">AI-ASSISTED VISUAL ASSESSMENT</span>
          <div class="badge-wrapper">
            <FreshnessBadge :classification="resultData.classification || 'Fresh'" />
          </div>

          <!-- Dual Recommendation Box -->
          <div class="recommendation-box">
            <h4>Culinary & Market Recommendation</h4>
            <p class="rec-en">{{ resultData.recommendation }}</p>
            <p v-if="resultData.recommendation_tagalog" class="rec-tl">
              <em>"{{ resultData.recommendation_tagalog }}"</em>
            </p>
          </div>

          <!-- Food Safety Warning — shown for Less Fresh and Not Fresh -->
          <div
            v-if="resultData.food_safety_warning"
            :class="['safety-warning-box', safetyLevel]"
          >
            <div class="safety-icon">{{ safetyLevel === 'danger' ? '🚫' : '⚠️' }}</div>
            <div class="safety-content">
              <p class="safety-en">{{ strippedWarning }}</p>
              <p v-if="resultData.food_safety_warning_tagalog" class="safety-tl">
                <em>{{ strippedWarningTl }}</em>
              </p>
            </div>
          </div>
        </div>

        <!-- Confidence Gauge & Multi-Class Probabilities -->
        <ConfidenceGauge 
          :confidence="resultData.confidence || 0.92" 
          :probabilities="resultData.class_probabilities || resultData.classProbabilities"
        />

        <!-- Detected Visual Indicators -->
        <IndicatorList :indicators="resultData.visualIndicators || resultData.visual_indicators" />

        <!-- Prominent Safety Disclaimer Banner -->
        <DisclaimerBanner />

        <!-- Bottom Actions -->
        <div class="result-actions">
          <router-link to="/analyze" class="btn btn-primary btn-lg w-full">
            Analyze Another Fish
          </router-link>
          <router-link to="/history" class="btn btn-secondary btn-lg w-full">
            View Assessment History
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import FreshnessBadge from '../../components/result/FreshnessBadge.vue';
import ConfidenceGauge from '../../components/result/ConfidenceGauge.vue';
import IndicatorList from '../../components/result/IndicatorList.vue';
import DisclaimerBanner from '../../components/common/DisclaimerBanner.vue';
import ApiService from '../../services/api';
import confetti from 'canvas-confetti';

const route = useRoute();
const defaultSampleImage = '/dataset/raw/fish_0001_bangus_fresh_bright.jpg';

const resultData = ref({
  classification: 'Fresh',
  confidence: 0.924,
  imageUrl: defaultSampleImage,
  modelVersion: 'FreshCatch-CNN-v1.0-MobileNetV2',
  recommendation: 'The fish appears visually fresh based on clear eyes, vibrant opercular redness, and intact scale luster. Highly suitable for raw preparation (kinilaw), steaming, grilling, or soup dishes like sinigang.',
  recommendation_tagalog: 'Ang isda ay mukhang sariwa batay sa malinaw na mata, mapulang hasang, at makintab na kaliskis. Angkop na angkop para sa kinilaw, inihaw, o sinigang.',
  class_probabilities: {
    'Fresh': 0.924,
    'Moderately Fresh': 0.052,
    'Not Fresh': 0.016,
    'Spoiled': 0.008
  },
  visualIndicators: [
    { region: 'Eyes', label: 'Clear, convex cornea with distinct pupil', tagalog: 'Malinaw at umbok na mata', status: 'fresh' },
    { region: 'Gills', label: 'Vibrant red / pink opercular coloration', tagalog: 'Matingkad na pula o rosas na hasang', status: 'fresh' },
    { region: 'Skin & Scales', label: 'Natural metallic sheen and intact tight scales', tagalog: 'Makintab at buo ang mga kaliskis', status: 'fresh' }
  ],
  quality_metrics: {
    blur_variance: 142.5,
    brightness_mean: 184.2,
    contrast_std: 42.1
  },
  createdAt: new Date().toISOString()
});

function formatTimestamp(t) {
  if (!t) return new Date().toLocaleDateString();
  return new Date(t).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' });
}

function printSlip() {
  window.print();
}

// Strip leading emoji prefix from warning strings (rendered separately as icon)
const strippedWarning = computed(() => {
  const w = resultData.value.food_safety_warning || '';
  return w.replace(/^[🚫⚠️\s]+/, '').trim();
});

const strippedWarningTl = computed(() => {
  const w = resultData.value.food_safety_warning_tagalog || '';
  return w.replace(/^[🚫⚠️\s]+/, '').trim();
});

const safetyLevel = computed(() => {
  const cls = (resultData.value.classification || '').toLowerCase();
  if (cls === 'spoiled') return 'danger';
  if (cls === 'not fresh') return 'danger';
  return 'caution';
});

onMounted(async () => {
  const cached = sessionStorage.getItem('freshcatch_active_result');
  if (cached) {
    try {
      resultData.value = JSON.parse(cached);
    } catch (e) {}
  } else if (route.params.id && route.params.id !== 'latest') {
    try {
      const res = await ApiService.getPredictionById(route.params.id);
      if (res.success && res.prediction) {
        resultData.value = res.prediction;
      }
    } catch (e) {}
  }

  // Trigger celebration confetti if fresh
  if ((resultData.value.classification || '').toLowerCase() === 'fresh') {
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.6 }
    });
  }
});
</script>

<style scoped>
.result-view {
  padding: clamp(1.25rem, 4vw, 2.5rem) 1.25rem 4rem;
}

.result-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.top-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.result-main-grid {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 2rem;
}

@media (max-width: 900px) {
  .result-main-grid {
    grid-template-columns: 1fr;
  }
}

.left-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.image-card {
  padding: 1.25rem;
}

.img-frame {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #000;
  margin-bottom: 0.75rem;
}

.analyzed-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.img-caption {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-dim);
}

.quality-card {
  padding: 1.25rem;
}

.quality-card h4 {
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.quality-metrics-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.82rem;
}

.q-metric-item {
  display: flex;
  justify-content: space-between;
  padding: 0.35rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.q-lbl { color: var(--text-muted); }
.q-val { font-weight: 700; color: var(--text-white); }
.text-cyan { color: var(--primary); }

.right-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.classification-header-card {
  padding: 1.75rem;
}

.result-tag {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--primary);
  letter-spacing: 0.08em;
  margin-bottom: 0.75rem;
  display: block;
}

.badge-wrapper {
  margin-bottom: 1.25rem;
}

.recommendation-box {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-glass);
  padding: 1.15rem;
  border-radius: var(--radius-sm);
}

.recommendation-box h4 {
  font-size: 0.95rem;
  color: var(--text-white);
  margin-bottom: 0.4rem;
}

.rec-en {
  font-size: 0.9rem;
  color: var(--text-main);
  line-height: 1.5;
  margin-bottom: 0.4rem;
}

.rec-tl {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.w-full { width: 100%; }

@media (min-width: 480px) {
  .result-actions {
    flex-direction: row;
  }
}

@media (max-width: 480px) {
  .classification-header-card {
    padding: 1.25rem;
  }
  .recommendation-box {
    padding: 0.9rem;
  }
  .img-caption {
    flex-direction: column;
    gap: 0.2rem;
  }
}

@media print {
  .result-top-bar, .result-actions, .navbar, .app-footer {
    display: none !important;
  }
}

/* ── Food Safety Warning ───────────────────────────────────────────────────── */
.safety-warning-box {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  padding: 1.1rem 1.25rem;
  border-radius: var(--radius-sm);
  border-width: 1px;
  border-style: solid;
  margin-top: 0.25rem;
}

.safety-warning-box.danger {
  background: rgba(220, 38, 38, 0.12);
  border-color: rgba(220, 38, 38, 0.45);
}

.safety-warning-box.caution {
  background: rgba(234, 179, 8, 0.10);
  border-color: rgba(234, 179, 8, 0.40);
}

.safety-icon {
  font-size: 1.5rem;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 0.05rem;
}

.safety-content {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.safety-en {
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.5;
  color: var(--text-white);
  margin: 0;
}

.safety-warning-box.danger .safety-en { color: #fca5a5; }
.safety-warning-box.caution .safety-en { color: #fde68a; }

.safety-tl {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin: 0;
}
</style>
