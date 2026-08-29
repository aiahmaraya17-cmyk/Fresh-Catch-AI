<template>
  <div class="disclaimer-banner">
    <div class="icon-wrap">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    </div>
    <div class="content-wrap">
      <h5 class="disclaimer-title">
        {{ lang === 'tl' ? 'Mahalagang Paalala sa Kaligtasan at Pagsusuri ng AI' : 'Important Safety & Visual Assessment Disclaimer' }}
      </h5>
      <p class="disclaimer-text">
        {{ lang === 'tl'
          ? 'Ang FreshCatch AI ay nagbibigay ng AI-assisted na visual assessment ng hitsura ng isda batay sa larawan. Ang resulta ay hindi laboratory test at hindi garantiya ng lubos na kaligtasan sa pagkain. Ang kasariwaan ay nakasalalay din sa amoy, temperatura, at paraan ng pag-imbak. Palaging suriin ang iba pang pisikal na katangian bago bilhin o kainin ang isda.'
          : 'FreshCatch AI provides an AI-assisted visual assessment of apparent fish freshness based on an uploaded or captured image. The result is not a laboratory test and does not guarantee that the fish is safe to eat. Freshness can also depend on factors that cannot be determined from an image, such as odor, temperature, handling, storage conditions, microorganisms, and contamination. Users should consider other appropriate freshness and food-safety indicators before purchasing or consuming fish.'
        }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '../../stores/authStore';

const authStore = useAuthStore();
const lang = computed(() => authStore.language || 'en');
</script>

<style scoped>
.disclaimer-banner {
  display: flex;
  gap: 1rem;
  background: rgba(245, 158, 11, 0.09);
  border: 1px solid rgba(245, 158, 11, 0.25);
  padding: 1.15rem 1.4rem;
  border-radius: var(--radius-md);
  margin: 1.5rem 0;
  backdrop-filter: blur(8px);
}

.icon-wrap {
  color: #f59e0b;
  flex-shrink: 0;
  margin-top: 2px;
}

.content-wrap {
  flex: 1;
}

.disclaimer-title {
  color: #fde68a;
  font-size: 0.92rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.disclaimer-text {
  color: #fef3c7;
  font-size: 0.85rem;
  line-height: 1.5;
  opacity: 0.92;
}
</style>
