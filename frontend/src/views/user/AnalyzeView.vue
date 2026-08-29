<template>
  <div class="analyze-view container container-narrow">

    <!-- Page header -->
    <div class="page-header text-center">
      <span class="badge badge-cyan">AI Visual Classification</span>
      <h1>{{ t('analyze.title') }}</h1>
      <p class="subtitle">{{ t('analyze.subtitle') }}</p>
    </div>

    <!-- Mode tabs -->
    <div class="mode-tabs">
      <button class="tab-btn" :class="{ active: inputMode === 'camera' }" @click="switchMode('camera')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
          <circle cx="12" cy="13" r="3"/>
        </svg>
        {{ t('analyze.tabCamera') }}
      </button>
      <button class="tab-btn" :class="{ active: inputMode === 'upload' }" @click="switchMode('upload')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        {{ t('analyze.tabUpload') }}
      </button>
    </div>

    <!-- Species selector -->
    <div class="species-select-box glass-card">
      <label for="species-select">Fish Species <span class="optional-tag">(Optional)</span></label>
      <select id="species-select" v-model="selectedSpecies" class="input-field">
        <option value="">Auto-detect from image…</option>
        <option v-for="sp in speciesOptions" :key="sp.id" :value="sp.name">
          {{ sp.local_name }} ({{ sp.name }})
        </option>
      </select>
    </div>

    <!-- Workspace card -->
    <div class="glass-card workspace-card">

      <!-- ── Quality rejection banner ─────────────────────────────────── -->
      <Transition name="fade-up">
        <div v-if="qualityRejection" class="quality-rejection-card">
          <div class="rejection-icon-wrap">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-amber">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="rejection-body">
            <h4>Image Quality Insufficient</h4>
            <p>{{ qualityRejection.message }}</p>
            <ul v-if="qualityRejection.reasons?.length" class="rejection-reasons">
              <li v-for="(r, i) in qualityRejection.reasons" :key="i">{{ r }}</li>
            </ul>
          </div>
          <button @click="resetCapture" class="btn btn-primary btn-sm rejection-retry-btn">
            Try Again
          </button>
        </div>
      </Transition>

      <!-- ── Camera permission denied ───────────────────────────────── -->
      <Transition name="fade-up">
        <div v-if="cameraError" class="camera-error-card">
          <div class="camera-error-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
              <line x1="2" y1="2" x2="22" y2="22"/>
            </svg>
          </div>
          <div class="camera-error-body">
            <h4>Camera Access Denied</h4>
            <p>{{ cameraError }}</p>
            <p class="camera-error-hint">Allow camera access in your browser settings, or use the Upload tab to select an image from your device.</p>
          </div>
          <button @click="switchMode('upload')" class="btn btn-primary btn-sm">
            Use Upload Instead
          </button>
        </div>
      </Transition>

      <!-- ══════════════════════════════════════════════════════════════
           CAMERA MODE
      ════════════════════════════════════════════════════════════════ -->
      <div v-if="inputMode === 'camera' && !capturedImage && !cameraError" class="camera-workspace">

        <!-- Live viewfinder -->
        <div class="video-container scanner-container" :class="{ 'is-countdown': countdown > 0 }">
          <video ref="videoRef" autoplay playsinline muted class="camera-video"></video>

          <!-- Alignment HUD boxes -->
          <div class="viewfinder-hud">
            <div class="hud-box head-box"><span class="hud-tag">HEAD / EYE</span></div>
            <div class="hud-box gill-box"><span class="hud-tag">GILLS</span></div>
            <div class="hud-box body-box"><span class="hud-tag">BODY</span></div>
            <div class="hud-prompt">
              Align fish with the guide boxes · Good lighting needed
            </div>
          </div>

          <!-- Flash overlay on capture -->
          <Transition name="flash">
            <div v-if="flashVisible" class="capture-flash"></div>
          </Transition>

          <!-- Countdown overlay -->
          <Transition name="fade-scale">
            <div v-if="countdown > 0" class="countdown-overlay">
              <span class="countdown-number">{{ countdown }}</span>
            </div>
          </Transition>

          <!-- Big shutter button OVERLAID on the video (bottom-center) -->
          <div class="shutter-row">
            <!-- Switch camera (left) -->
            <button class="btn-icon-round" @click="toggleCameraFacing" title="Flip camera" :disabled="countdown > 0">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6"/>
                <path d="M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </button>

            <!-- Main shutter -->
            <button
              class="shutter-btn"
              :class="{ 'is-counting': countdown > 0 }"
              @click="startCapture"
              :disabled="countdown > 0"
              aria-label="Capture photo"
            >
              <span class="shutter-ring"></span>
              <span class="shutter-dot"></span>
            </button>

            <!-- Timer toggle (right) -->
            <button
              class="btn-icon-round"
              :class="{ active: timerEnabled }"
              @click="timerEnabled = !timerEnabled"
              :title="timerEnabled ? 'Timer ON (3s) — tap to disable' : 'Timer OFF — tap to enable 3s delay'"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span v-if="timerEnabled" class="timer-badge">3</span>
            </button>
          </div>
        </div>

        <!-- Tip strip below camera -->
        <div class="camera-tips">
          <span>💡 Tip: Hold phone steady · Aim in bright light · Fill frame with fish</span>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════════════
           UPLOAD MODE
      ════════════════════════════════════════════════════════════════ -->
      <div v-else-if="inputMode === 'upload' && !capturedImage" class="upload-workspace">
        <div
          class="dropzone-area"
          :class="{ 'drag-over': isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleFileDrop"
          @click="$refs.fileInput.click()"
        >
          <input
            type="file"
            ref="fileInput"
            @change="handleFileSelect"
            accept="image/jpeg,image/png,image/webp"
            class="hidden"
          />
          <div class="upload-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" class="text-cyan">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <h3>Tap to choose a photo</h3>
          <p>or drag &amp; drop here</p>
          <p class="dropzone-formats">JPG · PNG · WEBP · max 10 MB</p>
          <button type="button" class="btn btn-secondary btn-sm mt-2" @click.stop="$refs.fileInput.click()">
            Browse Files
          </button>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════════════
           PREVIEW + SUBMIT
      ════════════════════════════════════════════════════════════════ -->
      <div v-if="capturedImage" class="preview-workspace">
        <div class="preview-container scanner-container" :class="{ 'is-analyzing': isAnalyzing }">
          <div v-if="isAnalyzing" class="scanner-laser"></div>
          <img :src="capturedImage" alt="Fish preview" class="preview-image" />

          <!-- Analysing overlay -->
          <Transition name="fade-scale">
            <div v-if="isAnalyzing" class="analyzing-overlay">
              <div class="spinner"></div>
              <h3>{{ t('analyze.analyzingText') }}</h3>
              <p class="ticker-text">{{ currentTickerStep }}</p>
            </div>
          </Transition>
        </div>

        <!-- Action row -->
        <div class="preview-actions">
          <button @click="resetCapture" class="btn btn-secondary btn-lg" :disabled="isAnalyzing">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="1 4 1 10 7 10"/>
              <path d="M3.51 15a9 9 0 1 0 .49-4.36"/>
            </svg>
            {{ t('analyze.btnRetake') }}
          </button>
          <button @click="submitAnalysis" class="btn btn-primary btn-lg" :disabled="isAnalyzing">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polygon points="10 8 16 12 10 16 10 8"/>
            </svg>
            {{ isAnalyzing ? 'Analyzing…' : t('analyze.btnAnalyze') }}
          </button>
        </div>

        <!-- Image info bar -->
        <div v-if="imageInfo" class="image-info-bar">
          <span>{{ imageInfo }}</span>
        </div>
      </div>

    </div><!-- /workspace-card -->

    <DisclaimerBanner />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { translations } from '../../i18n/translations';
import DisclaimerBanner from '../../components/common/DisclaimerBanner.vue';
import ApiService from '../../services/api';

const router    = useRouter();
const route     = useRoute();
const authStore = useAuthStore();

// ── State ──────────────────────────────────────────────────────────────────
const inputMode      = ref('camera');
const selectedSpecies = ref('');
const speciesOptions  = ref([]);

const videoRef       = ref(null);
const mediaStream    = ref(null);
const facingMode     = ref('environment');   // rear camera by default

const capturedImage  = ref(null);
const selectedFile   = ref(null);
const isDragging     = ref(false);
const isAnalyzing    = ref(false);
const imageInfo      = ref('');

const qualityRejection = ref(null);
const cameraError      = ref('');
const currentTickerStep = ref('');

const timerEnabled   = ref(false);   // 3-second countdown toggle
const countdown      = ref(0);       // 3 → 2 → 1 → capture
const flashVisible   = ref(false);   // white flash on capture
let   countdownTimer = null;

// ── i18n ───────────────────────────────────────────────────────────────────
function t(path) {
  const lang = authStore.language || 'en';
  let cur = translations[lang] || translations.en;
  for (const k of path.split('.')) {
    if (cur?.[k] !== undefined) cur = cur[k]; else return path;
  }
  return cur;
}

// ── Camera helpers ─────────────────────────────────────────────────────────
async function startCamera() {
  stopCamera();
  cameraError.value = '';
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: facingMode.value },
        width:  { ideal: 1920 },
        height: { ideal: 1080 },
      },
      audio: false,
    });
    mediaStream.value = stream;
    if (videoRef.value) {
      videoRef.value.srcObject = stream;
      await videoRef.value.play().catch(() => {});
    }
  } catch (err) {
    let msg = 'Camera access was denied.';
    if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      msg = 'No camera found on this device.';
    } else if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      msg = 'Camera permission was denied. Please allow access in your browser/device settings.';
    } else if (err.name === 'NotReadableError') {
      msg = 'Camera is already in use by another app. Close other apps and try again.';
    } else if (err.name === 'OverconstrainedError') {
      // Retry with looser constraints
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        mediaStream.value = stream;
        if (videoRef.value) { videoRef.value.srcObject = stream; await videoRef.value.play().catch(() => {}); }
        return;
      } catch {
        msg = 'Could not start camera with the requested settings.';
      }
    }
    cameraError.value = msg;
  }
}

function stopCamera() {
  mediaStream.value?.getTracks().forEach(t => t.stop());
  mediaStream.value = null;
}

function toggleCameraFacing() {
  facingMode.value = facingMode.value === 'environment' ? 'user' : 'environment';
  startCamera();
}

// ── Capture flow ──────────────────────────────────────────────────────────
/**
 * Called when the shutter button is pressed.
 * If timer is enabled, counts down 3 → 2 → 1 then captures.
 * Otherwise captures immediately.
 */
function startCapture() {
  if (countdown.value > 0) return;   // already counting
  if (timerEnabled.value) {
    countdown.value = 3;
    countdownTimer = setInterval(() => {
      countdown.value -= 1;
      if (countdown.value <= 0) {
        clearInterval(countdownTimer);
        countdown.value = 0;
        doCapture();
      }
    }, 1000);
  } else {
    doCapture();
  }
}

function doCapture() {
  if (!videoRef.value) return;
  const video = videoRef.value;

  // Flash effect
  flashVisible.value = true;
  setTimeout(() => { flashVisible.value = false; }, 220);

  const canvas   = document.createElement('canvas');
  canvas.width   = video.videoWidth  || 1280;
  canvas.height  = video.videoHeight || 720;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  capturedImage.value = canvas.toDataURL('image/jpeg', 0.92);
  imageInfo.value     = `Camera · ${canvas.width}×${canvas.height}`;
  stopCamera();
}

// ── File upload ───────────────────────────────────────────────────────────
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) processFile(file);
}

function handleFileDrop(e) {
  isDragging.value = false;
  const file = e.dataTransfer.files[0];
  if (file) processFile(file);
}

function processFile(file) {
  // Basic client-side size check (10 MB)
  if (file.size > 10 * 1024 * 1024) {
    qualityRejection.value = {
      message: 'File is too large (max 10 MB). Please compress the image or use a smaller file.',
      reasons: [],
    };
    return;
  }
  selectedFile.value = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    capturedImage.value = e.target.result;
    const kb = (file.size / 1024).toFixed(0);
    imageInfo.value = `${file.name} · ${kb} KB`;
  };
  reader.readAsDataURL(file);
}

// ── Reset ─────────────────────────────────────────────────────────────────
function resetCapture() {
  capturedImage.value    = null;
  selectedFile.value     = null;
  qualityRejection.value = null;
  imageInfo.value        = '';
  if (inputMode.value === 'camera') startCamera();
}

// ── Mode switch ────────────────────────────────────────────────────────────
function switchMode(mode) {
  inputMode.value        = mode;
  qualityRejection.value = null;
  cameraError.value      = '';
  capturedImage.value    = null;
  if (mode === 'camera') {
    startCamera();
  } else {
    stopCamera();
  }
}

// ── Analysis ticker ────────────────────────────────────────────────────────
const TICKER_STEPS = [
  'Checking image quality…',
  'Segmenting fish body from background…',
  'Measuring eye clarity and corneal sharpness…',
  'Analysing gill colour (LAB a* redness)…',
  'Computing skin luster and body yellowing…',
  'Applying QIM freshness scoring…',
  'Generating recommendation…',
];

let tickerInterval = null;

function startTicker() {
  let i = 0;
  currentTickerStep.value = TICKER_STEPS[0];
  tickerInterval = setInterval(() => {
    i = (i + 1) % TICKER_STEPS.length;
    currentTickerStep.value = TICKER_STEPS[i];
  }, 900);
}

function stopTicker() {
  clearInterval(tickerInterval);
  tickerInterval = null;
}

// ── Submit analysis ────────────────────────────────────────────────────────
async function submitAnalysis() {
  if (!capturedImage.value || isAnalyzing.value) return;

  isAnalyzing.value      = true;
  qualityRejection.value = null;
  startTicker();

  try {
    let res;
    if (selectedFile.value) {
      const form = new FormData();
      form.append('image', selectedFile.value);
      if (selectedSpecies.value) form.append('species_name', selectedSpecies.value);
      res = await ApiService.analyzeImage(form);
    } else {
      // Camera capture (base64)
      res = await ApiService.analyzeImage(capturedImage.value);
    }

    stopTicker();
    isAnalyzing.value = false;

    if (res.success) {
      sessionStorage.setItem('freshcatch_active_result', JSON.stringify(res));
      router.push(`/result/${res.predictionId || 'latest'}`);
    } else {
      // Non-exception API failure
      qualityRejection.value = {
        message: res.message || 'Analysis failed. Please try another image.',
        reasons: res.quality_check?.reasons || [],
      };
    }
  } catch (err) {
    stopTicker();
    isAnalyzing.value = false;

    // Parse structured quality rejection from the API error
    let message = 'Analysis failed. Please try another image.';
    let reasons = [];

    try {
      // Some API layers serialise the error body
      const body = JSON.parse(err.message || '{}');
      if (body.message) message = body.message;
      if (body.quality_check?.reasons) reasons = body.quality_check.reasons;
      if (body.disclaimer) reasons.push(body.disclaimer.split('.')[0] + '.');
    } catch {
      message = err.message || message;
    }

    qualityRejection.value = { message, reasons };
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(async () => {
  if (route.query.species) selectedSpecies.value = route.query.species;

  try {
    const res = await ApiService.getSpecies();
    if (res.success) speciesOptions.value = res.species;
  } catch {}

  if (inputMode.value === 'camera') startCamera();
});

onUnmounted(() => {
  stopCamera();
  stopTicker();
  if (countdownTimer) clearInterval(countdownTimer);
});
</script>

<style scoped>
/* ── Page layout ──────────────────────────────────────────────────────────── */
.analyze-view {
  padding: clamp(1.25rem, 4vw, 2.75rem) 1.25rem clamp(3rem, 8vw, 5rem);
}

.page-header { margin-bottom: 1.5rem; }

.page-header h1 {
  font-size: clamp(1.45rem, 5vw, 2.2rem);
  margin: 0.5rem 0;
}

.subtitle { color: var(--text-muted); font-size: 0.93rem; }

/* ── Mode tabs ────────────────────────────────────────────────────────────── */
.mode-tabs {
  display: flex;
  gap: 0.65rem;
  margin-bottom: 1.1rem;
  flex-wrap: wrap;
}

.tab-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.72rem 1.25rem;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-muted);
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s;
  min-height: 44px;
}
.tab-btn.active {
  background: linear-gradient(135deg, var(--primary), #0284c7);
  color: #fff; border-color: var(--primary);
  box-shadow: 0 4px 14px var(--primary-glow);
}

/* ── Species selector ─────────────────────────────────────────────────────── */
.species-select-box {
  padding: 0.8rem 1.1rem;
  margin-bottom: 1.1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.species-select-box label {
  font-size: 0.83rem; font-weight: 600;
  color: var(--text-white); white-space: nowrap;
}
.optional-tag {
  font-size: 0.72rem; font-weight: 400;
  color: var(--text-dim); margin-left: 0.3rem;
}
.species-select-box .input-field { flex: 1; min-width: 180px; }

/* ── Workspace card ───────────────────────────────────────────────────────── */
.workspace-card {
  padding: clamp(0.85rem, 2.5vw, 1.35rem);
  overflow: hidden;
}

/* ── Quality rejection / camera error banners ─────────────────────────────── */
.quality-rejection-card,
.camera-error-card {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1.1rem 1.25rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1.1rem;
}
.quality-rejection-card {
  background: rgba(245,158,11,0.12);
  border: 1px solid rgba(245,158,11,0.38);
}
.camera-error-card {
  background: rgba(239,68,68,0.10);
  border: 1px solid rgba(239,68,68,0.35);
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.rejection-icon-wrap { flex-shrink: 0; margin-top: 0.1rem; }
.rejection-body      { flex: 1; min-width: 0; }
.rejection-body h4   { font-size: 0.92rem; color: #fde68a; margin-bottom: 0.25rem; }
.rejection-body p    { font-size: 0.83rem; color: #fef3c7; line-height: 1.4; }
.rejection-reasons   {
  margin: 0.5rem 0 0 1.2rem;
  font-size: 0.8rem; color: #fef3c7; line-height: 1.55;
}
.rejection-retry-btn { flex-shrink: 0; align-self: center; }

.camera-error-icon { color: #f87171; margin-bottom: 0.5rem; }
.camera-error-body h4 { color: #fca5a5; margin-bottom: 0.3rem; }
.camera-error-body p  { font-size: 0.85rem; color: #fecaca; }
.camera-error-hint    { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.4rem; }

/* ── Video / preview container ────────────────────────────────────────────── */
.video-container,
.preview-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  max-height: 62vw;          /* prevent giant video on desktop */
  min-height: 220px;
  background: #000;
  border-radius: var(--radius-md);
  overflow: hidden;
}
@media (min-width: 600px) {
  .video-container,
  .preview-container { max-height: 420px; }
}

.camera-video,
.preview-image {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
}

/* ── Viewfinder HUD boxes ─────────────────────────────────────────────────── */
.viewfinder-hud {
  position: absolute; inset: 0;
  pointer-events: none;
}
.hud-box {
  position: absolute;
  border: 1.5px dashed rgba(14,165,233,0.68);
  border-radius: 5px;
}
.head-box  { top:20%; left:12%; width:28%; height:40%; }
.gill-box  { top:28%; left:38%; width:18%; height:35%; border-color: rgba(20,184,166,0.7); }
.body-box  { top:22%; left:54%; width:34%; height:46%; }
.hud-tag {
  font-size: 0.58rem; font-weight: 800;
  color: #38bdf8; background: rgba(0,0,0,0.72);
  padding: 0.08rem 0.3rem; border-radius: 3px;
  display: inline-block;
}
.hud-prompt {
  position: absolute; bottom: 72px; left: 50%; transform: translateX(-50%);
  white-space: nowrap;
  background: rgba(0,0,0,0.62); backdrop-filter: blur(4px);
  padding: 0.35rem 0.85rem; border-radius: var(--radius-full);
  font-size: 0.7rem; color: rgba(255,255,255,0.88);
}
@media (max-width: 380px) {
  .hud-prompt { font-size: 0.62rem; bottom: 80px; }
}

/* ── Capture flash overlay ────────────────────────────────────────────────── */
.capture-flash {
  position: absolute; inset: 0;
  background: rgba(255,255,255,0.85);
  z-index: 30; pointer-events: none;
}
.flash-enter-active { transition: opacity 0.05s; }
.flash-leave-active { transition: opacity 0.18s ease; }
.flash-enter-from, .flash-leave-to { opacity: 0; }

/* ── Countdown overlay ────────────────────────────────────────────────────── */
.countdown-overlay {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.38); z-index: 20;
}
.countdown-number {
  font-size: clamp(3.5rem, 15vw, 6rem);
  font-weight: 900; font-family: var(--font-heading);
  color: #fff;
  text-shadow: 0 0 30px var(--primary), 0 4px 16px rgba(0,0,0,0.6);
  line-height: 1;
}
.fade-scale-enter-active { transition: all 0.22s cubic-bezier(.4,0,.2,1); }
.fade-scale-leave-active { transition: all 0.18s ease; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(0.7); }

/* ── Shutter row (overlaid on video bottom) ──────────────────────────────── */
.shutter-row {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(1.5rem, 6vw, 3rem);
  padding: clamp(0.75rem, 3vw, 1.25rem) 1rem;
  background: linear-gradient(transparent, rgba(0,0,0,0.72));
  z-index: 10;
}

/* The big shutter button */
.shutter-btn {
  position: relative;
  width: clamp(58px, 14vw, 72px);
  height: clamp(58px, 14vw, 72px);
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.12s ease;
}
.shutter-btn:active:not(:disabled) { transform: scale(0.91); }
.shutter-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.shutter-ring {
  position: absolute; inset: 0;
  border: 3px solid #fff;
  border-radius: 50%;
}
.shutter-dot {
  width: 80%; height: 80%;
  background: #fff;
  border-radius: 50%;
  transition: background 0.15s, transform 0.15s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.35);
}
.shutter-btn.is-counting .shutter-dot {
  background: var(--primary);
  animation: shutter-pulse 1s ease infinite;
}
@keyframes shutter-pulse {
  0%,100% { transform: scale(0.85); }
  50%      { transform: scale(1.05); }
}

/* Icon round buttons flanking the shutter */
.btn-icon-round {
  width: clamp(38px, 9vw, 46px);
  height: clamp(38px, 9vw, 46px);
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.25);
  color: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  position: relative;
  transition: background 0.18s;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
}
.btn-icon-round:hover,
.btn-icon-round.active { background: rgba(14,165,233,0.45); border-color: var(--primary); }
.btn-icon-round:disabled { opacity: 0.4; cursor: not-allowed; }

.timer-badge {
  position: absolute; top: -2px; right: -2px;
  width: 14px; height: 14px;
  background: var(--primary); color: #fff;
  border-radius: 50%; font-size: 0.6rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}

/* Highlight on countdown active state */
.video-container.is-countdown .shutter-ring {
  border-color: var(--primary);
  box-shadow: 0 0 16px var(--primary);
}

/* ── Tips strip ───────────────────────────────────────────────────────────── */
.camera-tips {
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-dim);
  margin-top: 0.6rem;
  padding: 0 0.5rem;
}

/* ── Upload dropzone ─────────────────────────────────────────────────────── */
.dropzone-area {
  border: 2px dashed rgba(14,165,233,0.38);
  border-radius: var(--radius-md);
  padding: clamp(2.5rem, 8vw, 5rem) clamp(1rem, 4vw, 2.5rem);
  text-align: center;
  cursor: pointer;
  background: rgba(14,165,233,0.03);
  transition: all 0.18s;
}
.dropzone-area:hover,
.dropzone-area.drag-over {
  border-color: var(--primary);
  background: rgba(14,165,233,0.09);
}
.upload-icon    { margin-bottom: 0.9rem; }
.dropzone-area h3 { font-size: clamp(1rem, 3vw, 1.2rem); margin-bottom: 0.3rem; }
.dropzone-area p  { font-size: 0.85rem; color: var(--text-muted); }
.dropzone-formats { font-size: 0.72rem !important; color: var(--text-dim) !important; margin-top: 0.2rem; }
.hidden { display: none; }
.mt-2   { margin-top: 0.6rem; }

/* ── Preview actions ─────────────────────────────────────────────────────── */
.preview-actions {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-top: 1rem;
}
@media (min-width: 440px) {
  .preview-actions { flex-direction: row; justify-content: center; }
  .preview-actions .btn { min-width: 150px; }
}
@media (max-width: 439px) {
  .preview-actions .btn { width: 100%; }
}

.image-info-bar {
  text-align: center;
  font-size: 0.74rem;
  color: var(--text-dim);
  margin-top: 0.5rem;
}

/* ── Analysing overlay ───────────────────────────────────────────────────── */
.analyzing-overlay {
  position: absolute; inset: 0;
  background: rgba(7,13,30,0.88);
  backdrop-filter: blur(8px);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 1.5rem; text-align: center; z-index: 20;
}
.spinner {
  width: 52px; height: 52px;
  border: 4px solid rgba(14,165,233,0.18);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.85s linear infinite;
  margin-bottom: 1.1rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.ticker-text {
  font-size: 0.83rem; color: #38bdf8;
  margin-top: 0.45rem;
  animation: fade-in-up 0.35s ease;
}
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(5px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Transition: fade-up for banners ─────────────────────────────────────── */
.fade-up-enter-active { transition: all 0.28s ease; }
.fade-up-leave-active { transition: all 0.2s ease; }
.fade-up-enter-from, .fade-up-leave-to { opacity: 0; transform: translateY(-8px); }

.text-cyan  { color: var(--primary); }
.text-amber { color: #f59e0b; }
</style>
