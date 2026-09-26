<template>
  <div class="result-view container">
    <div class="result-top-bar">
      <router-link to="/analyze" class="btn btn-secondary btn-sm">
        &larr; Analyze Another Fish
      </router-link>
      <div class="top-meta">
        <span class="badge badge-cyan">{{ resultData.modelVersion || 'FreshCatch-CNN-v1.0-MobileNetV2' }}</span>
        <button @click="printSlip" class="btn btn-outline btn-sm">Print assessment</button>
      </div>
    </div>

    <!-- Main Results Grid -->
    <div class="result-main-grid">
      <!-- Left Column: Image Snapshot & Quality Diagnostics -->
      <div class="left-col">
        <div class="glass-card image-card">
          <div class="img-frame">
            <img :src="mediaUrl(resultData.imageUrl || defaultSampleImage)" alt="Analyzed Fish" class="analyzed-img" />
          </div>
          <div class="img-caption">
            <span class="caption-date">Analyzed on {{ formatTimestamp(resultData.createdAt) }}</span>
            <span class="caption-loc">Roxas Wet Market, Oriental Mindoro</span>
          </div>
        </div>

        <!-- Image Quality Diagnostics -->
        <div v-if="resultData.quality_metrics && Object.keys(resultData.quality_metrics).length" class="glass-card quality-card">
          <h4>Image quality</h4>
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
          <span class="result-tag">Visual freshness report</span>
          <div class="badge-wrapper">
            <FreshnessBadge :classification="resultData.classification || 'Fresh'" />
          </div>

          <!-- Dual Recommendation Box -->
          <div class="recommendation-box">
            <h4>Culinary &amp; handling guidance</h4>
            <p class="rec-en">{{ resultData.recommendation }}</p>
            <p v-if="resultData.recommendation_tagalog" class="rec-tl">
              <em>"{{ resultData.recommendation_tagalog }}"</em>
            </p>
            <div v-if="consumptionGuidance" class="consumption-guidance">
              <div class="consumption-heading">
                <span class="consumption-icon" aria-hidden="true">⏱</span>
                <span>Estimated consumption timing</span>
              </div>
              <strong v-if="consumptionGuidance.consume_by">
                Consume by {{ consumptionGuidance.consume_by }}
              </strong>
              <strong v-else>Do not consume</strong>
              <p>{{ consumptionGuidance.window }}</p>
              <p v-if="consumptionGuidance.window_tagalog" class="rec-tl">
                <em>{{ consumptionGuidance.window_tagalog }}</em>
              </p>
            </div>
          </div>

          <!-- Food Safety Warning — shown for Less Fresh and Not Fresh -->
          <div
            v-if="resultData.food_safety_warning"
            :class="['safety-warning-box', safetyLevel]"
          >
            <div class="safety-icon" aria-hidden="true">
              <svg v-if="safetyLevel === 'danger'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
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

        <!-- Live Recipe Suggestions (TheMealDB) — freshness-filtered -->
        <RecipeSuggestions
          :classification="resultData.classification"
          :species="resultData.species_name || resultData.species_local_name || ''"
        />

        <!-- Prominent Safety Disclaimer Banner -->
        <DisclaimerBanner />

        <!-- Bottom Actions -->
        <div class="result-actions">
          <router-link to="/analyze" class="btn btn-primary btn-lg w-full" @click="clearActiveResult">
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
import RecipeSuggestions from '../../components/result/RecipeSuggestions.vue';
import DisclaimerBanner from '../../components/common/DisclaimerBanner.vue';
import ApiService, { mediaUrl } from '../../services/api';
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

function clearActiveResult() {
  if (typeof window !== 'undefined' && window.sessionStorage) {
    window.sessionStorage.removeItem('freshcatch_active_result');
  }
}

const consumptionGuidance = computed(() => {
  if (resultData.value.consumption_guidance) return resultData.value.consumption_guidance;
  const windows = {
    Fresh: ['Best consumed today; refrigerate at 0-4°C and use within 1 day.', 'Pinakamainam kainin ngayong araw; ilagay sa 0-4°C na refrigerator at gamitin sa loob ng 1 araw.', 1],
    'Moderately Fresh': ['Cook promptly today; if continuously refrigerated, use within 1 day. Do not eat raw.', 'Lutuin agad ngayong araw; kung naka-refrigerate, gamitin sa loob ng 1 araw. Huwag kainin nang hilaw.', 1],
    'Less Fresh': ['Cook immediately today only after checking smell and texture. Do not store for later or eat raw.', 'Lutuin agad ngayong araw matapos suriin ang amoy at tekstura. Huwag itago o kainin nang hilaw.', 0],
    'Not Fresh': ['Do not consume. Discard immediately; there is no safe consumption date.', 'Huwag kainin. Itapon agad; walang ligtas na petsa para kainin ito.', null],
  };
  const [window, windowTagalog, days] = windows[resultData.value.classification] || windows.Fresh;
  const consumeBy = days === null ? null : new Date(Date.now() + days * 86400000).toISOString().slice(0, 10);
  return { window, window_tagalog: windowTagalog, consume_by: consumeBy };
});

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
  if (cls.includes('not fresh') || cls.includes('spoiled') || cls.includes('stale') || cls.includes('bilasa')) return 'danger';
  if (cls.includes('less fresh')) return 'caution';
  return 'caution';
});

onMounted(async () => {
  const cached = sessionStorage.getItem('freshcatch_active_result');

  // Always clear the cache immediately after reading it.
  // This ensures the next analysis never gets this stale result —
  // even if the user navigates back without starting a new analysis.
  clearActiveResult();

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
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #0a0f1e;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 480px;
}

.analyzed-img {
  width: 100%;
  height: auto;
  max-height: 480px;
  object-fit: contain;
  display: block;
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
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--accent-gold);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 0.85rem;
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

.consumption-guidance {
  margin-top: 0.9rem;
  padding: 0.8rem 0.9rem;
  border-left: 3px solid var(--accent-teal);
  background: rgba(45, 212, 191, 0.08);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.consumption-heading {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--accent-teal);
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.consumption-icon { font-size: 0.95rem; }

.consumption-guidance strong {
  display: block;
  margin-top: 0.35rem;
  color: var(--text-white);
  font-size: 0.9rem;
}

.consumption-guidance p {
  margin-top: 0.25rem;
  color: var(--text-main);
  font-size: 0.78rem;
  line-height: 1.45;
}

.consumption-guidance .rec-tl {
  color: var(--text-muted);
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
  color: inherit;
  flex-shrink: 0;
  margin-top: 0.15rem;
}
.safety-warning-box.danger .safety-icon { color: #fca5a5; }
.safety-warning-box.caution .safety-icon { color: #fde68a; }

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
