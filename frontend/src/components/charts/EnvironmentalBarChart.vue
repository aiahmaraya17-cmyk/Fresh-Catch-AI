<template>
  <div class="env-chart-card">
    <div class="env-chart-header">
      <h4>Environmental Factor Robustness</h4>
      <span class="badge badge-cyan">{{ factorTitle }}</span>
    </div>

    <div class="bars-container">
      <div v-for="item in data" :key="item.condition" class="bar-row">
        <div class="bar-info">
          <span class="bar-name">{{ item.condition }}</span>
          <span class="bar-sub">{{ item.sample_count }} samples</span>
        </div>

        <div class="bar-track">
          <div 
            class="bar-fill" 
            :style="{ width: (item.accuracy * 100) + '%' }"
            :class="getBarClass(item.accuracy)"
          ></div>
        </div>

        <div class="bar-metric">
          <span class="score-text">{{ (item.accuracy * 100).toFixed(1) }}%</span>
          <span class="status-chip" :class="getStatusClass(item.status)">{{ item.status }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  factorKey: {
    type: String,
    default: 'lighting'
  },
  data: {
    type: Array,
    default: () => [
      { condition: 'Bright', sample_count: 52, accuracy: 0.942, status: 'Robust' },
      { condition: 'Normal', sample_count: 64, accuracy: 0.921, status: 'Robust' },
      { condition: 'Dim', sample_count: 44, accuracy: 0.818, status: 'Acceptable' }
    ]
  }
});

const factorTitle = computed(() => {
  const map = {
    lighting: 'Market Lighting',
    background: 'Background Clutter',
    orientation: 'Fish Angle & Orientation',
    distance: 'Camera Distance',
    image_quality: 'Image Quality & Blur'
  };
  return map[props.factorKey] || props.factorKey;
});

function getBarClass(acc) {
  if (acc >= 0.88) return 'bar-green';
  if (acc >= 0.75) return 'bar-amber';
  return 'bar-red';
}

function getStatusClass(status) {
  if (status === 'Robust') return 'status-robust';
  if (status === 'Acceptable') return 'status-acceptable';
  return 'status-vulnerable';
}
</script>

<style scoped>
.env-chart-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.5rem;
}

.env-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.bars-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.bar-row {
  display: grid;
  grid-template-columns: 140px 1fr 110px;
  align-items: center;
  gap: 1rem;
}

@media (max-width: 600px) {
  .bar-row {
    grid-template-columns: 1fr;
    gap: 0.35rem;
  }
}

.bar-info {
  display: flex;
  flex-direction: column;
}

.bar-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-white);
}

.bar-sub {
  font-size: 0.72rem;
  color: var(--text-dim);
}

.bar-track {
  background: rgba(0, 0, 0, 0.4);
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-green { background: linear-gradient(90deg, #10b981, #34d399); }
.bar-amber { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.bar-red { background: linear-gradient(90deg, #ef4444, #f87171); }

.bar-metric {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.score-text {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-white);
}

.status-chip {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.status-robust {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.status-acceptable {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.status-vulnerable {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}
</style>
