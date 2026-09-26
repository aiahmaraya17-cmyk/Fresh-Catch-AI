<template>
  <div class="stalls-view container">
    <div class="page-header">
      <span class="badge badge-cyan">Market Directory</span>
      <h1>Verified Fish Stalls</h1>
      <p class="subtitle">
        Browse Roxas Public Market stalls and check their freshness track record before you buy.
      </p>
    </div>

    <div v-if="isLoading" class="loading-state text-center">
      <p>Loading stalls...</p>
    </div>

    <div v-else-if="stalls.length === 0" class="glass-card empty-state text-center">
      <p>No registered stalls yet.</p>
    </div>

    <div v-else class="stalls-grid">
      <router-link
        v-for="stall in stalls"
        :key="stall.id"
        :to="`/stalls/${stall.id}`"
        class="glass-card stall-card"
      >
        <div class="stall-card-head">
          <h3>{{ stall.name }}</h3>
          <span
            v-if="stall.stats.freshness_percentage !== null"
            class="freshness-pill"
            :class="ratePillClass(stall.stats.freshness_percentage)"
          >
            {{ stall.stats.freshness_percentage }}% fresh
          </span>
          <span v-else class="freshness-pill pill-neutral">No scans yet</span>
        </div>

        <p class="stall-meta">{{ stall.market_name }}<span v-if="stall.section"> · {{ stall.section }}</span></p>
        <p v-if="stall.description" class="stall-desc">{{ stall.description }}</p>

        <div class="stall-stats-row">
          <div class="stat-chip">
            <strong>{{ stall.stats.total_scans }}</strong>
            <span>total scans</span>
          </div>
          <div class="stat-chip">
            <strong>{{ stall.stats.scans_today }}</strong>
            <span>today</span>
          </div>
          <div class="stat-chip">
            <strong>{{ stall.stats.last_scan_at ? formatDate(stall.stats.last_scan_at) : '—' }}</strong>
            <span>last scan</span>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '../../services/api';

const stalls = ref([]);
const isLoading = ref(true);

function ratePillClass(pct) {
  if (pct >= 80) return 'pill-good';
  if (pct >= 50) return 'pill-mid';
  return 'pill-poor';
}

function formatDate(ts) {
  if (!ts) return '—';
  const d = new Date(ts.replace(' ', 'T'));
  return d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' });
}

async function fetchStalls() {
  isLoading.value = true;
  try {
    const res = await ApiService.getStalls();
    if (res.success) stalls.value = res.stalls;
  } catch (e) {
    console.error('Failed to load stalls:', e);
  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchStalls);
</script>

<style scoped>
.stalls-view { padding: 2rem 0 4rem; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { margin: 0.5rem 0; }
.subtitle { color: var(--text-muted); max-width: 640px; }

.stalls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

.stall-card {
  padding: 1.4rem;
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.stall-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.stall-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}
.stall-card-head h3 { font-size: 1.15rem; margin: 0; }

.freshness-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
  white-space: nowrap;
}
.pill-good    { background: rgba(34,197,94,0.15);  color: #22c55e; }
.pill-mid     { background: rgba(234,179,8,0.15);   color: #eab308; }
.pill-poor    { background: rgba(239,68,68,0.15);   color: #ef4444; }
.pill-neutral { background: rgba(148,163,184,0.15); color: #94a3b8; }

.stall-meta { font-size: 0.82rem; color: var(--text-muted); margin: 0; }
.stall-desc { font-size: 0.88rem; color: var(--text-soft, #cbd5e1); margin: 0; }

.stall-stats-row {
  display: flex;
  gap: 1.25rem;
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(148,163,184,0.12);
}
.stat-chip { display: flex; flex-direction: column; }
.stat-chip strong { font-size: 1rem; color: var(--text-white, #fff); }
.stat-chip span { font-size: 0.7rem; color: var(--text-muted); }

.loading-state, .empty-state { padding: 3rem 1rem; }
</style>
