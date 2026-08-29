<template>
  <div class="dataset-upload-view container container-narrow">
    <div class="page-header flex-between">
      <div>
        <span class="badge badge-cyan">Research Dataset Ingestion</span>
        <h1>Add Annotated Fish Specimen</h1>
        <p class="subtitle">Upload and tag fish imagery with ground truth labels and environmental metadata</p>
      </div>
      <router-link to="/admin/dataset" class="btn btn-secondary btn-sm">
        &larr; Back to Dataset
      </router-link>
    </div>

    <div class="glass-card upload-form-card">
      <div v-if="successMsg" class="success-alert mb-4">
        {{ successMsg }}
      </div>
      <div v-if="errorMsg" class="error-alert mb-4">
        {{ errorMsg }}
      </div>

      <form @submit.prevent="handleSubmit" class="specimen-form">
        <!-- Image File Picker -->
        <div class="form-group">
          <label>Specimen Photograph (JPG, PNG, WEBP)</label>
          <input 
            type="file" 
            ref="fileInputRef"
            @change="handleFileChange" 
            accept="image/jpeg,image/png,image/webp" 
            class="input-field file-field" 
            required 
          />
          <div v-if="previewUrl" class="preview-box mt-2">
            <img :src="previewUrl" alt="Specimen Preview" class="upload-preview-img" />
          </div>
        </div>

        <div class="grid-2">
          <div class="form-group">
            <label>Fish Species</label>
            <select v-model="form.species_id" class="input-field" required>
              <option v-for="sp in speciesList" :key="sp.id" :value="sp.id">
                {{ sp.local_name }} ({{ sp.name }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Ground Truth Freshness</label>
            <select v-model="form.freshness_category_id" class="input-field" required>
              <option value="1">Fresh (Sariwa)</option>
              <option value="2">Moderately Fresh</option>
              <option value="3">Less Fresh</option>
              <option value="4">Not Fresh (Bilasa)</option>
            </select>
          </div>
        </div>

        <div class="grid-3">
          <div class="form-group">
            <label>Dataset Split</label>
            <select v-model="form.split" class="input-field" required>
              <option value="train">Training (70%)</option>
              <option value="validation">Validation (15%)</option>
              <option value="test">Testing (15%)</option>
            </select>
          </div>

          <div class="form-group">
            <label>Lighting Condition</label>
            <select v-model="form.lighting_condition" class="input-field">
              <option value="Normal">Normal Lighting</option>
              <option value="Bright">Bright / Direct Sunlight</option>
              <option value="Dim">Dim / Market Stall Shadow</option>
            </select>
          </div>

          <div class="form-group">
            <label>Background</label>
            <select v-model="form.background_condition" class="input-field">
              <option value="Wet-market">Wet-Market Ice & Basin</option>
              <option value="Clean">Clean Plain Background</option>
              <option value="Cluttered">Cluttered Stall Counter</option>
            </select>
          </div>
        </div>

        <div class="grid-3">
          <div class="form-group">
            <label>Fish Orientation</label>
            <select v-model="form.fish_orientation" class="input-field">
              <option value="Side">Side View (Full Body)</option>
              <option value="Angled">Angled Perspective</option>
              <option value="Front">Frontal Snout View</option>
              <option value="Partial view">Partial View / Head Close-up</option>
            </select>
          </div>

          <div class="form-group">
            <label>Camera Distance</label>
            <select v-model="form.distance_condition" class="input-field">
              <option value="Medium">Medium (Standard)</option>
              <option value="Close">Close Macro</option>
              <option value="Far">Far / Wide Shot</option>
            </select>
          </div>

          <div class="form-group">
            <label>Image Quality</label>
            <select v-model="form.image_quality" class="input-field">
              <option value="High">High Resolution</option>
              <option value="Medium">Medium Quality</option>
              <option value="Low">Low / Grainy</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Collection Source / Market Location</label>
          <input 
            v-model="form.source" 
            type="text" 
            class="input-field" 
            placeholder="e.g. Roxas Public Wet Market, Stall 7, Oriental Mindoro" 
          />
        </div>

        <button type="submit" class="btn btn-primary btn-lg" :disabled="isLoading">
          <span v-if="isLoading">Uploading & Ingesting Specimen...</span>
          <span v-else>Save Dataset Specimen</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '../../services/api';

const speciesList = ref([]);
const fileInputRef = ref(null);
const selectedFile = ref(null);
const previewUrl = ref(null);
const isLoading = ref(false);
const successMsg = ref('');
const errorMsg = ref('');

const form = ref({
  species_id: 1,
  freshness_category_id: 1,
  split: 'train',
  lighting_condition: 'Normal',
  background_condition: 'Wet-market',
  fish_orientation: 'Side',
  distance_condition: 'Medium',
  image_quality: 'High',
  source: 'Roxas Public Wet Market, Oriental Mindoro'
});

function handleFileChange(e) {
  const file = e.target.files[0];
  if (file) {
    selectedFile.value = file;
    const reader = new FileReader();
    reader.onload = (ev) => {
      previewUrl.value = ev.target.result;
    };
    reader.readAsDataURL(file);
  }
}

async function handleSubmit() {
  if (!selectedFile.value) {
    errorMsg.value = 'Please select a fish specimen image file.';
    return;
  }

  isLoading.value = true;
  successMsg.value = '';
  errorMsg.value = '';

  const formData = new FormData();
  formData.append('image', selectedFile.value);
  for (const key in form.value) {
    formData.append(key, form.value[key]);
  }

  try {
    const res = await ApiService.uploadDatasetImage(formData);
    if (res.success) {
      successMsg.value = 'Dataset specimen added successfully!';
      selectedFile.value = null;
      previewUrl.value = null;
      if (fileInputRef.value) fileInputRef.value.value = '';
    }
  } catch (err) {
    errorMsg.value = err.message || 'Failed to upload specimen.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  try {
    const res = await ApiService.getSpecies();
    if (res.success) speciesList.value = res.species;
  } catch (e) {}
});
</script>

<style scoped>
.dataset-upload-view {
  padding: 3rem 1.25rem;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.upload-form-card {
  padding: 2.5rem;
}

.specimen-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-white);
  margin-bottom: 0.35rem;
}

.preview-box {
  width: 100%;
  max-height: 240px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #000;
}

.upload-preview-img {
  width: 100%;
  max-height: 240px;
  object-fit: cover;
}

.success-alert {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #a7f3d0;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.error-alert {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.mt-2 { margin-top: 0.5rem; }
.mb-4 { margin-bottom: 1.5rem; }
</style>
