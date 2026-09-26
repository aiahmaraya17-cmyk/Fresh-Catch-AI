<template>
  <div class="stall-detail-view container">
    <router-link to="/stalls" class="back-link">&larr; All stalls</router-link>

    <div v-if="isLoading" class="loading-state text-center">
      <p>Loading stall...</p>
    </div>

    <div v-else-if="!stall" class="glass-card empty-state text-center">
      <p>Stall not found.</p>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="glass-card stall-hero">
        <div class="hero-main">
          <h1>{{ stall.name }}</h1>
          <p class="stall-meta">
            {{ stall.market_name }}<span v-if="stall.section"> · {{ stall.section }}</span>
          </p>
          <p v-if="stall.description" class="stall-desc">{{ stall.description }}</p>
          <p v-if="stall.owner_name" class="stall-owner">Operated by {{ stall.owner_name }}</p>
          <p v-if="stall.contact_number" class="stall-contact">📞 {{ stall.contact_number }}</p>
        </div>

        <div class="hero-score">
          <div
            class="score-ring"
            :class="ratePillClass(stall.stats.freshness_percentage)"
          >
            <span class="score-num">
              {{ stall.stats.freshness_percentage !== null ? stall.stats.freshness_percentage + '%' : '—' }}
            </span>
            <span class="score-label">freshness rate</span>
          </div>
        </div>
      </div>

      <!-- Stat tiles -->
      <div class="stat-tiles">
        <div class="glass-card tile">
          <strong>{{ stall.stats.total_scans }}</strong>
          <span>Total scans</span>
        </div>
        <div class="glass-card tile">
          <strong>{{ stall.stats.scans_today }}</strong>
          <span>Scans today</span>
        </div>
        <div class="glass-card tile">
          <strong>{{ stall.stats.class_counts['Fresh'] + stall.stats.class_counts['Moderately Fresh'] }}</strong>
          <span>Fresh results</span>
        </div>
        <div class="glass-card tile">
          <strong>{{ stall.stats.last_scan_at ? formatDate(stall.stats.last_scan_at) : '—' }}</strong>
          <span>Last scan</span>
        </div>
      </div>

      <!-- Freshness breakdown bar -->
      <div class="glass-card breakdown-card" v-if="stall.stats.total_scans > 0">
        <h3>Freshness breakdown</h3>
        <div class="breakdown-bar">
          <div
            v-for="cls in classOrder"
            :key="cls.key"
            v-show="stall.stats.class_counts[cls.key] > 0"
            class="bar-seg"
            :style="{ width: pct(stall.stats.class_counts[cls.key]) + '%', background: cls.color }"
            :title="`${cls.key}: ${stall.stats.class_counts[cls.key]}`"
          ></div>
        </div>
        <div class="breakdown-legend">
          <span v-for="cls in classOrder" :key="cls.key" class="legend-item">
            <span class="legend-dot" :style="{ background: cls.color }"></span>
            {{ cls.key }} ({{ stall.stats.class_counts[cls.key] }})
          </span>
        </div>
      </div>

      <!-- Recent scans feed -->
      <h3 class="feed-title">Recent freshness scans</h3>
      <div v-if="recentScans.length === 0" class="glass-card empty-state text-center">
        <p>This stall has no public scans yet.</p>
      </div>
      <div v-else class="scans-grid">
        <div v-for="scan in recentScans" :key="scan.id" class="glass-card scan-card">
          <div class="scan-thumb">
            <img :src="mediaUrl(scan.image_url)" :alt="scan.species_local_name || 'fish'" />
            <span class="scan-badge" :class="badgeClass(scan.classification)">
              {{ scan.classification }}
            </span>
          </div>
          <div class="scan-info">
            <strong>{{ scan.species_local_name || scan.species_name || 'Unknown species' }}</strong>
            <span>{{ Math.round(scan.confidence * 100) }}% · {{ formatDateTime(scan.created_at) }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import ApiService, { mediaUrl } from '../../services/api';

const route = useRoute();
const stall = ref(null);
const recentScans = ref([]);
const isLoading = ref(true);

const classOrder = [
  { key: 'Fresh',            color: '#22c55e' },
  { key: 'Moderately Fresh', color: '#84cc16' },
  { key: 'Less Fresh',       color: '#eab308' },
  { key: 'Not Fresh',        color: '#ef4444' },
];

function ratePillClass(pct) {
  if (pct === null) return 'ring-neutral';
  if (pct >= 80) return 'ring-good';
  if (pct >= 50) return 'ring-mid';
  return 'ring-poor';
}

function badgeClass(cls) {
  if (cls === 'Fresh') return 'b-fresh';
  if (cls === 'Moderately Fresh') return 'b-mod';
  if (cls === 'Less Fresh') return 'b-less';
  return 'b-not';
}

function pct(count) {
  const total = stall.value?.stats?.total_scans || 1;
  return (count / total) * 100;
}

function formatDate(ts) {
  if (!ts) return '—';
  return new Date(ts.replace(' ', 'T')).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' });
}
function formatDateTime(ts) {
  if (!ts) return '';
  return new Date(ts.replace(' ', 'T')).toLocaleString('en-PH', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

async function fetchStall() {
  isLoading.value = true;
  try {
    const res = await ApiService.getStallById(route.params.id);
    if (res.success) {
      stall.value = res.stall;
      recentScans.value = res.recentScans || [];
    }
  } catch (e) {
    console.error('Failed to load stall:', e);
  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchStall);
</script>

<style scoped>
.stall-detail-view { padding: 1.5rem 0 4rem; }
.back-link { display: inline-block; margin-bottom: 1rem; color: var(--text-muted); font-size: 0.85rem; }
.back-link:hover { color: var(--primary, #0ea5e9); }

.stall-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  padding: 1.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}
.hero-main h1 { margin: 0 0 0.35rem; }
.stall-meta { color: var(--text-muted); font-size: 0.9rem; margin: 0 0 0.5rem; }
.stall-desc { color: var(--text-soft, #cbd5e1); margin: 0 0 0.5rem; max-width: 520px; }
.stall-owner, .stall-contact { font-size: 0.82rem; color: var(--text-muted); margin: 0.15rem 0; }

.hero-score { flex-shrink: 0; }
.score-ring {
  width: 130px; height: 130px;
  border-radius: 50%;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  border: 6px solid;
}
.score-num { font-size: 1.9rem; font-weight: 800; }
.score-label { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.ring-good    { border-color: #22c55e; }
.ring-good .score-num { color: #22c55e; }
.ring-mid     { border-color: #eab308; }
.ring-mid .score-num { color: #eab308; }
.ring-poor    { border-color: #ef4444; }
.ring-poor .score-num { color: #ef4444; }
.ring-neutral { border-color: #94a3b8; }
.ring-neutral .score-num { color: #94a3b8; }

.stat-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.tile { padding: 1.1rem; text-align: center; }
.tile strong { display: block; font-size: 1.4rem; color: var(--text-white, #fff); }
.tile span { font-size: 0.75rem; color: var(--text-muted); }

.breakdown-card { padding: 1.4rem; margin-bottom: 1.75rem; }
.breakdown-card h3 { margin: 0 0 1rem; font-size: 1rem; }
.breakdown-bar {
  display: flex; height: 20px; border-radius: 999px; overflow: hidden;
  background: rgba(148,163,184,0.1);
}
.bar-seg { height: 100%; }
.breakdown-legend { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 0.85rem; }
.legend-item { font-size: 0.78rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.35rem; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }

.feed-title { margin: 0 0 1rem; font-size: 1.1rem; }
.scans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}
.scan-card { padding: 0.6rem; }
.scan-thumb { position: relative; border-radius: 8px; overflow: hidden; aspect-ratio: 4/3; }
.scan-thumb img { width: 100%; height: 100%; object-fit: cover; }
.scan-badge {
  position: absolute; top: 6px; left: 6px;
  font-size: 0.66rem; font-weight: 700;
  padding: 0.18rem 0.45rem; border-radius: 6px;
}
.b-fresh { background: #22c55e; color: #052e16; }
.b-mod   { background: #84cc16; color: #1a2e05; }
.b-less  { background: #eab308; color: #422006; }
.b-not   { background: #ef4444; color: #450a0a; }
.scan-info { padding: 0.5rem 0.3rem 0.2rem; display: flex; flex-direction: column; }
.scan-info strong { font-size: 0.85rem; }
.scan-info span { font-size: 0.72rem; color: var(--text-muted); }

.loading-state, .empty-state { padding: 3rem 1rem; }
</style>
