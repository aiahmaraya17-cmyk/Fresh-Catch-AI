<template>
  <div class="indicator-list-card">
    <div class="card-header">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan">
        <path d="M2 12h20"/>
        <path d="M20 12v8H4v-8"/>
        <path d="m4 4 16 8"/>
      </svg>
      <h4>Observable Physical Indicators</h4>
    </div>

    <div class="indicators-container">
      <div v-for="(ind, idx) in indicators" :key="idx" class="indicator-item" :class="'item-' + ind.status">
        <div class="indicator-icon">
          <svg v-if="ind.status === 'fresh'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else-if="ind.status === 'moderate'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </div>

        <div class="indicator-text-wrap">
          <div class="indicator-region-tag">{{ ind.region }}</div>
          <p class="indicator-desc">{{ lang === 'tl' && ind.tagalog ? ind.tagalog : ind.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '../../stores/authStore';

const authStore = useAuthStore();
const lang = computed(() => authStore.language || 'en');

const props = defineProps({
  indicators: {
    type: Array,
    default: () => [
      { region: 'Eyes', label: 'Clear, convex cornea with distinct pupil', status: 'fresh' },
      { region: 'Gills', label: 'Vibrant red / pink opercular coloration', status: 'fresh' },
      { region: 'Skin & Scales', label: 'Natural metallic sheen and intact tight scales', status: 'fresh' }
    ]
  }
});
</script>

<style scoped>
.indicator-list-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.25rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.card-header h4 {
  font-size: 0.95rem;
  font-weight: 700;
}

.text-cyan { color: var(--primary); }

.indicators-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.indicator-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
}

.indicator-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.indicator-text-wrap {
  flex: 1;
}

.indicator-region-tag {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.2rem;
}

.indicator-desc {
  font-size: 0.85rem;
  color: var(--text-white);
  line-height: 1.35;
}

/* Fresh indicator status */
.item-fresh {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.25);
}
.item-fresh .indicator-icon {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}
.item-fresh .indicator-region-tag {
  color: #34d399;
}

/* Moderate indicator status */
.item-moderate {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.25);
}
.item-moderate .indicator-icon {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}
.item-moderate .indicator-region-tag {
  color: #fbbf24;
}

/* Stale indicator status */
.item-stale {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.25);
}
.item-stale .indicator-icon {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}
.item-stale .indicator-region-tag {
  color: #f87171;
}
</style>
