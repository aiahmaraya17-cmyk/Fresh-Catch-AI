<template>
  <div class="confidence-gauge-card">
    <div class="gauge-header">
      <span class="gauge-title">AI Confidence Score</span>
      <span class="certainty-pill" :class="certaintyClass">{{ certaintyText }}</span>
    </div>

    <div class="dial-container">
      <svg viewBox="0 0 100 55" class="dial-svg">
        <!-- Background Track -->
        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          stroke-width="9"
          stroke-linecap="round"
        />
        <!-- Active Progress Arc -->
        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          :stroke="gaugeColor"
          stroke-width="9"
          stroke-linecap="round"
          :stroke-dasharray="dashArray"
          :stroke-dashoffset="dashOffset"
          class="dial-progress"
        />
      </svg>
      <div class="dial-value">
        <span class="pct-number">{{ percentage }}%</span>
      </div>
    </div>

    <!-- Probability Breakdown per Class -->
    <div v-if="probabilities && Object.keys(probabilities).length" class="prob-distribution">
      <div v-for="(pVal, pName) in probabilities" :key="pName" class="prob-row">
        <span class="prob-name">{{ pName }}</span>
        <div class="prob-bar-track">
          <div class="prob-bar-fill" :style="{ width: (pVal * 100) + '%' }"></div>
        </div>
        <span class="prob-val">{{ (pVal * 100).toFixed(1) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  confidence: {
    type: Number,
    default: 0.92
  },
  probabilities: {
    type: Object,
    default: () => ({})
  }
});

const percentage = computed(() => {
  return (props.confidence * 100).toFixed(1);
});

const certaintyText = computed(() => {
  if (props.confidence >= 0.85) return 'High Certainty';
  if (props.confidence >= 0.70) return 'Moderate Certainty';
  return 'Low Certainty (Inspect Closely)';
});

const certaintyClass = computed(() => {
  if (props.confidence >= 0.85) return 'cert-high';
  if (props.confidence >= 0.70) return 'cert-mod';
  return 'cert-low';
});

const gaugeColor = computed(() => {
  if (props.confidence >= 0.85) return '#0ea5e9';
  if (props.confidence >= 0.70) return '#f59e0b';
  return '#ef4444';
});

const arcLength = 125.6; // pi * 40
const dashArray = arcLength;
const dashOffset = computed(() => {
  const fraction = Math.min(1, Math.max(0, props.confidence));
  return arcLength * (1 - fraction);
});
</script>

<style scoped>
.confidence-gauge-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.25rem;
}

.gauge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.gauge-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.certainty-pill {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}

.cert-high { background: rgba(14, 165, 233, 0.2); color: #38bdf8; }
.cert-mod  { background: rgba(245, 158, 11, 0.2);  color: #fbbf24; }
.cert-low  { background: rgba(239, 68, 68, 0.2);   color: #f87171; }

.dial-container {
  position: relative;
  width: clamp(100px, 35vw, 140px);
  margin: 0.5rem auto 1rem;
}

.dial-svg {
  width: 100%;
  overflow: visible;
}

.dial-progress {
  transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.dial-value {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
}

.pct-number {
  font-size: clamp(1rem, 4vw, 1.35rem);
  font-weight: 800;
  font-family: var(--font-heading);
  color: var(--text-white);
}

.prob-distribution {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.prob-row {
  display: grid;
  grid-template-columns: minmax(0, 120px) 1fr 42px;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

/* On very narrow screens shrink the label column */
@media (max-width: 360px) {
  .prob-row {
    grid-template-columns: minmax(0, 80px) 1fr 38px;
    font-size: 0.7rem;
  }
}

.prob-name {
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prob-bar-track {
  background: rgba(0, 0, 0, 0.3);
  height: 5px;
  border-radius: 3px;
  overflow: hidden;
}

.prob-bar-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 3px;
  transition: width 0.6s ease;
}

.prob-val {
  text-align: right;
  font-weight: 600;
  color: var(--text-white);
}
</style>
