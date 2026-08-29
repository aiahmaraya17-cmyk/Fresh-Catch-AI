import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import App from './App.vue';
import './style.css';

// ── PWA service worker (auto-registered by vite-plugin-pwa) ───────────────
import { registerSW } from 'virtual:pwa-register';

registerSW({
  // Re-check for updates every hour while the tab is open
  onRegisteredSW(swUrl, registration) {
    if (registration) {
      setInterval(() => {
        registration.update();
      }, 60 * 60 * 1000);
    }
  },
  // When a new version is available, refresh automatically
  onNeedRefresh() {
    // The PWAPrompt component handles user-facing update toasts,
    // so we just store the flag here and let the component react.
    window.__pwa_update_available__ = true;
    window.dispatchEvent(new CustomEvent('pwa-update-available'));
  },
  onOfflineReady() {
    window.dispatchEvent(new CustomEvent('pwa-offline-ready'));
  },
});

// ── App bootstrap ──────────────────────────────────────────────────────────
const app   = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.mount('#app');
