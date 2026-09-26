<template>
  <div class="my-stall-view container">
    <div class="page-header">
      <span class="badge badge-cyan">Vendor</span>
      <h1>My Stall</h1>
      <p class="subtitle">
        Manage your stall profile. Every fish you scan while signed in is automatically
        attributed to your stall and builds your public freshness reputation.
      </p>
    </div>

    <div v-if="isLoading" class="loading-state text-center">
      <p>Loading...</p>
    </div>

    <template v-else>
      <!-- Live reputation summary (only if stall exists) -->
      <div v-if="hasStall && stall.stats" class="stat-tiles">
        <div class="glass-card tile">
          <strong>{{ stall.stats.freshness_percentage !== null ? stall.stats.freshness_percentage + '%' : '—' }}</strong>
          <span>Freshness rate</span>
        </div>
        <div class="glass-card tile">
          <strong>{{ stall.stats.total_scans }}</strong>
          <span>Total scans</span>
        </div>
        <div class="glass-card tile">
          <strong>{{ stall.stats.scans_today }}</strong>
          <span>Scans today</span>
        </div>
        <div class="glass-card tile">
          <router-link v-if="hasStall" :to="`/stalls/${stall.id}`" class="view-public-link">
            View public profile &rarr;
          </router-link>
        </div>
      </div>

      <!-- Create / edit form -->
      <div class="glass-card form-card">
        <h3>{{ hasStall ? 'Edit stall details' : 'Register your stall' }}</h3>

        <div v-if="message" class="form-message" :class="messageType">{{ message }}</div>

        <div class="form-grid">
          <label class="field">
            <span>Stall name *</span>
            <input v-model="form.name" type="text" class="input-field" placeholder="e.g. Mang Berting's Fresh Catch" />
          </label>
          <label class="field">
            <span>Market</span>
            <input v-model="form.market_name" type="text" class="input-field" placeholder="Roxas Public Market" />
          </label>
          <label class="field">
            <span>Section / Stall number</span>
            <input v-model="form.section" type="text" class="input-field" placeholder="Wet Section — Stall 14" />
          </label>
          <label class="field">
            <span>Contact number</span>
            <input v-model="form.contact_number" type="text" class="input-field" placeholder="0917-000-0000" />
          </label>
          <label class="field field-full">
            <span>Description</span>
            <textarea v-model="form.description" class="input-field" rows="3" placeholder="What you sell, where your catch comes from..."></textarea>
          </label>
        </div>

        <button class="btn btn-primary" :disabled="isSaving || !form.name.trim()" @click="save">
          {{ isSaving ? 'Saving...' : (hasStall ? 'Save changes' : 'Register stall') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import ApiService from '../../services/api';

const isLoading = ref(true);
const isSaving = ref(false);
const hasStall = ref(false);
const stall = ref(null);
const message = ref('');
const messageType = ref('success');

const form = reactive({
  name: '',
  market_name: 'Roxas Public Market',
  section: '',
  contact_number: '',
  description: '',
});

function fillForm(s) {
  form.name = s.name || '';
  form.market_name = s.market_name || 'Roxas Public Market';
  form.section = s.section || '';
  form.contact_number = s.contact_number || '';
  form.description = s.description || '';
}

async function fetchMyStall() {
  isLoading.value = true;
  try {
    const res = await ApiService.getMyStall();
    if (res.success && res.stall) {
      hasStall.value = true;
      stall.value = res.stall;
      fillForm(res.stall);
    } else {
      hasStall.value = false;
    }
  } catch (e) {
    console.error('Failed to load stall:', e);
  } finally {
    isLoading.value = false;
  }
}

async function save() {
  isSaving.value = true;
  message.value = '';
  try {
    let res;
    if (hasStall.value) {
      res = await ApiService.updateStall(stall.value.id, { ...form });
    } else {
      res = await ApiService.createStall({ ...form });
    }
    if (res.success) {
      hasStall.value = true;
      stall.value = res.stall;
      fillForm(res.stall);
      messageType.value = 'success';
      message.value = hasStall.value ? 'Stall saved successfully.' : 'Stall registered.';
    } else {
      messageType.value = 'error';
      message.value = res.message || 'Something went wrong.';
    }
  } catch (e) {
    messageType.value = 'error';
    message.value = e.message || 'Failed to save stall.';
  } finally {
    isSaving.value = false;
  }
}

onMounted(fetchMyStall);
</script>

<style scoped>
.my-stall-view { padding: 2rem 0 4rem; }
.page-header { margin-bottom: 1.75rem; }
.page-header h1 { margin: 0.5rem 0; }
.subtitle { color: var(--text-muted); max-width: 640px; }

.stat-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.tile { padding: 1.1rem; text-align: center; display: flex; flex-direction: column; justify-content: center; }
.tile strong { display: block; font-size: 1.5rem; color: var(--text-white, #fff); }
.tile span { font-size: 0.75rem; color: var(--text-muted); }
.view-public-link { color: var(--primary, #0ea5e9); font-size: 0.85rem; font-weight: 600; }

.form-card { padding: 1.75rem; }
.form-card h3 { margin: 0 0 1.25rem; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field-full { grid-column: 1 / -1; }
.field span { font-size: 0.8rem; color: var(--text-muted); }
textarea.input-field { resize: vertical; font-family: inherit; }

.form-message {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
.form-message.success { background: rgba(34,197,94,0.12); color: #22c55e; }
.form-message.error   { background: rgba(239,68,68,0.12); color: #ef4444; }

.loading-state { padding: 3rem 1rem; }
</style>
