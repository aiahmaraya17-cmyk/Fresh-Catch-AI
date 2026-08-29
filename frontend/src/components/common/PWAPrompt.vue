<template>
  <!-- ── Install banner ──────────────────────────────────────────────────── -->
  <Transition name="pwa-slide">
    <div v-if="showInstall" class="pwa-banner pwa-install" role="banner" aria-live="polite">
      <div class="pwa-banner-icon">
        <img src="/icons/icon-96x96.png" alt="FreshCatch AI" width="44" height="44" />
      </div>
      <div class="pwa-banner-body">
        <p class="pwa-title">Add FreshCatch AI to your home screen</p>
        <p class="pwa-sub">Works offline — analyze fish without internet.</p>
      </div>
      <div class="pwa-banner-actions">
        <button class="btn btn-primary btn-sm" @click="install">Install</button>
        <button class="pwa-dismiss" @click="dismissInstall" aria-label="Dismiss">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
  </Transition>

  <!-- ── Update toast ────────────────────────────────────────────────────── -->
  <Transition name="pwa-slide">
    <div v-if="showUpdate" class="pwa-banner pwa-update" role="status" aria-live="polite">
      <div class="pwa-banner-icon update-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
      </div>
      <div class="pwa-banner-body">
        <p class="pwa-title">New version available</p>
        <p class="pwa-sub">Refresh to get the latest FreshCatch AI.</p>
      </div>
      <div class="pwa-banner-actions">
        <button class="btn btn-primary btn-sm" @click="reload">Refresh</button>
        <button class="pwa-dismiss" @click="showUpdate = false" aria-label="Dismiss">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
  </Transition>

  <!-- ── Offline-ready toast ─────────────────────────────────────────────── -->
  <Transition name="pwa-slide">
    <div v-if="showOfflineReady" class="pwa-banner pwa-offline" role="status" aria-live="polite">
      <div class="pwa-banner-icon offline-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12.55a11 11 0 0 1 14.08 0"/>
          <path d="M1.42 9a16 16 0 0 1 21.16 0"/>
          <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
          <line x1="12" y1="20" x2="12.01" y2="20"/>
        </svg>
      </div>
      <div class="pwa-banner-body">
        <p class="pwa-title">Ready to work offline</p>
        <p class="pwa-sub">FreshCatch AI is cached and ready.</p>
      </div>
      <button class="pwa-dismiss" @click="showOfflineReady = false" aria-label="Dismiss">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

// ── Install prompt ─────────────────────────────────────────────────────────
const showInstall   = ref(false);
const showUpdate    = ref(false);
const showOfflineReady = ref(false);
let   deferredPrompt = null;

// Auto-dismiss offline-ready toast after 4 s
let offlineTimer = null;

function handleBeforeInstallPrompt(e) {
  e.preventDefault();
  deferredPrompt = e;
  // Only show if user hasn't permanently dismissed
  if (!localStorage.getItem('pwa-install-dismissed')) {
    showInstall.value = true;
  }
}

async function install() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  if (outcome === 'accepted') {
    localStorage.setItem('pwa-install-dismissed', '1');
  }
  deferredPrompt = null;
  showInstall.value = false;
}

function dismissInstall() {
  showInstall.value = false;
  // Remember for 7 days so it doesn't re-appear immediately
  localStorage.setItem('pwa-install-dismissed', Date.now().toString());
}

// ── Update / offline-ready events from main.js ────────────────────────────
function handleUpdateAvailable() { showUpdate.value = true; }
function handleOfflineReady() {
  showOfflineReady.value = true;
  offlineTimer = setTimeout(() => { showOfflineReady.value = false; }, 4000);
}

function reload() {
  window.location.reload();
}

// ── Re-show install after 7 days ──────────────────────────────────────────
function shouldShowInstall() {
  const ts = parseInt(localStorage.getItem('pwa-install-dismissed') || '0', 10);
  if (!ts) return true;
  // If ts is '1' (accepted), never show again
  if (ts === 1) return false;
  return Date.now() - ts > 7 * 24 * 60 * 60 * 1000;
}

onMounted(() => {
  // Re-check 7-day cooldown before attaching listener
  if (shouldShowInstall()) {
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  }
  window.addEventListener('pwa-update-available', handleUpdateAvailable);
  window.addEventListener('pwa-offline-ready',    handleOfflineReady);
  // iOS Safari: already installed detection
  if (window.navigator.standalone) {
    showInstall.value = false;
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  window.removeEventListener('pwa-update-available', handleUpdateAvailable);
  window.removeEventListener('pwa-offline-ready',    handleOfflineReady);
  if (offlineTimer) clearTimeout(offlineTimer);
});
</script>

<style scoped>
/* ── Banner base ─────────────────────────────────────────────────────────── */
.pwa-banner {
  position: fixed;
  z-index: 200;
  bottom: calc(1rem + env(safe-area-inset-bottom));
  left: 50%;
  transform: translateX(-50%);
  width: min(480px, calc(100vw - 2rem));
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.9rem 1.1rem;
  border-radius: var(--radius-md);
  box-shadow: 0 8px 32px rgba(0,0,0,0.55);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid var(--border-glass);
}

.pwa-install {
  background: rgba(9, 17, 40, 0.95);
  border-color: rgba(14, 165, 233, 0.4);
}
.pwa-update {
  background: rgba(9, 17, 40, 0.95);
  border-color: rgba(14, 165, 233, 0.5);
}
.pwa-offline {
  background: rgba(6, 25, 18, 0.95);
  border-color: rgba(16, 185, 129, 0.45);
}

/* ── Icon ────────────────────────────────────────────────────────────────── */
.pwa-banner-icon {
  flex-shrink: 0;
  width: 44px; height: 44px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px;
  overflow: hidden;
}
.update-icon {
  background: rgba(14, 165, 233, 0.15);
  border: 1px solid rgba(14, 165, 233, 0.3);
  color: var(--primary);
}
.offline-icon {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: var(--color-fresh);
}

/* ── Text ────────────────────────────────────────────────────────────────── */
.pwa-banner-body { flex: 1; min-width: 0; }
.pwa-title {
  font-size: 0.88rem; font-weight: 700;
  color: var(--text-white); line-height: 1.2;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.pwa-sub {
  font-size: 0.76rem; color: var(--text-muted);
  margin-top: 0.15rem; line-height: 1.3;
}

/* ── Actions ─────────────────────────────────────────────────────────────── */
.pwa-banner-actions {
  display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0;
}
.pwa-dismiss {
  background: transparent; border: none;
  color: var(--text-dim); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px;
  border-radius: 6px; transition: color 0.18s;
  -webkit-tap-highlight-color: transparent;
}
.pwa-dismiss:hover { color: var(--text-white); }

/* ── Transition ──────────────────────────────────────────────────────────── */
.pwa-slide-enter-active { transition: all 0.35s cubic-bezier(.4,0,.2,1); }
.pwa-slide-leave-active { transition: all 0.25s cubic-bezier(.4,0,.2,1); }
.pwa-slide-enter-from  { transform: translateX(-50%) translateY(120%); opacity: 0; }
.pwa-slide-leave-to    { transform: translateX(-50%) translateY(120%); opacity: 0; }

/* ── Compact on very small screens ───────────────────────────────────────── */
@media (max-width: 360px) {
  .pwa-banner { gap: 0.6rem; padding: 0.75rem 0.85rem; }
  .pwa-title  { font-size: 0.82rem; }
  .pwa-sub    { display: none; }
}
</style>
