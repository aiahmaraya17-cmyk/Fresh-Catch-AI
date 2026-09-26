<template>
  <div class="how-it-works-view container container-narrow">
    <!-- Header -->
    <div class="page-header text-center">
      <span class="badge badge-cyan">Simple Guide</span>
      <h1>How FreshCatch AI Works</h1>
      <p class="subtitle">
        Just take a photo of a fish, and we will tell you how fresh it is —
        in a few seconds. Here is how it works, step by step.
      </p>
    </div>

    <!-- 4 Simple Steps -->
    <div class="steps">
      <!-- Step 1 -->
      <div class="glass-card step-card">
        <div class="step-number">1</div>
        <div class="step-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
        </div>
        <div class="step-body">
          <h2>Take a photo of the fish</h2>
          <p>
            Use your phone or computer camera to take a picture of the fish.
            You can also choose a photo you already have saved.
          </p>
          <div class="tip-box">
            <span class="tip-label">Best photo</span>
            Show the whole fish from the side, so its eye and body are clear.
            Take it in a bright, well-lit place.
          </div>
        </div>
      </div>

      <!-- Step 2 -->
      <div class="glass-card step-card">
        <div class="step-number">2</div>
        <div class="step-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="7"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <path d="M11 8v6M8 11h6"/>
          </svg>
        </div>
        <div class="step-body">
          <h2>We check the photo</h2>
          <p>
            First, we make sure the picture is clear enough and that it really
            shows a fish. If the photo is too dark, too blurry, or is not a
            fish, we will kindly ask you to take another one.
          </p>
          <div class="tip-box tip-box-soft">
            <span class="tip-label">Why</span>
            A clear photo gives you a more trustworthy result.
          </div>
        </div>
      </div>

      <!-- Step 3 -->
      <div class="glass-card step-card">
        <div class="step-number">3</div>
        <div class="step-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 18h6M10 22h4"/>
            <path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2h6c0-.8.4-1.5 1-2A7 7 0 0 0 12 2z"/>
          </svg>
        </div>
        <div class="step-body">
          <h2>The app studies the fish</h2>
          <p>
            Our app has learned from thousands of fish photos. It looks at the
            same signs an experienced buyer checks:
          </p>
          <ul class="sign-list">
            <li>
              <span class="sign-emoji">👁️</span>
              <span><strong>The eyes</strong> — clear and full means fresh; cloudy and sunken means older.</span>
            </li>
            <li>
              <span class="sign-emoji">🩸</span>
              <span><strong>The gills</strong> — bright red is fresh; pale or brown is not.</span>
            </li>
            <li>
              <span class="sign-emoji">✨</span>
              <span><strong>The skin and scales</strong> — shiny and firm is fresh; dull and loose is older.</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Step 4 -->
      <div class="glass-card step-card">
        <div class="step-number">4</div>
        <div class="step-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 11l3 3L22 4"/>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
        </div>
        <div class="step-body">
          <h2>You get an easy answer</h2>
          <p>
            In a few seconds you see how fresh the fish is, in simple words.
            We also suggest how to cook it and remind you when a fish is not
            safe to eat.
          </p>
        </div>
      </div>
    </div>

    <!-- What the result means -->
    <section class="result-guide">
      <h2 class="section-title text-center">What your result means</h2>
      <div class="result-grid">
        <div class="result-card is-fresh">
          <div class="result-dot"></div>
          <h3>Fresh <span class="result-fil">Sariwa</span></h3>
          <p>Very good to eat. You can cook it any way you like — grill it, or make sinigang.</p>
        </div>
        <div class="result-card is-moderate">
          <div class="result-dot"></div>
          <h3>Moderately Fresh <span class="result-fil">Katamtamang sariwa</span></h3>
          <p>Still good, but cook it today. Best cooked well, such as frying or stewing. Do not eat it raw.</p>
        </div>
        <div class="result-card is-less">
          <div class="result-dot"></div>
          <h3>Not Fresh <span class="result-fil">Hindi na sariwa</span></h3>
          <p>It is getting old. We do not recommend eating it. When in doubt, throw it out.</p>
        </div>
        <div class="result-card is-spoiled">
          <div class="result-dot"></div>
          <h3>Spoiled <span class="result-fil">Bilasa</span></h3>
          <p>Not safe to eat. Please do not cook or eat this fish. Throw it away.</p>
        </div>
      </div>
    </section>

    <!-- Reassurance -->
    <div class="glass-card note-card">
      <div class="note-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
      </div>
      <p>
        <strong>A helpful guide, not a rule.</strong>
        FreshCatch AI helps you decide, but always trust your own senses too.
        If a fish smells bad or looks wrong, do not eat it — even if the app
        says otherwise.
      </p>
    </div>

    <!-- Call to action -->
    <div class="text-center cta">
      <router-link to="/analyze" class="btn btn-primary btn-lg">
        Try it now — scan a fish
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.how-it-works-view {
  padding: clamp(1.5rem, 4vw, 3.5rem) 1.25rem;
}

/* ── Header ── */
.page-header { margin-bottom: 2.75rem; }
.page-header h1 {
  font-size: clamp(1.7rem, 5vw, 2.6rem);
  margin: 0.75rem 0;
}
.subtitle {
  color: var(--text-main);
  font-size: clamp(1.02rem, 2.2vw, 1.2rem);
  line-height: 1.7;
  max-width: 620px;
  margin: 0 auto;
}

/* ── Steps ── */
.steps {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.step-card {
  display: grid;
  grid-template-columns: auto auto 1fr;
  align-items: start;
  gap: 1.25rem;
  padding: clamp(1.35rem, 3vw, 2rem);
}
.step-number {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent-teal));
  color: #042033;
  font-size: 1.4rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 14px var(--primary-glow);
}
.step-icon {
  width: 46px;
  height: 46px;
  color: var(--primary);
  flex-shrink: 0;
}
.step-icon svg { width: 100%; height: 100%; }

.step-body h2 {
  font-size: clamp(1.18rem, 3vw, 1.5rem);
  margin-bottom: 0.5rem;
  line-height: 1.3;
}
.step-body p {
  color: var(--text-main);
  font-size: clamp(1rem, 2.2vw, 1.1rem);
  line-height: 1.7;
  margin: 0 0 0.85rem;
}

/* Tip boxes */
.tip-box {
  background: rgba(45, 212, 191, 0.1);
  border-left: 4px solid var(--accent-teal);
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-size: clamp(0.95rem, 2vw, 1.05rem);
  line-height: 1.6;
  color: var(--text-main);
}
.tip-box-soft {
  background: rgba(56, 189, 248, 0.08);
  border-left-color: var(--primary);
}
.tip-label {
  display: inline-block;
  font-weight: 800;
  color: var(--accent-teal);
  margin-right: 0.4rem;
  text-transform: uppercase;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
}
.tip-box-soft .tip-label { color: var(--primary); }

/* Sign list (eyes / gills / skin) */
.sign-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}
.sign-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: clamp(0.98rem, 2.1vw, 1.08rem);
  line-height: 1.6;
  color: var(--text-main);
}
.sign-emoji {
  font-size: 1.4rem;
  line-height: 1.3;
  flex-shrink: 0;
}

/* ── Result guide ── */
.result-guide { margin-top: 3rem; }
.section-title {
  font-size: clamp(1.4rem, 4vw, 1.9rem);
  margin-bottom: 1.5rem;
}
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.result-card {
  background: var(--bg-card);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.35rem;
  border-top: 5px solid var(--text-dim);
}
.result-card h3 {
  font-size: 1.2rem;
  margin: 0.5rem 0 0.4rem;
}
.result-fil {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 0.15rem;
}
.result-card p {
  font-size: clamp(0.95rem, 2vw, 1.02rem);
  line-height: 1.6;
  color: var(--text-main);
  margin: 0;
}
.result-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--text-dim);
}
.result-card.is-fresh    { border-top-color: #22c55e; }
.result-card.is-fresh    .result-dot { background: #22c55e; box-shadow: 0 0 10px rgba(34,197,94,0.6); }
.result-card.is-moderate { border-top-color: #eab308; }
.result-card.is-moderate .result-dot { background: #eab308; box-shadow: 0 0 10px rgba(234,179,8,0.6); }
.result-card.is-less     { border-top-color: #f97316; }
.result-card.is-less     .result-dot { background: #f97316; box-shadow: 0 0 10px rgba(249,115,22,0.6); }
.result-card.is-spoiled  { border-top-color: #ef4444; }
.result-card.is-spoiled  .result-dot { background: #ef4444; box-shadow: 0 0 10px rgba(239,68,68,0.6); }

/* ── Reassurance note ── */
.note-card {
  margin-top: 2.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.35rem 1.5rem;
}
.note-icon {
  width: 40px;
  height: 40px;
  color: var(--primary);
  flex-shrink: 0;
}
.note-icon svg { width: 100%; height: 100%; }
.note-card p {
  margin: 0;
  font-size: clamp(0.98rem, 2.1vw, 1.08rem);
  line-height: 1.65;
  color: var(--text-main);
}

/* ── CTA ── */
.cta { margin-top: 3rem; }

/* ── Mobile ── */
@media (max-width: 600px) {
  .step-card {
    grid-template-columns: auto 1fr;
    gap: 0.85rem 1rem;
    padding: 1.35rem;
  }
  /* Icon sits beside the number on its own row on small screens */
  .step-icon { grid-row: 1; grid-column: 2; justify-self: end; }
  .step-body { grid-column: 1 / -1; }
}
</style>
