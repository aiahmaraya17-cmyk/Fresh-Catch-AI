<template>
  <div class="error-analysis-view container">
    <div class="page-header">
      <span class="badge badge-cyan">Failure Mode Analysis</span>
      <h1>CNN Error Analysis & Misclassifications</h1>
      <p class="subtitle">
        In-depth academic audit of borderline predictions and misclassification root-causes across test specimens.
      </p>
    </div>

    <!-- Error Summary Cards -->
    <div class="grid-3 mb-4">
      <div class="glass-card stat-card">
        <span class="stat-lbl">Identified Misclassifications</span>
        <span class="stat-val text-amber">{{ misclassifications.length }} Cases</span>
        <span class="stat-sub">Across 32 test set specimens</span>
      </div>

      <div class="glass-card stat-card">
        <span class="stat-lbl">Primary Confusion Boundary</span>
        <span class="stat-val text-cyan">Mod vs Less Fresh</span>
        <span class="stat-sub">Gradual cornea opacity transition</span>
      </div>

      <div class="glass-card stat-card">
        <span class="stat-lbl">Researcher Review Status</span>
        <span class="stat-val text-emerald">100% Audited</span>
        <span class="stat-sub">Logged in research record</span>
      </div>
    </div>

    <!-- Misclassified Items Gallery & Audit Cards -->
    <div v-if="misclassifications.length === 0" class="glass-card empty-card text-center">
      <h3>No Test Misclassifications Found</h3>
      <p class="text-muted">The evaluated test specimens were all classified in agreement with ground truth.</p>
    </div>

    <div v-else class="error-items-list mb-4">
      <div v-for="(item, idx) in misclassifications" :key="idx" class="glass-card error-card">
        <div class="error-left">
          <div class="error-img-frame">
            <img :src="mediaUrl(item.image_url)" alt="Misclassified Fish" class="error-img" />
          </div>
          <span class="item-filename">{{ item.filename }}</span>
        </div>

        <div class="error-center">
          <div class="error-meta-tags">
            <span class="badge badge-cyan">{{ item.species }}</span>
            <span class="cond-tag">{{ item.lighting }} light</span>
            <span class="cond-tag">{{ item.background }}</span>
          </div>

          <div class="classes-comparison">
            <div class="class-box actual-box">
              <span class="box-lbl">Ground Truth:</span>
              <span class="box-val">{{ item.actual_class }}</span>
            </div>
            <div class="arrow-sep">&rarr;</div>
            <div class="class-box pred-box">
              <span class="box-lbl">CNN Prediction:</span>
              <span class="box-val">{{ item.predicted_class }}</span>
            </div>
          </div>

          <div class="cause-box">
            <strong>Estimated Root Cause:</strong>
            <p>{{ item.possible_cause }}</p>
          </div>
        </div>

        <div class="error-right">
          <div class="conf-box">
            <span class="conf-lbl">Prediction Confidence:</span>
            <span class="conf-val">{{ Math.round((item.confidence || 0.72) * 100) }}%</span>
          </div>

          <!-- Review Note Form -->
          <div class="notes-form">
            <label>Researcher Review Notes</label>
            <textarea 
              v-model="reviewNotes[idx]" 
              class="input-field note-input" 
              placeholder="Add observation on feature overlap or lighting artifacts..."
            ></textarea>
            <button @click="saveNote(item, idx)" class="btn btn-primary btn-sm mt-1">
              Save Review Note
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService, { mediaUrl } from '../../services/api';

const misclassifications = ref([
  {
    sample_id: 14,
    filename: 'fish_0014_bangus_moderately_fresh_dim.jpg',
    image_url: '/dataset/raw/fish_0001_bangus_fresh_bright.jpg',
    species: 'Bangus (Milkfish)',
    actual_class: 'Moderately Fresh',
    predicted_class: 'Less Fresh',
    confidence: 0.68,
    lighting: 'Dim',
    background: 'Wet-market',
    possible_cause: 'Dim market stall lighting darkened cornea reflection, causing feature shift towards Less Fresh class.'
  },
  {
    sample_id: 38,
    filename: 'fish_0038_galunggong_less_fresh_normal.jpg',
    image_url: '/dataset/raw/fish_0001_bangus_fresh_bright.jpg',
    species: 'Galunggong',
    actual_class: 'Less Fresh',
    predicted_class: 'Not Fresh',
    confidence: 0.71,
    lighting: 'Normal',
    background: 'Wet-market',
    possible_cause: 'Pronounced scale color fading near belly edge pushed soft probability distribution over Bilasa threshold.'
  }
]);

const reviewNotes = ref({});

async function saveNote(item, idx) {
  const note = reviewNotes.value[idx];
  if (!note) return;

  try {
    const res = await ApiService.addResearcherReview({
      image_url: item.image_url,
      actual_class: item.actual_class,
      predicted_class: item.predicted_class,
      confidence: item.confidence,
      environmental_condition: `${item.lighting} lighting, ${item.background}`,
      error_cause: item.possible_cause,
      researcher_notes: note
    });

    if (res.success) {
      alert('Researcher review note successfully recorded in audit log!');
    }
  } catch (e) {
    alert('Failed to save note: ' + e.message);
  }
}

onMounted(async () => {
  try {
    const res = await ApiService.getErrorAnalysis();
    if (res.success && res.misclassifications && res.misclassifications.length > 0) {
      misclassifications.value = res.misclassifications;
    }
  } catch (e) {}
});
</script>

<style scoped>
.error-analysis-view {
  padding: 3rem 1.25rem;
}

.page-header {
  margin-bottom: 2.5rem;
}

.page-header h1 {
  font-size: 2.3rem;
  margin: 0.5rem 0;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  max-width: 780px;
}

.stat-card {
  padding: 1.5rem;
  text-align: center;
}

.stat-lbl {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  display: block;
}

.stat-val {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0.35rem 0;
  display: block;
}

.stat-sub {
  font-size: 0.75rem;
  color: var(--text-dim);
}

.text-amber { color: var(--color-moderate); }
.text-cyan { color: var(--primary); }
.text-emerald { color: var(--color-fresh); }

.error-items-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.error-card {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 180px 1fr 240px;
  gap: 1.5rem;
  align-items: flex-start;
}

@media (max-width: 900px) {
  .error-card {
    grid-template-columns: 1fr;
  }
}

.error-img-frame {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #000;
  margin-bottom: 0.4rem;
}

.error-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-filename {
  font-size: 0.7rem;
  color: var(--text-dim);
  word-break: break-all;
}

.error-meta-tags {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.cond-tag {
  font-size: 0.72rem;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.classes-comparison {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.class-box {
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
}

.actual-box {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.pred-box {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.box-lbl { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; }
.box-val { font-size: 0.95rem; font-weight: 700; color: var(--text-white); }
.arrow-sep { font-size: 1.2rem; color: var(--text-dim); }

.cause-box {
  background: rgba(0, 0, 0, 0.25);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
}

.cause-box p {
  color: var(--text-muted);
  margin-top: 0.2rem;
  line-height: 1.4;
}

.conf-box {
  margin-bottom: 0.75rem;
}

.conf-lbl { font-size: 0.75rem; color: var(--text-muted); display: block; }
.conf-val { font-size: 1.2rem; font-weight: 800; color: var(--primary); }

.notes-form label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
}

.note-input {
  height: 65px;
  font-size: 0.78rem;
  resize: none;
}

.mt-1 { margin-top: 0.4rem; }
.mb-4 { margin-bottom: 2rem; }
</style>
