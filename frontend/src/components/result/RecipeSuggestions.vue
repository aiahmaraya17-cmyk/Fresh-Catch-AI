<template>
  <div class="recipe-section glass-card">
    <div class="recipe-header">
      <h4>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/>
          <path d="M7 2v20"/>
          <path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>
        </svg>
        Filipino Recipe Suggestions
      </h4>
      <span class="recipe-source" v-if="cuisine">{{ cuisine }} cuisine</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="recipe-loading">
      <div class="mini-spinner"></div>
      <span>Fetching fresh recipe ideas…</span>
    </div>

    <!-- Unsafe / no recipes -->
    <div v-else-if="!available" class="recipe-unavailable" :class="{ 'is-unsafe': reason === 'no_recipes_unsafe' }">
      <svg v-if="reason === 'no_recipes_unsafe'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/><line x1="4.9" y1="4.9" x2="19.1" y2="19.1"/>
      </svg>
      <p>{{ message }}</p>
    </div>

    <!-- Recipe cards -->
    <div v-else class="recipe-grid">
      <div v-for="r in recipes" :key="r.id" class="recipe-card" @click="openRecipe(r)">
        <div class="recipe-thumb">
          <img v-if="r.thumbnail && !broken[r.id]" :src="r.thumbnail" :alt="r.name" loading="lazy" @error="onImgError(r.id)" />
          <div v-else class="recipe-thumb-fallback">🐟</div>
          <span v-if="r.isRaw" class="raw-badge">Raw · Fresh only</span>
        </div>
        <div class="recipe-body">
          <h5>{{ r.name }}</h5>
          <span class="recipe-area">{{ r.cooking_method || r.area }}</span>
          <span class="recipe-count">{{ r.ingredients.length }} ingredients · {{ r.steps.length }} steps</span>
        </div>
      </div>
    </div>

    <!-- Recipe detail modal -->
    <Transition name="modal-fade">
      <div v-if="selected" class="recipe-modal-overlay" @click.self="selected = null">
        <div class="recipe-modal">
          <button class="modal-close" @click="selected = null" aria-label="Close">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <img v-if="selected.thumbnail && !broken[selected.id]" :src="selected.thumbnail" :alt="selected.name" class="modal-thumb" @error="onImgError(selected.id)" />
          <div class="modal-content">
            <h3>{{ selected.name }}</h3>
            <p class="modal-meta">
              {{ selected.category }}<span v-if="selected.cooking_method"> · {{ selected.cooking_method }}</span>
              <span v-if="selected.prep_time_mins"> · {{ selected.prep_time_mins }} min</span>
            </p>
            <p v-if="selected.description" class="modal-desc">{{ selected.description }}</p>

            <h4>Ingredients</h4>
            <ul class="ingredient-list">
              <li v-for="(ing, i) in selected.ingredients" :key="i">{{ ing }}</li>
            </ul>

            <h4>Instructions</h4>
            <ol class="step-list">
              <li v-for="(step, i) in selected.steps" :key="i">{{ step }}</li>
            </ol>

            <div class="modal-links">
              <a v-if="selected.youtube" :href="selected.youtube" target="_blank" rel="noopener" class="btn btn-secondary btn-sm">
                Watch Video
              </a>
              <a v-if="selected.source" :href="selected.source" target="_blank" rel="noopener" class="btn btn-outline btn-sm">
                Original Source
              </a>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import ApiService from '../../services/api';

const props = defineProps({
  classification: { type: String, default: '' },
  species:        { type: String, default: '' },
});

const loading   = ref(false);
const available = ref(false);
const recipes   = ref([]);
const cuisine   = ref('Filipino');
const reason    = ref('');
const message   = ref('');
const selected  = ref(null);
const broken    = ref({});   // recipe id → true if its thumbnail failed to load

async function loadRecipes() {
  if (!props.classification) return;
  loading.value = true;
  broken.value = {};
  try {
    const res = await ApiService.getRecipes(props.classification, props.species, 6);
    available.value = res.available;
    recipes.value   = res.recipes || [];
    cuisine.value   = res.cuisine || 'Filipino';
    reason.value    = res.reason || '';
    message.value   = res.message || '';
  } catch (e) {
    available.value = false;
    reason.value    = 'api_unavailable';
    message.value   = 'Recipe service is temporarily unavailable. Please try again later.';
  } finally {
    loading.value = false;
  }
}

function openRecipe(r) {
  selected.value = r;
}

function onImgError(id) {
  // Fall back to the 🐟 placeholder (never leave an empty box).
  broken.value = { ...broken.value, [id]: true };
}

onMounted(loadRecipes);
watch(() => [props.classification, props.species], loadRecipes);
</script>

<style scoped>
.recipe-section { padding: 1.25rem; }

.recipe-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;
}
.recipe-header h4 {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 1rem; color: var(--text-white);
}
.recipe-source {
  font-size: 0.7rem; font-weight: 600; color: var(--accent-teal);
  background: rgba(20,184,166,0.12); padding: 0.2rem 0.55rem;
  border-radius: var(--radius-full);
}

/* Loading */
.recipe-loading {
  display: flex; align-items: center; gap: 0.75rem;
  color: var(--text-muted); font-size: 0.88rem; padding: 1rem 0;
}
.mini-spinner {
  width: 22px; height: 22px;
  border: 3px solid rgba(14,165,233,0.2);
  border-top-color: var(--primary);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Unavailable / unsafe */
.recipe-unavailable {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.9rem 1rem; border-radius: var(--radius-sm);
  background: rgba(255,255,255,0.04); color: var(--text-muted);
  font-size: 0.85rem; line-height: 1.4;
}
.recipe-unavailable.is-unsafe {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.3);
  color: #fca5a5;
}

/* Grid */
.recipe-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.9rem;
}
.recipe-card {
  background: rgba(0,0,0,0.25);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  overflow: hidden; cursor: pointer;
  transition: transform 0.15s, border-color 0.15s;
}
.recipe-card:hover {
  transform: translateY(-3px);
  border-color: var(--primary);
}
.recipe-thumb { position: relative; aspect-ratio: 4/3; overflow: hidden; background: #0a1420;
  display: flex; align-items: center; justify-content: center; }
.recipe-thumb img { width: 100%; height: 100%; object-fit: cover; }
.recipe-thumb-fallback {
  font-size: 2.2rem;
  opacity: 0.5;
}
.raw-badge {
  position: absolute; top: 6px; left: 6px;
  background: rgba(16,185,129,0.9); color: #fff;
  font-size: 0.62rem; font-weight: 700;
  padding: 0.12rem 0.4rem; border-radius: 4px;
}
.recipe-body { padding: 0.6rem 0.7rem; display: flex; flex-direction: column; gap: 0.15rem; }
.recipe-body h5 {
  font-size: 0.82rem; color: var(--text-white); line-height: 1.25;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.recipe-area  { font-size: 0.68rem; color: var(--primary); font-weight: 600; }
.recipe-count { font-size: 0.66rem; color: var(--text-dim); }

/* Modal */
.recipe-modal-overlay {
  position: fixed; inset: 0; z-index: 300;
  background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.recipe-modal {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  max-width: 640px; width: 100%;
  max-height: 88vh; overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
.modal-close {
  position: absolute; top: 0.75rem; right: 0.75rem; z-index: 2;
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(0,0,0,0.6); border: none; color: #fff;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.modal-thumb { width: 100%; max-height: 260px; object-fit: cover; display: block; }
.modal-content { padding: 1.25rem; }
.modal-content h3 { font-size: 1.25rem; margin-bottom: 0.2rem; }
.modal-meta { font-size: 0.8rem; color: var(--primary); margin-bottom: 0.6rem; }
.modal-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 0.5rem; }
.modal-content h4 {
  font-size: 0.92rem; color: var(--text-white);
  margin: 1rem 0 0.5rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 0.3rem;
}
.ingredient-list { margin: 0 0 0 1.1rem; font-size: 0.85rem; color: var(--text-main); line-height: 1.6; }
.step-list { margin: 0 0 0 1.1rem; font-size: 0.85rem; color: var(--text-main); line-height: 1.65; }
.step-list li { margin-bottom: 0.5rem; }
.modal-links { display: flex; gap: 0.6rem; margin-top: 1.25rem; flex-wrap: wrap; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
