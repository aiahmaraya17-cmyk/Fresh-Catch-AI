<template>
  <div class="analyze-view container container-narrow">

    <!-- Page header -->
    <div class="page-header text-center">
      <span class="badge badge-cyan">Visual classification</span>
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
          <span>Hold the phone steady, use even light, and fill the frame with the fish.</span>
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

    <div
      v-if="showResultModal && analysisResult"
      class="result-modal-backdrop"
      @click.self="closeResultModal"
    >
      <div
        class="result-modal-panel glass-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="result-modal-title"
      >
        <button class="result-modal-close" @click="closeResultModal" aria-label="Close result">
          &times;
        </button>

        <div class="result-hero-summary">
          <div>
            <span class="result-hero-eyebrow">Analysis complete</span>
            <h2 id="result-modal-title">Your fish freshness result</h2>
          </div>
          <div class="result-hero-status">
            <FreshnessBadge :classification="analysisResult.classification || 'Fresh'" />
            <div class="result-hero-confidence">
              <strong>{{ ((analysisResult.confidence || 0.92) * 100).toFixed(1) }}%</strong>
              <span>confidence</span>
            </div>
          </div>
        </div>

        <div class="result-modal-grid">
          <div class="result-image-panel">
            <div class="result-image-frame">
              <img :src="analysisResult.imageUrl || defaultSampleImage" :alt="'Analyzed fish result'" class="result-modal-image" />
            </div>

            <div v-if="analysisResult.quality_metrics && Object.keys(analysisResult.quality_metrics).length" class="result-metrics-box">
              <h4>Image quality</h4>
              <div class="result-metrics-list">
                <div class="result-metric-item">
                  <span>Sharpness / Focus Index</span>
                  <strong>{{ analysisResult.quality_metrics.blur_variance }}</strong>
                </div>
                <div class="result-metric-item">
                  <span>Luminance / Brightness</span>
                  <strong>{{ analysisResult.quality_metrics.brightness_mean }}/255</strong>
                </div>
                <div class="result-metric-item">
                  <span>Contrast Standard Dev</span>
                  <strong>{{ analysisResult.quality_metrics.contrast_std }}</strong>
                </div>
              </div>
            </div>
          </div>

          <div class="result-content-panel">
            <span class="result-tag">Visual freshness report</span>
            <div class="badge-wrapper">
              <span class="result-detail-label">Classification details</span>
            </div>

            <div class="recommendation-box">
              <h4>Culinary &amp; handling guidance</h4>
              <p class="rec-en">{{ analysisResult.recommendation }}</p>
              <p v-if="analysisResult.recommendation_tagalog" class="rec-tl">
                <em>"{{ analysisResult.recommendation_tagalog }}"</em>
              </p>
              <div v-if="consumptionGuidance" class="consumption-guidance">
                <div class="consumption-heading">
                  <span class="consumption-icon" aria-hidden="true">⏱</span>
                  <span>Estimated consumption timing</span>
                </div>
                <strong v-if="consumptionGuidance.consume_by">
                  Consume by {{ consumptionGuidance.consume_by }}
                </strong>
                <strong v-else>Do not consume</strong>
                <p>{{ consumptionGuidance.window }}</p>
                <p v-if="consumptionGuidance.window_tagalog" class="rec-tl">
                  <em>{{ consumptionGuidance.window_tagalog }}</em>
                </p>
              </div>
            </div>

            <div
              v-if="analysisResult.food_safety_warning"
              :class="['safety-warning-box', safetyLevel]"
            >
              <div class="safety-icon" aria-hidden="true">
                <svg v-if="safetyLevel === 'danger'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </div>
              <div class="safety-content">
                <p class="safety-en">{{ strippedWarning }}</p>
                <p v-if="analysisResult.food_safety_warning_tagalog" class="safety-tl">
                  <em>{{ strippedWarningTl }}</em>
                </p>
              </div>
            </div>

            <ConfidenceGauge
              :confidence="analysisResult.confidence || 0.92"
              :probabilities="analysisResult.class_probabilities || analysisResult.classProbabilities"
            />

            <IndicatorList :indicators="analysisResult.visualIndicators || analysisResult.visual_indicators" />

            <DisclaimerBanner />

            <div class="result-actions">
              <button class="btn btn-primary btn-lg w-full" @click="closeResultModal">Close</button>
              <router-link to="/history" class="btn btn-secondary btn-lg w-full">View Assessment History</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <DisclaimerBanner />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { translations } from '../../i18n/translations';
import FreshnessBadge from '../../components/result/FreshnessBadge.vue';
import ConfidenceGauge from '../../components/result/ConfidenceGauge.vue';
import IndicatorList from '../../components/result/IndicatorList.vue';
import DisclaimerBanner from '../../components/common/DisclaimerBanner.vue';
import ApiService from '../../services/api';

const router    = useRouter();
const route     = useRoute();
const authStore = useAuthStore();
const defaultSampleImage = '/dataset/raw/fish_0001_bangus_fresh_bright.jpg';

// ── State ──────────────────────────────────────────────────────────────────
const inputMode      = ref('camera');
const selectedSpecies = ref('');
const speciesOptions  = ref([]);
const analysisResult  = ref(null);
const showResultModal = ref(false);

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

const strippedWarning = computed(() => {
  const w = analysisResult.value?.food_safety_warning || '';
  return w.replace(/^[🚫⚠️\s]+/, '').trim();
});

const strippedWarningTl = computed(() => {
  const w = analysisResult.value?.food_safety_warning_tagalog || '';
  return w.replace(/^[🚫⚠️\s]+/, '').trim();
});

const safetyLevel = computed(() => {
  const cls = (analysisResult.value?.classification || '').toLowerCase();
  if (cls.includes('not fresh') || cls.includes('spoiled') || cls.includes('stale') || cls.includes('bilasa')) return 'danger';
  if (cls.includes('less fresh')) return 'caution';
  return 'caution';
});

const consumptionGuidance = computed(() => {
  const result = analysisResult.value;
  if (!result) return null;
  if (result.consumption_guidance) return result.consumption_guidance;
  const classification = result.classification || 'Fresh';
  const windows = {
    Fresh: ['Best consumed today; refrigerate at 0-4°C and use within 1 day.', 'Pinakamainam kainin ngayong araw; ilagay sa 0-4°C na refrigerator at gamitin sa loob ng 1 araw.', 1],
    'Moderately Fresh': ['Cook promptly today; if continuously refrigerated, use within 1 day. Do not eat raw.', 'Lutuin agad ngayong araw; kung naka-refrigerate, gamitin sa loob ng 1 araw. Huwag kainin nang hilaw.', 1],
    'Less Fresh': ['Cook immediately today only after checking smell and texture. Do not store for later or eat raw.', 'Lutuin agad ngayong araw matapos suriin ang amoy at tekstura. Huwag itago o kainin nang hilaw.', 0],
    'Not Fresh': ['Do not consume. Discard immediately; there is no safe consumption date.', 'Huwag kainin. Itapon agad; walang ligtas na petsa para kainin ito.', null],
  };
  const [window, windowTagalog, days] = windows[classification] || windows.Fresh;
  const consumeBy = days === null ? null : new Date(Date.now() + days * 86400000).toISOString().slice(0, 10);
  return { window, window_tagalog: windowTagalog, consume_by: consumeBy };
});

function closeResultModal() {
  showResultModal.value = false;
  analysisResult.value = null;
}

function updateModalScrollLock() {
  document.body.style.overflow = showResultModal.value ? 'hidden' : '';
}

watch(showResultModal, updateModalScrollLock);

function handleEscapeClose(event) {
  if (event.key === 'Escape' && showResultModal.value) {
    closeResultModal();
  }
}

// ── Submit analysis ────────────────────────────────────────────────────────
async function submitAnalysis() {
  if (!capturedImage.value || isAnalyzing.value) return;

  isAnalyzing.value      = true;
  qualityRejection.value = null;

  // Clear any previous result from sessionStorage BEFORE sending
  // the new request — this prevents ResultView from ever reading
  // a stale cached result if the navigation races the write.
  sessionStorage.removeItem('freshcatch_active_result');

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
      analysisResult.value = res;
      showResultModal.value = true;
      sessionStorage.setItem('freshcatch_active_result', JSON.stringify(res));
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

  window.addEventListener('keydown', handleEscapeClose);

  try {
    const res = await ApiService.getSpecies();
    if (res.success) speciesOptions.value = res.species;
  } catch {}

  if (inputMode.value === 'camera') startCamera();
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscapeClose);
  document.body.style.overflow = '';
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

.result-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.72);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 0;
  z-index: 1000;
}

.result-modal-panel {
  position: relative;
  width: min(1100px, 100vw);
  max-height: 88vh;
  overflow: hidden;
  padding: 1rem 1rem 0.75rem;
  border-radius: 1.5rem 1.5rem 0 0;
  display: flex;
  flex-direction: column;
}

.result-modal-close {
  position: absolute;
  top: 0.8rem;
  right: 0.9rem;
  width: 2.35rem;
  height: 2.35rem;
  border: 1px solid var(--border-glass);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.55);
  color: var(--text-white);
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 5;
}

.result-hero-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.65rem 3.25rem 1rem 0.35rem;
  border-bottom: 1px solid var(--border-glass);
}

.result-hero-eyebrow {
  display: block;
  margin-bottom: 0.3rem;
  color: var(--accent-gold);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.result-hero-summary h2 {
  margin: 0;
  color: var(--text-white);
  font-size: clamp(1.05rem, 2.5vw, 1.45rem);
}

.result-hero-status {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  flex-shrink: 0;
}

.result-hero-confidence {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.1;
}

.result-hero-confidence strong {
  color: var(--text-white);
  font-family: var(--font-heading);
  font-size: 1.25rem;
}

.result-hero-confidence span {
  color: var(--text-muted);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.result-modal-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(320px, 1.1fr);
  gap: 1.5rem;
  align-items: flex-start;
  overflow: auto;
  padding: 0.5rem 0.15rem 0.25rem;
}

.result-image-panel,
.result-content-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-image-frame {
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border-radius: var(--radius-sm);
  background: #020817;
}

.result-modal-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-metrics-box {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  padding: 1rem;
}

.result-metrics-box h4 {
  margin: 0 0 0.7rem;
  font-size: 0.92rem;
  color: var(--text-white);
}

.result-metrics-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.result-metric-item {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.result-metric-item span {
  color: var(--text-muted);
}

.result-metric-item strong {
  color: var(--text-white);
}

.result-tag {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--accent-gold);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  display: block;
}

.badge-wrapper {
  margin-top: 0.2rem;
}

.result-detail-label {
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.recommendation-box {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-glass);
  padding: 1rem;
  border-radius: var(--radius-sm);
}

.recommendation-box h4 {
  font-size: 0.92rem;
  color: var(--text-white);
  margin-bottom: 0.45rem;
}

.rec-en {
  font-size: 0.9rem;
  color: var(--text-main);
  line-height: 1.5;
  margin-bottom: 0.4rem;
}

.rec-tl {
  font-size: 0.84rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.consumption-guidance {
  margin-top: 0.9rem;
  padding: 0.8rem 0.9rem;
  border-left: 3px solid var(--accent-teal);
  background: rgba(45, 212, 191, 0.08);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.consumption-heading {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--accent-teal);
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.consumption-icon { font-size: 0.95rem; }

.consumption-guidance strong {
  display: block;
  margin-top: 0.35rem;
  color: var(--text-white);
  font-size: 0.9rem;
}

.consumption-guidance p {
  margin-top: 0.25rem;
  color: var(--text-main);
  font-size: 0.78rem;
  line-height: 1.45;
}

.consumption-guidance .rec-tl {
  color: var(--text-muted);
}

.safety-warning-box {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  padding: 1rem;
  border-radius: var(--radius-sm);
  border-width: 1px;
  border-style: solid;
}

.safety-warning-box.danger {
  background: rgba(220, 38, 38, 0.12);
  border-color: rgba(220, 38, 38, 0.45);
}

.safety-warning-box.caution {
  background: rgba(234, 179, 8, 0.10);
  border-color: rgba(234, 179, 8, 0.40);
}

.safety-icon {
  color: inherit;
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.safety-warning-box.danger .safety-icon { color: #fca5a5; }
.safety-warning-box.caution .safety-icon { color: #fde68a; }

.safety-content {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.safety-en {
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.5;
  color: var(--text-white);
  margin: 0;
}

.safety-warning-box.danger .safety-en { color: #fca5a5; }
.safety-warning-box.caution .safety-en { color: #fde68a; }

.safety-tl {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin: 0;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

@media (min-width: 820px) {
  .result-modal-backdrop {
    align-items: center;
    padding: 1rem;
  }

  .result-modal-panel {
    width: min(1100px, 92vw);
    max-height: 88vh;
    border-radius: var(--radius-lg);
  }
}

@media (max-width: 820px) {
  .result-modal-grid {
    grid-template-columns: 1fr;
  }

  .result-modal-panel {
    max-height: 88vh;
  }
}

@media (max-width: 640px) {
  .result-modal-panel {
    width: 100vw;
    max-height: 88vh;
    border-radius: 1.25rem 1.25rem 0 0;
    padding: 0.9rem 0.9rem 0.75rem;
  }

  .result-modal-close {
    top: 0.7rem;
    right: 0.7rem;
  }

  .result-modal-grid {
    gap: 1rem;
    padding-bottom: 0.5rem;
  }

  .result-hero-summary {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.45rem 2.8rem 0.85rem 0.15rem;
  }

  .result-hero-status {
    justify-content: space-between;
    width: 100%;
  }

  .result-hero-confidence {
    align-items: flex-start;
  }

  .result-actions {
    flex-direction: column;
  }

  .recommendation-box,
  .safety-warning-box,
  .result-metrics-box {
    padding: 0.9rem;
  }
}

@media (min-width: 480px) {
  .result-actions {
    flex-direction: row;
  }
}

.text-cyan  { color: var(--primary); }
.text-amber { color: #f59e0b; }
</style>
