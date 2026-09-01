<template>
  <div class="home-view">
    <section class="hero-section">
      <div class="container hero-container">
        <div class="hero-badge">
          <span class="live-dot"></span>
          <span>{{ t('home.tag') }}</span>
        </div>

        <h1 class="hero-title">{{ t('home.title') }}</h1>
        <p class="hero-subtitle">{{ t('home.subtitle') }}</p>

        <div class="hero-actions">
          <router-link to="/analyze" class="btn btn-primary btn-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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

        <div class="metric-strip">
          <div class="metric-item">
            <span class="metric-val">89.6%</span>
            <span class="metric-lbl">Held-out test accuracy</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">4</span>
            <span class="metric-lbl">QIM freshness grades</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">8</span>
            <span class="metric-lbl">Local market species</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">QIM</span>
            <span class="metric-lbl">Eyes, gills &amp; skin cues</span>
          </div>
        </div>

        <div class="research-banner glass-card">
          <div class="banner-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div class="banner-content">
            <h3>{{ t('home.researchTitle') }}</h3>
            <p>{{ t('home.researchDesc') }}</p>
          </div>
          <div class="market-pill">Dangay Port &amp; Public Wet Market</div>
        </div>
      </div>
    </section>

    <section class="section-process container">
      <div class="section-header text-center">
        <p class="kicker">Assessment workflow</p>
        <h2>From photograph to market-ready grade</h2>
        <p class="section-subtitle">A structured visual pipeline aligned with FAO Quality Index Method criteria.</p>
      </div>
      <div class="process-grid">
        <article class="glass-card process-card">
          <span class="process-num">01</span>
          <h3>Capture</h3>
          <p>Photograph the head, gill cover, and flank in even light. Alignment guides keep the specimen in frame.</p>
        </article>
        <article class="glass-card process-card">
          <span class="process-num">02</span>
          <h3>Measure</h3>
          <p>The model extracts QIM cues: corneal clarity, gill redness, scale luster, and body yellowing.</p>
        </article>
        <article class="glass-card process-card">
          <span class="process-num">03</span>
          <h3>Grade</h3>
          <p>An ensemble classifier returns a four-level freshness grade with confidence and culinary guidance.</p>
        </article>
      </div>
    </section>

    <section class="section-categories container">
      <div class="section-header text-center">
        <p class="kicker">Taxonomy</p>
        <h2>Apparent visual freshness classification</h2>
        <p class="section-subtitle">Four ordinal grades used by vendors and consumers at Roxas Public Market.</p>
      </div>

      <div class="grid-4">
        <div class="glass-card cat-card">
          <div class="cat-header">
            <span class="cat-chip chip-fresh">FRESH</span>
            <span class="cat-tagalog">SARIWA</span>
          </div>
          <h4 class="cat-name">Optimal freshness</h4>
          <p class="cat-desc">Convex clear eyes, bright ruby-red gills, tight iridescent scales, and firm elastic flesh.</p>
          <div class="cat-culinary"><strong>Best for:</strong> Kinilaw, sinigang, grilling, steaming.</div>
        </div>

        <div class="glass-card cat-card">
          <div class="cat-header">
            <span class="cat-chip chip-mod">MODERATELY FRESH</span>
            <span class="cat-tagalog">KATAMTAMANG SARIWA</span>
          </div>
          <h4 class="cat-name">Acceptable freshness</h4>
          <p class="cat-desc">Slight corneal flattening, fading gill redness, and moderate scale luster. Cook promptly.</p>
          <div class="cat-culinary"><strong>Best for:</strong> Paksiw, escabeche, frying, sarciado.</div>
        </div>

        <div class="glass-card cat-card">
          <div class="cat-header">
            <span class="cat-chip chip-less">LESS FRESH</span>
            <span class="cat-tagalog">HINDI GAANONG SARIWA</span>
          </div>
          <h4 class="cat-name">Reduced freshness</h4>
          <p class="cat-desc">Cloudy sunken eyes, dull brownish gills, and a muted metallic finish. Cook thoroughly.</p>
          <div class="cat-culinary"><strong>Caution:</strong> Not for raw dishes. Inspect smell and texture.</div>
        </div>

        <div class="glass-card cat-card">
          <div class="cat-header">
            <span class="cat-chip chip-stale">NOT FRESH</span>
            <span class="cat-tagalog">BILASA</span>
          </div>
          <h4 class="cat-name">Stale / spoiled</h4>
          <p class="cat-desc">Opaque sunken eyes, dark slimy gills, yellowish discoloration, and softened tissue.</p>
          <div class="cat-culinary"><strong>Warning:</strong> Do not purchase, cook, or consume.</div>
        </div>
      </div>
    </section>

    <section class="scanner-cta-section container">
      <div class="scanner-cta-card glass-card">
        <div class="scanner-laser"></div>
        <div class="cta-inner">
          <div class="cta-text">
            <p class="kicker">Ready when you are</p>
            <h2>Assess a specimen at the stall</h2>
            <p>Use your phone camera or upload a clear photo of the eyes, gills, and flank for an instant visual grade.</p>
          </div>
          <router-link to="/analyze" class="btn btn-primary btn-lg">
            Open scanner
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
.hero-section {
  padding: clamp(2.75rem, 8vw, 5.5rem) 0 clamp(1.5rem, 4vw, 2.5rem);
  text-align: center;
}
.hero-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(56,189,248,0.08);
  border: 1px solid rgba(56,189,248,0.28);
  color: var(--primary);
  font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.04em;
  padding: 0.4rem 1rem;
  border-radius: var(--radius-full);
  margin-bottom: 1.6rem;
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
  font-size: clamp(2rem, 5.4vw, 3.35rem);
  max-width: 18ch;
  line-height: 1.12;
  margin-bottom: 1.15rem;
  letter-spacing: -0.03em;
  color: var(--text-white);
  padding: 0 0.5rem;
}

.hero-subtitle {
  font-size: clamp(0.98rem, 2.3vw, 1.12rem);
  color: var(--text-muted);
  max-width: 640px;
  line-height: 1.7;
  margin-bottom: 2rem;
  padding: 0 0.5rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  margin-bottom: 2.5rem;
  padding: 0 0.5rem;
}

@media (max-width: 380px) {
  .hero-actions { flex-direction: column; align-items: stretch; width: 100%; padding: 0; }
  .hero-actions .btn { width: 100%; }
}

.metric-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  width: 100%;
  max-width: 920px;
  background: var(--border-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-bottom: 1.75rem;
}
.metric-item {
  background: rgba(6, 16, 28, 0.72);
  padding: 1.1rem 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.metric-val {
  font-family: var(--font-heading);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-white);
}
.metric-lbl {
  font-size: 0.72rem;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}
@media (max-width: 720px) {
  .metric-strip { grid-template-columns: 1fr 1fr; }
}

.research-banner {
  display: flex; align-items: center; gap: 1.25rem;
  padding: 1.15rem 1.5rem;
  max-width: 920px; width: 100%;
  text-align: left;
}
.banner-icon { flex-shrink: 0; }
.banner-content { flex: 1; min-width: 0; }
.banner-content h3 { font-size: 0.98rem; color: var(--text-white); }
.banner-content p  { font-size: 0.83rem; color: var(--text-muted); line-height: 1.45; margin-top: 0.2rem; }
.market-pill {
  background: rgba(45,212,191,0.12); color: var(--accent-teal);
  padding: 0.4rem 0.8rem; border-radius: var(--radius-sm);
  border: 1px solid rgba(45,212,191,0.28);
  font-size: 0.75rem; font-weight: 700; white-space: nowrap; flex-shrink: 0;
}

@media (max-width: 680px) {
  .research-banner { flex-direction: column; text-align: center; gap: 0.85rem; }
  .banner-icon { display: none; }
  .market-pill { width: 100%; text-align: center; }
}

.section-process, .section-categories { padding: clamp(2rem, 6vw, 3.75rem) 1.25rem; }
.section-header { margin-bottom: 2rem; }
.section-header h2 { font-size: clamp(1.45rem, 3.6vw, 2rem); margin: 0.4rem 0 0.5rem; }
.section-subtitle { color: var(--text-muted); font-size: clamp(0.85rem, 2vw, 1rem); max-width: 560px; margin: 0 auto; }

.process-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.15rem;
}
.process-card { padding: 1.4rem 1.35rem; text-align: left; }
.process-num {
  font-family: var(--font-heading);
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  color: var(--accent-gold);
  font-weight: 700;
}
.process-card h3 { margin: 0.55rem 0 0.4rem; font-size: 1.12rem; }
.process-card p { font-size: 0.86rem; color: var(--text-muted); line-height: 1.55; }
@media (max-width: 800px) {
  .process-grid { grid-template-columns: 1fr; }
}

.cat-card { padding: 1.35rem; display: flex; flex-direction: column; }
.cat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.35rem; }
.cat-chip {
  font-size: 0.66rem; font-weight: 800; padding: 0.18rem 0.5rem;
  border-radius: 4px; letter-spacing: 0.06em;
}
.chip-fresh { background: var(--color-fresh-bg);    color: var(--color-fresh);    border: 1px solid rgba(16,185,129,0.4); }
.chip-mod   { background: var(--color-moderate-bg); color: var(--color-moderate); border: 1px solid rgba(245,158,11,0.4); }
.chip-less  { background: var(--color-less-fresh-bg);color: var(--color-less-fresh);border: 1px solid rgba(249,115,22,0.4); }
.chip-stale { background: var(--color-not-fresh-bg); color: var(--color-not-fresh); border: 1px solid rgba(239,68,68,0.4); }

.cat-tagalog { font-size: 0.65rem; font-weight: 700; color: var(--text-dim); letter-spacing: 0.06em; }
.cat-name { font-size: 1.08rem; margin-bottom: 0.5rem; }
.cat-desc { font-size: 0.83rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 1rem; flex: 1; }
.cat-culinary {
  font-size: 0.8rem; color: var(--text-main);
  background: rgba(0,0,0,0.22); padding: 0.55rem 0.8rem;
  border-radius: var(--radius-sm);
}

.scanner-cta-section {
  padding: clamp(1.5rem, 4vw, 2.5rem) 1.25rem clamp(3rem, 8vw, 5rem);
}

.scanner-cta-card {
  position: relative; overflow: hidden;
  padding: clamp(1.75rem, 5vw, 2.75rem) clamp(1.5rem, 5vw, 3rem);
}
.cta-inner {
  display: flex; justify-content: space-between;
  align-items: center; gap: 2rem;
}
.cta-text h2 { font-size: clamp(1.35rem, 3.5vw, 1.8rem); margin: 0.35rem 0 0.45rem; }
.cta-text p  { color: var(--text-muted); font-size: clamp(0.85rem, 2vw, 0.95rem); }

@media (max-width: 700px) {
  .cta-inner { flex-direction: column; text-align: center; }
  .cta-inner .btn { width: 100%; max-width: 320px; }
}

.text-cyan { color: var(--primary); }
</style>
