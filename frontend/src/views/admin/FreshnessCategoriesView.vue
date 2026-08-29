<template>
  <div class="categories-admin-view container">
    <div class="page-header">
      <span class="badge badge-cyan">Taxonomy Configuration</span>
      <h1>Freshness Category Management</h1>
      <p class="subtitle">Customize category names, Filipino/Tagalog labels, observable criteria, and culinary advice</p>
    </div>

    <!-- Categories List Grid -->
    <div class="grid-2 mb-4">
      <div v-for="cat in categories" :key="cat.id" class="glass-card cat-edit-card">
        <div class="cat-card-top">
          <div>
            <span class="badge" :class="getBadgeClass(cat.name)">{{ cat.name }}</span>
            <h3>{{ cat.name }} <span class="tagalog-sub">({{ cat.tagalog_name }})</span></h3>
          </div>
          <button @click="openEditModal(cat)" class="btn btn-secondary btn-sm">
            ✏️ Edit Category
          </button>
        </div>

        <div class="cat-field">
          <span class="field-lbl">English Description:</span>
          <p class="field-val">{{ cat.description }}</p>
        </div>

        <div class="cat-field">
          <span class="field-lbl">Culinary Recommendation (EN):</span>
          <p class="field-val">{{ cat.recommendation }}</p>
        </div>

        <div class="cat-field">
          <span class="field-lbl">Tagalog Advice (TL):</span>
          <p class="field-val text-dim"><em>"{{ cat.recommendation_tagalog }}"</em></p>
        </div>

        <div class="cat-indicators-box">
          <span class="field-lbl">Visual Indicator Rules:</span>
          <ul class="indicators-sublist">
            <li v-for="(v, vIdx) in cat.visual_characteristics" :key="vIdx">{{ v }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingCat" class="modal-backdrop" @click.self="editingCat = null">
      <div class="glass-card modal-card">
        <div class="modal-header">
          <h3>Edit {{ editingCat.name }}</h3>
          <button @click="editingCat = null" class="btn-close">&times;</button>
        </div>
        <form @submit.prevent="saveCategory" class="edit-form">
          <div class="form-group">
            <label>Category Name (EN)</label>
            <input v-model="editingCat.name" type="text" class="input-field" required />
          </div>
          <div class="form-group">
            <label>Tagalog Label (TL)</label>
            <input v-model="editingCat.tagalog_name" type="text" class="input-field" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editingCat.description" class="input-field txt-area" required></textarea>
          </div>
          <div class="form-group">
            <label>Recommendation (EN)</label>
            <textarea v-model="editingCat.recommendation" class="input-field txt-area" required></textarea>
          </div>
          <div class="form-group">
            <label>Recommendation (TL)</label>
            <textarea v-model="editingCat.recommendation_tagalog" class="input-field txt-area" required></textarea>
          </div>
          <button type="submit" class="btn btn-primary btn-lg w-full">Save Changes</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '../../services/api';

const categories = ref([]);
const editingCat = ref(null);

function getBadgeClass(cls) {
  const norm = (cls || '').toLowerCase();
  if (norm.includes('moderately')) return 'badge-moderate';
  if (norm.includes('less')) return 'badge-less-fresh';
  if (norm.includes('not') || norm.includes('bilasa')) return 'badge-not-fresh';
  return 'badge-fresh';
}

function openEditModal(cat) {
  editingCat.value = JSON.parse(JSON.stringify(cat));
}

async function loadCategories() {
  try {
    const res = await ApiService.getCategories();
    if (res.success) {
      categories.value = res.categories || [];
    }
  } catch (e) {
    console.error('Failed to load categories:', e);
  }
}

async function saveCategory() {
  if (!editingCat.value) return;
  try {
    const res = await ApiService.updateCategory(editingCat.value.id, editingCat.value);
    if (res.success) {
      editingCat.value = null;
      await loadCategories();
    }
  } catch (e) {
    alert('Error saving category: ' + e.message);
  }
}

onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.categories-admin-view {
  padding: 3rem 1.25rem;
}

.page-header {
  margin-bottom: 2.5rem;
}

.cat-edit-card {
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cat-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 0.85rem;
}

.cat-card-top h3 {
  font-size: 1.2rem;
  margin-top: 0.35rem;
}

.tagalog-sub {
  font-size: 0.85rem;
  color: var(--text-dim);
}

.cat-field {
  display: flex;
  flex-direction: column;
}

.field-lbl {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 0.2rem;
}

.field-val {
  font-size: 0.85rem;
  color: var(--text-main);
  line-height: 1.45;
}

.indicators-sublist {
  margin: 0.4rem 0 0 1.25rem;
  font-size: 0.82rem;
  color: var(--text-main);
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1.5rem;
}

.modal-card {
  max-width: 550px;
  width: 100%;
  padding: 2rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.txt-area {
  height: 65px;
  resize: vertical;
}

.w-full { width: 100%; }
.mb-4 { margin-bottom: 2rem; }
</style>
