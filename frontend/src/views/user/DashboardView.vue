<template>
  <div class="dashboard-view container">
    <!-- User Welcome Greeting Banner -->
    <div class="glass-card welcome-card">
      <div class="welcome-left">
        <span class="badge badge-cyan">{{ authStore.userRole.toUpperCase() }} PORTAL</span>
        <h1>Welcome back, {{ authStore.userName }}</h1>
        <p class="welcome-sub">
          Assess fish specimens from Roxas wet market stalls or review your recent visual freshness classifications.
        </p>
        <div class="welcome-actions">
          <router-link to="/analyze" class="btn btn-primary btn-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
              <circle cx="12" cy="13" r="3"/>
            </svg>
            Analyze New Fish
          </router-link>
          <router-link to="/history" class="btn btn-secondary btn-lg">
            View All History
          </router-link>
        </div>
      </div>
      <div class="welcome-right">
        <div class="stats-mini-grid">
          <div class="mini-stat-card">
            <span class="stat-num">{{ stats.totalUserScans }}</span>
            <span class="stat-lbl">Personal Scans</span>
          </div>
          <div class="mini-stat-card">
            <span class="stat-num text-emerald">{{ stats.freshCount }}</span>
            <span class="stat-lbl">Fresh Classified</span>
          </div>
          <div class="mini-stat-card">
            <span class="stat-num text-cyan">89.6%</span>
            <span class="stat-lbl">Test-set accuracy</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Scan Shortcut Banner -->
    <div class="grid-2 my-4">
      <!-- Species Quick Launcher -->
      <div class="glass-card panel-card">
        <div class="panel-header">
          <h3>Local Species Quick Reference</h3>
          <router-link to="/guide" class="text-cyan text-sm">View Encyclopedia &rarr;</router-link>
        </div>
        <div class="species-chips-grid">
          <button 
            v-for="sp in commonSpecies" 
            :key="sp.local" 
            @click="quickAnalyzeSpecies(sp.name)"
            class="species-chip-btn"
          >
            <span class="sp-icon">🐟</span>
            <span class="sp-name">{{ sp.local }}</span>
            <span class="sp-sub">{{ sp.name }}</span>
          </button>
        </div>
      </div>

      <!-- Freshness Classification Guide Summary -->
      <div class="glass-card panel-card">
        <div class="panel-header">
          <h3>Freshness Categories</h3>
          <router-link to="/guide" class="text-cyan text-sm">Guidelines &rarr;</router-link>
        </div>
        <div class="categories-list">
          <div class="cat-row cat-row-fresh">
            <span class="badge badge-fresh">Fresh (Sariwa)</span>
            <span class="cat-hint">Convex clear eyes, ruby gills, metallic luster</span>
          </div>
          <div class="cat-row cat-row-mod">
            <span class="badge badge-moderate">Moderately Fresh</span>
            <span class="cat-hint">Slight flattening, dull red gills, good for frying</span>
          </div>
          <div class="cat-row cat-row-less">
            <span class="badge badge-less-fresh">Less Fresh</span>
            <span class="cat-hint">Cloudy eyes, dull gills — cook thoroughly</span>
          </div>
          <div class="cat-row cat-row-stale">
            <span class="badge badge-not-fresh">Not Fresh (Bilasa)</span>
            <span class="cat-hint">Do not purchase or consume</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Predictions Table / Grid -->
    <div class="glass-card panel-card">
      <div class="panel-header">
        <h3>Recent Classification History</h3>
        <router-link to="/history" class="text-cyan text-sm">See Full History &rarr;</router-link>
      </div>

      <div v-if="recentScans.length === 0" class="empty-state">
        <p>No fish scans recorded yet. Capture or upload your first fish photo to get started!</p>
        <router-link to="/analyze" class="btn btn-primary btn-sm mt-2">Start First Scan</router-link>
      </div>

      <div v-else class="recent-grid">
        <div v-for="scan in recentScans" :key="scan.id" class="scan-card glass-card">
          <div class="scan-img-wrap">
            <img :src="mediaUrl(scan.image_url)" alt="Fish scan thumbnail" class="scan-thumb" />
            <span class="scan-confidence-badge">{{ Math.round(scan.confidence * 100) }}% AI</span>
          </div>
          <div class="scan-details">
            <span class="scan-date">{{ formatDate(scan.created_at) }}</span>
            <h4 class="scan-species">{{ scan.species_local_name || scan.species_name || 'Fish Specimen' }}</h4>
            <div class="scan-badge-wrap">
              <span class="badge" :class="getBadgeClass(scan.classification)">
                {{ scan.classification }}
              </span>
            </div>
            <router-link :to="'/result/' + scan.id" class="btn btn-secondary btn-sm w-full mt-2">
              View Assessment
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import ApiService, { mediaUrl } from '../../services/api';

const authStore = useAuthStore();
const router = useRouter();

const stats = ref({
  totalUserScans: 0,
  freshCount: 0
});

const recentScans = ref([]);

const commonSpecies = [
  { local: 'Bangus', name: 'Milkfish' },
  { local: 'Tilapia', name: 'Tilapia' },
  { local: 'Galunggong', name: 'Round Scad' },
  { local: 'Tamban', name: 'Sardines' },
  { local: 'Matangbaka', name: 'Bigeye Scad' },
  { local: 'Tulingan', name: 'Mackerel Tuna' }
];

function quickAnalyzeSpecies(name) {
  router.push({ path: '/analyze', query: { species: name } });
}

function formatDate(dStr) {
  if (!dStr) return '';
  const d = new Date(dStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function getBadgeClass(cls) {
  const norm = (cls || '').toLowerCase();
  if (norm.includes('moderately')) return 'badge-moderate';
  if (norm === 'not fresh')        return 'badge-less-fresh';
  if (norm.includes('spoiled') || norm.includes('bilasa')) return 'badge-not-fresh';
  return 'badge-fresh';
}

onMounted(async () => {
  try {
    const res = await ApiService.getPredictions({ limit: 4 });
    if (res.success) {
      recentScans.value = res.predictions || [];
      stats.value.totalUserScans = res.total || recentScans.value.length;
      stats.value.freshCount = recentScans.value.filter(s => (s.classification || '').toLowerCase() === 'fresh').length;
    }
  } catch (e) {
    console.error('Failed to load dashboard scans:', e);
  }
});
</script>

<style scoped>
.dashboard-view {
  padding: 2.5rem 1.25rem;
}

.welcome-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  padding: 2.5rem;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(20, 184, 166, 0.08));
}

@media (max-width: 850px) {
  .welcome-card {
    flex-direction: column;
    align-items: flex-start;
  }
}

.welcome-left h1 {
  font-size: 2.2rem;
  margin: 0.5rem 0 0.75rem;
}

.welcome-sub {
  color: var(--text-muted);
  font-size: 0.95rem;
  max-width: 580px;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.welcome-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stats-mini-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.85rem;
}

@media (max-width: 600px) {
  .stats-mini-grid {
    grid-template-columns: 1fr;
  }
}

.mini-stat-card {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid var(--border-glass);
  padding: 1rem;
  border-radius: var(--radius-sm);
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  font-family: var(--font-heading);
  color: var(--text-white);
}

.stat-lbl {
  font-size: 0.72rem;
  color: var(--text-dim);
}

.text-emerald { color: var(--color-fresh); }
.text-cyan { color: var(--primary); }

.my-4 { margin: 2rem 0; }

.panel-card {
  padding: 1.5rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.species-chips-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.65rem;
}

@media (max-width: 600px) {
  .species-chips-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.species-chip-btn {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  padding: 0.6rem 0.5rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all var(--transition-fast);
}

.species-chip-btn:hover {
  background: var(--primary-glow);
  border-color: var(--primary);
  transform: translateY(-2px);
}

.sp-icon { font-size: 1.2rem; }
.sp-name { font-size: 0.85rem; font-weight: 700; color: var(--text-white); }
.sp-sub { font-size: 0.68rem; color: var(--text-dim); }

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.cat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius-sm);
}

.cat-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: right;
}

.empty-state {
  text-align: center;
  padding: 2.5rem;
  color: var(--text-muted);
}

.recent-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

@media (max-width: 900px) {
  .recent-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 550px) {
  .recent-grid {
    grid-template-columns: 1fr;
  }
}

.scan-card {
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
}

.scan-img-wrap {
  position: relative;
  width: 100%;
  height: 140px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.scan-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.scan-confidence-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(0, 0, 0, 0.75);
  color: var(--primary);
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.scan-date {
  font-size: 0.72rem;
  color: var(--text-dim);
}

.scan-species {
  font-size: 0.95rem;
  margin: 0.2rem 0 0.4rem;
}

.w-full { width: 100%; }
.mt-2 { margin-top: 0.5rem; }
.text-sm { font-size: 0.82rem; }
</style>
