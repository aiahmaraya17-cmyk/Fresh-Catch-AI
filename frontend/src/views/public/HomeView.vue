<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container hero-container">
        <div class="hero-badge">
          <span class="live-dot"></span>
          <span>{{ t('home.tag') }}</span>
        </div>

        <h1 class="hero-title">
          {{ t('home.title') }}
        </h1>

        <p class="hero-subtitle">
          {{ t('home.subtitle') }}
        </p>

        <!-- Primary Call to Actions -->
        <div class="hero-actions">
          <router-link to="/analyze" class="btn btn-primary btn-lg pulse-glow">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
              <circle cx="12" cy="13" r="3"/>
            </svg>
            {{ t('home.btnAnalyze') }}
          </router-link>
          <router-link to="/how-it-works" class="btn btn-secondary btn-lg">
            {{ t('home.btnLearn') }}
          </router-link>
          <router-link to="/guide" class="btn btn-outline btn-lg">
            {{ t('home.btnGuide') }}
          </router-link>
        </div>

        <!-- Research Location Highlight Banner -->
        <div class="research-banner glass-card">
          <div class="banner-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div class="banner-content">
            <h3>{{ t('home.researchTitle') }}</h3>
            <p>{{ t('home.researchDesc') }}</p>
          </div>
          <div class="market-pill">
            <span>Dangay Port & Public Wet Market</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 4 Freshness Categories Showcase -->
    <section class="section-categories container">
      <div class="section-header text-center">
        <h2>Apparent Visual Freshness Classification</h2>
        <p class="section-subtitle">Categorized using Convolutional Neural Network representations of anatomical features</p>
      </div>

      <div class="grid-4">
        <!-- Fresh -->
        <div class="glass-card cat-card cat-fresh">
          <div class="cat-header">
            <span class="cat-chip chip-fresh">FRESH</span>
            <span class="cat-tagalog">SARIWA</span>
          </div>
          <h4 class="cat-name">Optimal Freshness</h4>
          <p class="cat-desc">Crystal clear convex eyes, bright ruby red gills, tight shimmering iridescent scales, and firm elastic flesh.</p>
          <div class="cat-culinary">
            <strong>Best for:</strong> Kinilaw (raw), Sinigang, Grilling, Steaming.
          </div>
        </div>

        <!-- Moderately Fresh -->
        <div class="glass-card cat-card cat-moderate">
          <div class="cat-header">
            <span class="cat-chip chip-mod">MODERATELY FRESH</span>
            <span class="cat-tagalog">KATAMTAMANG SARIWA</span>
          </div>
          <h4 class="cat-name">Acceptable Freshness</h4>
          <p class="cat-desc">Slight cornea flattening with minor haze, slightly dull red gills, and moderate scale luster.</p>
          <div class="cat-culinary">
            <strong>Best for:</strong> Paksiw, Escabeche, Frying, Sarciado.
          </div>
        </div>

        <!-- Not Fresh -->
        <div class="glass-card cat-card cat-less">
          <div class="cat-header">
            <span class="cat-chip chip-less">NOT FRESH</span>
            <span class="cat-tagalog">HINDI NA SARIWA</span>
          </div>
          <h4 class="cat-name">Not Fresh</h4>
          <p class="cat-desc">Sunken cloudy eyes, pale brownish or bleached gills, dull discolored skin, and softened body tissue.</p>
          <div class="cat-culinary">
            <strong>Warning:</strong> DO NOT cook or eat. Discard immediately.
          </div>
        </div>

        <!-- Spoiled / Bilasa -->
        <div class="glass-card cat-card cat-stale">
          <div class="cat-header">
            <span class="cat-chip chip-stale">SPOILED</span>
            <span class="cat-tagalog">BILASA</span>
          </div>
          <h4 class="cat-name">Stale / Spoiled</h4>
          <p class="cat-desc">Deeply sunken opaque eyes, dark slimy grey/brown gills, yellowish skin discoloration, and soft flaccid belly.</p>
          <div class="cat-culinary">
            <strong>Warning:</strong> Not recommended for purchase or food consumption.
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Fish Scanner Live Banner -->
    <section class="scanner-cta-section container">
      <div class="scanner-cta-card glass-card">
        <div class="scanner-laser"></div>
        <div class="cta-inner">
          <div class="cta-text">
            <h2>Ready to assess a fish in the wet market?</h2>
            <p>Use your smartphone camera or upload a clear photo of the fish eyes, gills, and flank for instant AI classification.</p>
          </div>
          <router-link to="/analyze" class="btn btn-primary btn-lg">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="m10 15 5-3-5-3v6Z"/>
            </svg>
            Launch Camera Scanner
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../stores/authStore';
import { translations } from '../../i18n/translations';

const authStore = useAuthStore();

function t(path) {
  const lang = authStore.language || 'en';
  const keys = path.split('.');
  let current = translations[lang] || translations.en;
  for (const k of keys) {
    if (current && current[k] !== undefined) {
      current = current[k];
    } else {
      return path;
    }
  }
  return current;
}
</script>

<style scoped>
/* ── Hero ─────────────────────────────────────────────────────────────────── */
.hero-section {
  padding: clamp(2.5rem, 8vw, 5rem) 0 clamp(2rem, 6vw, 3.5rem);
  text-align: center;
}
.hero-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(14,165,233,0.12);
  border: 1px solid rgba(14,165,233,0.35);
  color: var(--primary);
  font-size: 0.82rem; font-weight: 700;
  padding: 0.4rem 1rem;
  border-radius: var(--radius-full);
  margin-bottom: 1.5rem;
}

.live-dot {
  display: inline-block; width: 7px; height: 7px;
  background: var(--color-fresh); border-radius: 50%;
  box-shadow: 0 0 8px var(--color-fresh);
  animation: pulse 1.8s infinite;
  flex-shrink: 0;
}
@keyframes pulse {
  0%,100% { transform: scale(0.95); opacity: 0.8; }
  50%      { transform: scale(1.35); opacity: 1; }
}

.hero-title {
  font-size: clamp(1.85rem, 5.5vw, 3.2rem);
  max-width: 950px;
  line-height: 1.15;
  margin-bottom: 1.25rem;
  background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  padding: 0 0.5rem;        /* prevent clipping on mobile */
}

.hero-subtitle {
  font-size: clamp(0.95rem, 2.5vw, 1.15rem);
  color: var(--text-muted);
  max-width: 720px;
  line-height: 1.65;
  margin-bottom: 2rem;
  padding: 0 0.5rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  justify-content: center;
  margin-bottom: clamp(2rem, 6vw, 3.5rem);
  padding: 0 0.5rem;
}

/* Stack buttons on very small screens */
@media (max-width: 380px) {
  .hero-actions { flex-direction: column; align-items: stretch; width: 100%; padding: 0; }
  .hero-actions .btn { width: 100%; }
}

.pulse-glow { animation: pulseGlow 2.5s infinite; }
@keyframes pulseGlow {
  0%,100% { box-shadow: 0 0 15px rgba(14,165,233,0.4); }
  50%      { box-shadow: 0 0 30px rgba(14,165,233,0.8); }
}

/* ── Research banner ──────────────────────────────────────────────────────── */
.research-banner {
  display: flex; align-items: center; gap: 1.25rem;
  padding: 1.1rem 1.5rem;
  max-width: 920px; width: 100%;
  text-align: left;
  border-color: rgba(14,165,233,0.25);
}
.banner-icon { flex-shrink: 0; }
.banner-content { flex: 1; min-width: 0; }
.banner-content h3 { font-size: 1rem; color: var(--text-white); }
.banner-content p  { font-size: 0.83rem; color: var(--text-muted); line-height: 1.4; margin-top: 0.2rem; }
.market-pill {
  background: rgba(20,184,166,0.15); color: var(--accent-teal);
  padding: 0.4rem 0.8rem; border-radius: var(--radius-sm);
  border: 1px solid rgba(20,184,166,0.3);
  font-size: 0.78rem; font-weight: 700; white-space: nowrap; flex-shrink: 0;
}

@media (max-width: 680px) {
  .research-banner { flex-direction: column; text-align: center; gap: 0.85rem; }
  .banner-icon { display: none; }
  .market-pill { width: 100%; text-align: center; }
}

/* ── Freshness category cards ────────────────────────────────────────────── */
.section-categories { padding: clamp(2rem, 6vw, 3.5rem) 1.25rem; }
@media (max-width: 480px) { .section-categories { padding: 2rem 1rem; } }

.section-header      { margin-bottom: 2.25rem; }
.section-header h2   { font-size: clamp(1.5rem, 4vw, 2.1rem); margin-bottom: 0.5rem; }
.section-subtitle    { color: var(--text-muted); font-size: clamp(0.85rem, 2vw, 1rem); }

.cat-card { padding: 1.35rem; display: flex; flex-direction: column; }
.cat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.35rem; }
.cat-chip {
  font-size: 0.68rem; font-weight: 800; padding: 0.18rem 0.5rem;
  border-radius: 4px; letter-spacing: 0.05em;
}
.chip-fresh { background: var(--color-fresh-bg);    color: var(--color-fresh);    border: 1px solid rgba(16,185,129,0.4); }
.chip-mod   { background: var(--color-moderate-bg); color: var(--color-moderate); border: 1px solid rgba(245,158,11,0.4); }
.chip-less  { background: var(--color-less-fresh-bg);color: var(--color-less-fresh);border: 1px solid rgba(249,115,22,0.4); }
.chip-stale { background: var(--color-not-fresh-bg); color: var(--color-not-fresh); border: 1px solid rgba(239,68,68,0.4); }

.cat-tagalog { font-size: 0.67rem; font-weight: 700; color: var(--text-dim); }
.cat-name { font-size: 1.1rem; margin-bottom: 0.5rem; }
.cat-desc { font-size: 0.83rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 1rem; flex: 1; }
.cat-culinary {
  font-size: 0.8rem; color: var(--text-main);
  background: rgba(0,0,0,0.25); padding: 0.55rem 0.8rem;
  border-radius: var(--radius-sm);
}

/* ── CTA banner ───────────────────────────────────────────────────────────── */
.scanner-cta-section {
  padding: clamp(1.5rem, 4vw, 2.5rem) 1.25rem clamp(3rem, 8vw, 5rem);
}
@media (max-width: 480px) { .scanner-cta-section { padding: 1.5rem 1rem 3rem; } }

.scanner-cta-card {
  position: relative; overflow: hidden;
  padding: clamp(1.75rem, 5vw, 2.75rem) clamp(1.5rem, 5vw, 3rem);
  background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(20,184,166,0.12));
  border-color: rgba(14,165,233,0.4);
}
.cta-inner {
  display: flex; justify-content: space-between;
  align-items: center; gap: 2rem;
}
.cta-text h2 { font-size: clamp(1.35rem, 3.5vw, 1.8rem); margin-bottom: 0.5rem; }
.cta-text p  { color: var(--text-muted); font-size: clamp(0.85rem, 2vw, 0.95rem); }

@media (max-width: 700px) {
  .cta-inner { flex-direction: column; text-align: center; }
  .cta-inner .btn { width: 100%; max-width: 320px; }
}

.text-cyan { color: var(--primary); }
</style>
