<template>
  <nav class="navbar" :class="{ 'nav-scrolled': scrolled }">
    <div class="container nav-container">

      <!-- Brand -->
      <router-link to="/" class="brand-logo" @click="closeDrawer">
        <div class="logo-icon">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-cyan">
            <path d="M6.5 12c.94-3.46 4.94-6 8.5-6 3.56 0 6.06 2.54 7 6-.94 3.46-3.44 6-7 6s-7.56-2.54-8.5-6Z"/>
            <path d="M18 12h.01"/>
            <path d="M2 12c1.5 2 3.5 3.5 6 4"/>
            <path d="M2 12c1.5-2 3.5-3.5 6-4"/>
          </svg>
        </div>
        <div class="brand-text">
          <span>FreshCatch</span><span class="text-cyan"> AI</span>
        </div>
        <span class="brand-badge">2026</span>
      </router-link>

      <!-- Desktop links -->
      <ul class="nav-links desktop-only">
        <li><router-link to="/"           class="nav-link" active-class="active" exact>{{ t('nav.home') }}</router-link></li>
        <li>
          <router-link to="/analyze" class="nav-link" active-class="active">
            <span class="live-dot"></span>{{ t('nav.analyze') }}
          </router-link>
        </li>
        <li><router-link to="/guide"         class="nav-link" active-class="active">{{ t('nav.guide') }}</router-link></li>
        <li><router-link to="/how-it-works"  class="nav-link" active-class="active">{{ t('nav.howItWorks') }}</router-link></li>
        <li><router-link to="/about"         class="nav-link" active-class="active">{{ t('nav.about') }}</router-link></li>
        <li v-if="authStore.isAuthenticated">
          <router-link to="/history" class="nav-link" active-class="active">{{ t('nav.history') }}</router-link>
        </li>
        <li v-if="authStore.isResearcher">
          <router-link to="/admin" class="nav-link admin-nav-pill" active-class="active">{{ t('nav.admin') }}</router-link>
        </li>
      </ul>

      <!-- Desktop right actions -->
      <div class="nav-actions desktop-only">
        <button class="lang-toggle-btn" @click="toggleLanguage" :title="'Language: ' + (authStore.language === 'en' ? 'English' : 'Filipino')">
          {{ authStore.language?.toUpperCase() || 'EN' }}
        </button>

        <template v-if="authStore.isAuthenticated">
          <div class="user-pill-container">
            <router-link to="/dashboard" class="user-chip">
              <div class="user-avatar">{{ authStore.userName?.charAt(0) || '?' }}</div>
              <div class="user-info-text">
                <span class="user-name">{{ authStore.userName?.split(' ')[0] }}</span>
                <span class="user-role-tag">{{ authStore.userRole }}</span>
              </div>
            </router-link>
            <button @click="handleLogout" class="btn-icon-logout" title="Logout">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </button>
          </div>
        </template>

        <template v-else>
          <router-link to="/login"   class="btn btn-secondary btn-sm">{{ t('nav.login') }}</router-link>
          <router-link to="/analyze" class="btn btn-primary btn-sm">{{ t('nav.analyze') }}</router-link>
        </template>
      </div>

      <!-- Mobile right: lang + hamburger -->
      <div class="mobile-right mobile-only">
        <button class="lang-toggle-btn" @click="toggleLanguage">
          {{ authStore.language?.toUpperCase() || 'EN' }}
        </button>
        <button class="hamburger" @click="toggleDrawer" :aria-expanded="drawerOpen" aria-label="Toggle navigation">
          <span class="bar" :class="{ open: drawerOpen }"></span>
          <span class="bar" :class="{ open: drawerOpen }"></span>
          <span class="bar" :class="{ open: drawerOpen }"></span>
        </button>
      </div>
    </div>

    <!-- Mobile drawer overlay -->
    <Transition name="fade-overlay">
      <div v-if="drawerOpen" class="drawer-overlay" @click="closeDrawer"></div>
    </Transition>

    <!-- Mobile drawer -->
    <Transition name="slide-drawer">
      <div v-if="drawerOpen" class="mobile-drawer" role="dialog" aria-label="Navigation menu">

        <!-- Drawer header -->
        <div class="drawer-header">
          <div class="brand-logo">
            <div class="logo-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan"><path d="M6.5 12c.94-3.46 4.94-6 8.5-6 3.56 0 6.06 2.54 7 6-.94 3.46-3.44 6-7 6s-7.56-2.54-8.5-6Z"/><path d="M18 12h.01"/></svg></div>
            <span>FreshCatch<span class="text-cyan"> AI</span></span>
          </div>
          <button class="drawer-close" @click="closeDrawer" aria-label="Close menu">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Authenticated user info strip -->
        <div v-if="authStore.isAuthenticated" class="drawer-user-strip">
          <div class="user-avatar large">{{ authStore.userName?.charAt(0) || '?' }}</div>
          <div>
            <div class="drawer-user-name">{{ authStore.userName }}</div>
            <div class="drawer-user-role">{{ authStore.userRole }}</div>
          </div>
        </div>

        <!-- Nav links -->
        <nav class="drawer-nav">
          <router-link to="/"          class="drawer-link" active-class="drawer-active" exact @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            {{ t('nav.home') }}
          </router-link>

          <router-link to="/analyze"   class="drawer-link drawer-link-primary" @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <span class="flex-center gap-1"><span class="live-dot"></span>{{ t('nav.analyze') }}</span>
          </router-link>

          <router-link to="/guide"        class="drawer-link" @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            {{ t('nav.guide') }}
          </router-link>

          <router-link to="/how-it-works" class="drawer-link" @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
            {{ t('nav.howItWorks') }}
          </router-link>

          <router-link to="/about"        class="drawer-link" @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            {{ t('nav.about') }}
          </router-link>

          <router-link v-if="authStore.isAuthenticated" to="/history" class="drawer-link" @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {{ t('nav.history') }}
          </router-link>

          <router-link v-if="authStore.isAuthenticated" to="/dashboard" class="drawer-link" @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            Dashboard
          </router-link>

          <router-link v-if="authStore.isResearcher" to="/admin" class="drawer-link drawer-link-teal" @click="closeDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            {{ t('nav.admin') }}
          </router-link>
        </nav>

        <!-- Drawer footer actions -->
        <div class="drawer-footer">
          <template v-if="authStore.isAuthenticated">
            <button class="btn btn-danger w-full" @click="handleLogout">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              Logout
            </button>
          </template>
          <template v-else>
            <router-link to="/login"   class="btn btn-secondary w-full" @click="closeDrawer">{{ t('nav.login') }}</router-link>
            <router-link to="/analyze" class="btn btn-primary  w-full" @click="closeDrawer">{{ t('nav.analyze') }}</router-link>
          </template>
        </div>

      </div>
    </Transition>

  </nav>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { translations } from '../../i18n/translations';

const authStore = useAuthStore();
const router    = useRouter();

// ── Drawer state ───────────────────────────────────────────────────────────
const drawerOpen = ref(false);

function toggleDrawer() { drawerOpen.value = !drawerOpen.value; }
function closeDrawer()  { drawerOpen.value = false; }

// Close drawer on route change
router.afterEach(() => closeDrawer());

// Close drawer / prevent scroll on body when open
import { watch } from 'vue';
watch(drawerOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
});

// ── Scroll shadow ──────────────────────────────────────────────────────────
const scrolled = ref(false);
function onScroll() { scrolled.value = window.scrollY > 12; }
onMounted(()       => window.addEventListener('scroll', onScroll, { passive: true }));
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll));

// ── i18n ───────────────────────────────────────────────────────────────────
function t(path) {
  const lang = authStore.language || 'en';
  let cur = translations[lang] || translations.en;
  for (const k of path.split('.')) {
    if (cur?.[k] !== undefined) cur = cur[k]; else return path;
  }
  return cur;
}

function toggleLanguage() {
  authStore.setLanguage(authStore.language === 'en' ? 'tl' : 'en');
}

function handleLogout() {
  closeDrawer();
  authStore.logout();
  router.push('/');
}
</script>

<style scoped>
/* ── Navbar shell ─────────────────────────────────────────────────────────── */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(7, 13, 30, 0.85);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--border-glass);
  transition: box-shadow 0.2s;
}
.nav-scrolled { box-shadow: 0 4px 24px rgba(0,0,0,0.4); }

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4.25rem;
  gap: 1rem;
}

/* ── Brand ────────────────────────────────────────────────────────────────── */
.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-white);
  font-family: var(--font-heading);
  flex-shrink: 0;
  text-decoration: none;
}
.logo-icon {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px;
  background: rgba(14,165,233,0.15);
  border: 1px solid var(--border-glass);
  border-radius: 9px;
}
.brand-badge {
  font-size: 0.6rem; font-weight: 700; padding: 0.12rem 0.4rem;
  background: linear-gradient(135deg, var(--primary), var(--accent-teal));
  color: #fff; border-radius: 4px; letter-spacing: 0.05em;
}
.text-cyan { color: var(--primary); }

/* ── Desktop nav links ────────────────────────────────────────────────────── */
.nav-links {
  display: flex; align-items: center; gap: 1.35rem;
  list-style: none; flex: 1; justify-content: center;
}
.nav-link {
  display: inline-flex; align-items: center; gap: 0.35rem;
  font-size: 0.9rem; font-weight: 500; color: var(--text-muted);
  transition: color 0.18s; white-space: nowrap;
}
.nav-link:hover, .nav-link.active { color: var(--primary); }

.admin-nav-pill {
  background: rgba(20,184,166,0.15); color: var(--accent-teal) !important;
  padding: 0.3rem 0.65rem; border-radius: 6px;
  border: 1px solid rgba(20,184,166,0.3); font-size: 0.83rem;
}

/* ── Desktop right actions ────────────────────────────────────────────────── */
.nav-actions {
  display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0;
}
.lang-toggle-btn {
  background: var(--bg-glass); border: 1px solid var(--border-glass);
  color: var(--text-white); padding: 0.38rem 0.7rem;
  border-radius: var(--radius-sm); font-size: 0.78rem; font-weight: 700;
  cursor: pointer; transition: all 0.18s;
}
.lang-toggle-btn:hover { border-color: var(--primary); background: var(--primary-glow); }

.user-pill-container { display: flex; align-items: center; gap: 0.45rem; }
.user-chip {
  display: flex; align-items: center; gap: 0.45rem;
  background: var(--bg-glass); border: 1px solid var(--border-glass);
  padding: 0.28rem 0.6rem; border-radius: var(--radius-full); text-decoration: none;
}
.user-avatar {
  width: 26px; height: 26px;
  background: linear-gradient(135deg, var(--primary), var(--accent-teal));
  color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.78rem; font-weight: 700; flex-shrink: 0;
}
.user-avatar.large { width: 40px; height: 40px; font-size: 1rem; }
.user-info-text { display: flex; flex-direction: column; line-height: 1.1; }
.user-name  { font-size: 0.78rem; font-weight: 600; color: var(--text-white); }
.user-role-tag { font-size: 0.62rem; color: var(--text-muted); text-transform: capitalize; }
.btn-icon-logout {
  background: transparent; border: none; color: var(--text-dim);
  cursor: pointer; padding: 0.38rem; display: flex; align-items: center;
  border-radius: 6px; transition: color 0.18s;
}
.btn-icon-logout:hover { color: var(--color-not-fresh); }

/* ── Live dot ─────────────────────────────────────────────────────────────── */
.live-dot {
  display: inline-block; width: 6px; height: 6px;
  background: var(--color-fresh); border-radius: 50%;
  box-shadow: 0 0 7px var(--color-fresh);
  animation: pulse 1.8s infinite;
}
@keyframes pulse {
  0%,100% { transform: scale(0.95); opacity: 0.8; }
  50%      { transform: scale(1.35); opacity: 1; }
}

/* ── Responsive visibility ───────────────────────────────────────────────── */
.desktop-only { display: flex; }
.mobile-only  { display: none; }

@media (max-width: 900px) {
  .desktop-only { display: none !important; }
  .mobile-only  { display: flex; }
}

/* ── Hamburger button ────────────────────────────────────────────────────── */
.mobile-right { display: flex; align-items: center; gap: 0.6rem; }
.hamburger {
  display: flex; flex-direction: column; justify-content: center;
  gap: 5px; width: 40px; height: 40px; padding: 8px;
  background: var(--bg-glass); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); cursor: pointer;
}
.bar {
  display: block; height: 2px; width: 100%;
  background: var(--text-white); border-radius: 2px;
  transition: all 0.25s ease;
  transform-origin: center;
}
/* Animate to X when open */
.hamburger:has(.bar.open) .bar:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.hamburger:has(.bar.open) .bar:nth-child(2) { opacity: 0; transform: scaleX(0); }
.hamburger:has(.bar.open) .bar:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

/* ── Drawer overlay ──────────────────────────────────────────────────────── */
.drawer-overlay {
  position: fixed; inset: 0; z-index: 101;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(3px);
}
.fade-overlay-enter-active, .fade-overlay-leave-active { transition: opacity 0.25s; }
.fade-overlay-enter-from, .fade-overlay-leave-to { opacity: 0; }

/* ── Drawer panel ────────────────────────────────────────────────────────── */
.mobile-drawer {
  position: fixed; top: 0; right: 0; bottom: 0;
  z-index: 102;
  width: min(320px, 88vw);
  background: rgba(9, 17, 38, 0.97);
  backdrop-filter: blur(24px);
  border-left: 1px solid var(--border-glass);
  display: flex; flex-direction: column;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
.slide-drawer-enter-active, .slide-drawer-leave-active { transition: transform 0.28s cubic-bezier(.4,0,.2,1); }
.slide-drawer-enter-from, .slide-drawer-leave-to { transform: translateX(100%); }

.drawer-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid var(--border-glass);
  flex-shrink: 0;
}
.drawer-close {
  background: var(--bg-glass); border: 1px solid var(--border-glass);
  color: var(--text-white); width: 36px; height: 36px;
  border-radius: 8px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.18s;
}
.drawer-close:hover { background: rgba(255,255,255,0.12); }

.drawer-user-strip {
  display: flex; align-items: center; gap: 0.85rem;
  padding: 1rem 1.25rem;
  background: rgba(14,165,233,0.06);
  border-bottom: 1px solid var(--border-glass);
  flex-shrink: 0;
}
.drawer-user-name { font-size: 0.92rem; font-weight: 600; color: var(--text-white); }
.drawer-user-role { font-size: 0.72rem; color: var(--primary); text-transform: capitalize; margin-top: 1px; }

.drawer-nav {
  display: flex; flex-direction: column; gap: 0.15rem;
  padding: 0.75rem 0.75rem; flex: 1;
}
.drawer-link {
  display: flex; align-items: center; gap: 0.85rem;
  padding: 0.85rem 1rem; border-radius: var(--radius-sm);
  font-size: 0.95rem; font-weight: 500; color: var(--text-muted);
  text-decoration: none; transition: all 0.18s;
}
.drawer-link:hover, .drawer-link.drawer-active {
  background: rgba(14,165,233,0.1); color: var(--primary);
}
.drawer-link-primary { color: var(--primary) !important; }
.drawer-link-primary:hover { background: rgba(14,165,233,0.15) !important; }
.drawer-link-teal { color: var(--accent-teal) !important; }
.drawer-link-teal:hover { background: rgba(20,184,166,0.1) !important; }

.flex-center { display: inline-flex; align-items: center; }
.gap-1 { gap: 0.35rem; }

.drawer-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-glass);
  display: flex; flex-direction: column; gap: 0.6rem;
  flex-shrink: 0;
  /* Safe area for iPhone home indicator */
  padding-bottom: calc(1rem + env(safe-area-inset-bottom));
}
.w-full { width: 100%; }
</style>
