<template>
  <div class="freshness-badge-container" :class="badgeClass">
    <div class="status-indicator-dot"></div>
    <div class="badge-texts">
      <span class="badge-title">{{ displayName }}</span>
      <span class="badge-tagalog">{{ tagalogName }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  classification: {
    type: String,
    required: true
  }
});

const badgeClass = computed(() => {
  const norm = props.classification.toLowerCase();
  if (norm.includes('moderately')) return 'badge-mod';
  if (norm === 'not fresh')        return 'badge-less';
  if (norm.includes('spoiled') || norm.includes('bilasa') || norm.includes('stale')) return 'badge-stale';
  return 'badge-frsh';
});

const displayName = computed(() => {
  return props.classification.toUpperCase();
});

const tagalogName = computed(() => {
  const norm = props.classification.toLowerCase();
  if (norm.includes('moderately')) return 'KATAMTAMANG SARIWA';
  if (norm === 'not fresh')        return 'HINDI NA SARIWA';
  if (norm.includes('spoiled') || norm.includes('bilasa') || norm.includes('stale')) return 'BILASA';
  return 'SARIWA';
});
</script>

<style scoped>
.freshness-badge-container {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.75rem 1.6rem;
  border-radius: var(--radius-full);
  border: 1px solid;
  transition: all var(--transition-normal);
}

.status-indicator-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  box-shadow: 0 0 12px currentColor;
  animation: pulseDot 2s infinite;
}

@keyframes pulseDot {
  0% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.8; }
}

.badge-texts {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.badge-title {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  font-family: var(--font-heading);
}

.badge-tagalog {
  font-size: 0.72rem;
  font-weight: 700;
  opacity: 0.85;
  letter-spacing: 0.08em;
}

/* Fresh */
.badge-frsh {
  background: var(--color-fresh-bg);
  border-color: rgba(16, 185, 129, 0.4);
  color: var(--color-fresh);
  box-shadow: 0 0 20px var(--color-fresh-glow);
}
.badge-frsh .status-indicator-dot {
  background: var(--color-fresh);
  color: var(--color-fresh);
}

/* Moderately Fresh */
.badge-mod {
  background: var(--color-moderate-bg);
  border-color: rgba(245, 158, 11, 0.4);
  color: var(--color-moderate);
  box-shadow: 0 0 20px var(--color-moderate-glow);
}
.badge-mod .status-indicator-dot {
  background: var(--color-moderate);
  color: var(--color-moderate);
}

/* Not Fresh */
.badge-less {
  background: var(--color-less-fresh-bg);
  border-color: rgba(249, 115, 22, 0.4);
  color: var(--color-less-fresh);
  box-shadow: 0 0 20px var(--color-less-fresh-glow);
}
.badge-less .status-indicator-dot {
  background: var(--color-less-fresh);
  color: var(--color-less-fresh);
}

/* Spoiled */
.badge-stale {
  background: var(--color-not-fresh-bg);
  border-color: rgba(239, 68, 68, 0.4);
  color: var(--color-not-fresh);
  box-shadow: 0 0 20px var(--color-not-fresh-glow);
}
.badge-stale .status-indicator-dot {
  background: var(--color-not-fresh);
  color: var(--color-not-fresh);
}
</style>
