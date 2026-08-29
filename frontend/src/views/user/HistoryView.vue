<template>
  <div class="history-view container">
    <div class="page-header flex-between">
      <div>
        <span class="badge badge-cyan">Personal Archives</span>
        <h1>Prediction History</h1>
        <p class="subtitle">Search and review your past fish freshness assessments</p>
      </div>
      <router-link to="/analyze" class="btn btn-primary btn-sm">
        + Scan New Fish
      </router-link>
    </div>

    <!-- Filters & Search Bar -->
    <div class="glass-card filters-card">
      <div class="filters-grid">
        <div class="filter-item search-item">
          <input 
            v-model="searchQuery" 
            @input="debounceFetch" 
            type="text" 
            class="input-field" 
            placeholder="Search by species, category, or note..." 
          />
        </div>
        <div class="filter-item">
          <select v-model="selectedCategory" @change="fetchHistory" class="input-field">
            <option value="">All Freshness Classes</option>
            <option value="Fresh">Fresh</option>
            <option value="Moderately Fresh">Moderately Fresh</option>
            <option value="Not Fresh">Not Fresh</option>
            <option value="Spoiled">Spoiled</option>
          </select>
        </div>
        <div class="filter-item">
          <select v-model="selectedSpecies" @change="fetchHistory" class="input-field">
            <option value="">All Fish Species</option>
            <option v-for="sp in speciesOptions" :key="sp.id" :value="sp.name">
              {{ sp.local_name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Predictions List -->
    <div v-if="isLoading" class="loading-state text-center">
      <p>Loading history records...</p>
    </div>

    <div v-else-if="predictions.length === 0" class="glass-card empty-state text-center">
      <p>No matching predictions found in your history.</p>
      <router-link to="/analyze" class="btn btn-primary btn-sm mt-2">Analyze a Fish</router-link>
    </div>

    <div v-else class="history-table-card glass-card">
      <table class="history-table">
        <thead>
          <tr>
            <th>Specimen</th>
            <th>Species</th>
            <th>Freshness Class</th>
            <th>AI Confidence</th>
            <th>Model Version</th>
            <th>Date & Time</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in predictions" :key="item.id">
            <td class="col-thumb">
              <img :src="item.image_url" alt="Fish" class="table-thumb" />
            </td>
            <td class="col-species">
              <strong>{{ item.species_local_name || item.species_name || 'Fish Specimen' }}</strong>
            </td>
            <td>
              <span class="badge" :class="getBadgeClass(item.classification)">
                {{ item.classification }}
              </span>
            </td>
            <td class="col-conf">
              <span class="conf-pct">{{ Math.round(item.confidence * 100) }}%</span>
            </td>
            <td class="col-ver">
              <span class="ver-code">{{ item.model_version }}</span>
            </td>
            <td class="col-date">{{ formatDate(item.created_at) }}</td>
            <td class="col-actions">
              <router-link :to="'/result/' + item.id" class="btn btn-secondary btn-sm">
                View Result
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '../../services/api';

const predictions = ref([]);
const speciesOptions = ref([]);
const searchQuery = ref('');
const selectedCategory = ref('');
const selectedSpecies = ref('');
const isLoading = ref(false);

let debounceTimer = null;
function debounceFetch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchHistory();
  }, 300);
}

async function fetchHistory() {
  isLoading.value = true;
  try {
    const params = {};
    if (searchQuery.value) params.search = searchQuery.value;
    if (selectedCategory.value) params.category = selectedCategory.value;
    if (selectedSpecies.value) params.species = selectedSpecies.value;

    const res = await ApiService.getPredictions(params);
    if (res.success) {
      predictions.value = res.predictions || [];
    }
  } catch (e) {
    console.error('Failed to load history:', e);
  } finally {
    isLoading.value = false;
  }
}

function formatDate(dStr) {
  if (!dStr) return '';
  return new Date(dStr).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function getBadgeClass(cls) {
  const norm = (cls || '').toLowerCase();
  if (norm.includes('moderately')) return 'badge-moderate';
  if (norm === 'not fresh')        return 'badge-less-fresh';
  if (norm.includes('spoiled') || norm.includes('bilasa')) return 'badge-not-fresh';
  return 'badge-fresh';
}

onMounted(async () => {
  fetchHistory();
  try {
    const spRes = await ApiService.getSpecies();
    if (spRes.success) speciesOptions.value = spRes.species;
  } catch (e) {}
});
</script>

<style scoped>
.history-view {
  padding: 3rem 1.25rem;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.filters-card {
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
}

.history-table-card {
  padding: 0.5rem;
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  text-align: left;
}

.history-table th {
  padding: 0.85rem 1rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-glass);
}

.history-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  vertical-align: middle;
}

.table-thumb {
  width: 52px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.conf-pct {
  font-weight: 700;
  color: var(--primary);
}

.ver-code {
  font-size: 0.75rem;
  color: var(--text-dim);
}

.col-date {
  font-size: 0.8rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.empty-state {
  padding: 3rem;
  color: var(--text-muted);
}

.mt-2 { margin-top: 0.75rem; }
</style>
