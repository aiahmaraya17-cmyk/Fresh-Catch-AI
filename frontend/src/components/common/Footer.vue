<template>
  <footer class="app-footer">
    <div class="container footer-grid">
      <!-- Project Identity Column -->
      <div class="footer-col brand-col">
        <div class="brand-logo footer-logo">
          <span>FreshCatch</span><span class="text-cyan"> AI</span>
          <span class="brand-badge">2026</span>
        </div>
        <p class="footer-desc">
          An Image-Based Fish Freshness Classification System for Fish Vendors and Consumers in the Local Wet Market of Roxas, Oriental Mindoro Using Convolutional Neural Network (CNN).
        </p>
        <div class="location-badge">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          <span>Roxas Public Market & Dangay Port, Oriental Mindoro</span>
        </div>
      </div>

      <!-- Quick Links -->
      <div class="footer-col">
        <h4 class="footer-heading">Platform</h4>
        <ul class="footer-links">
          <li><router-link to="/analyze">Analyze Fish</router-link></li>
          <li><router-link to="/guide">Fish Freshness Guide</router-link></li>
          <li><router-link to="/how-it-works">How It Works</router-link></li>
          <li><router-link to="/about">Research Background</router-link></li>
        </ul>
      </div>

      <!-- Species & Classes -->
      <div class="footer-col">
        <h4 class="footer-heading">Classifications</h4>
        <ul class="footer-links">
          <li><span class="dot fresh-dot"></span> Fresh (Sariwa)</li>
          <li><span class="dot mod-dot"></span> Moderately Fresh (Katamtamang Sariwa)</li>
          <li><span class="dot less-dot"></span> Less Fresh (Hindi Gaanong Sariwa)</li>
          <li><span class="dot not-dot"></span> Not Fresh (Bilasa)</li>
        </ul>
      </div>

      <!-- Research & Portals -->
      <div class="footer-col">
        <h4 class="footer-heading">Portals & Research</h4>
        <ul class="footer-links">
          <li><router-link to="/login">Account Login</router-link></li>
          <li><router-link to="/admin">Researcher / Admin Dashboard</router-link></li>
          <li><router-link to="/admin/evaluation">CNN Model Metrics</router-link></li>
          <li><router-link to="/admin/environmental">Environmental Benchmarks</router-link></li>
        </ul>
      </div>
    </div>

    <!-- Safety Disclaimer Bar -->
    <div class="container footer-disclaimer-bar">
      <div class="disclaimer-inner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-amber">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <p>
          <strong>Scientific Disclaimer:</strong> FreshCatch AI provides an AI-assisted visual assessment of apparent fish freshness. Results are not a laboratory-grade food safety determination and cannot detect odor, bacteria, toxins, or internal chemical composition.
        </p>
      </div>
      <div class="copyright-text">
        &copy; 2026 FreshCatch AI Research Project. All rights reserved. Roxas, Oriental Mindoro, Philippines.
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: rgba(4, 8, 20, 0.95);
  border-top: 1px solid var(--border-glass);
  padding: 3.5rem 0 1.5rem;
  margin-top: 3rem;
  font-size: 0.9rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
}

@media (max-width: 900px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 600px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
}

.brand-col .footer-desc {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin: 1rem 0;
  line-height: 1.5;
}

.location-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.78rem;
  color: var(--accent-teal);
  background: rgba(20, 184, 166, 0.1);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-full);
  border: 1px solid rgba(20, 184, 166, 0.2);
}

.footer-heading {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--text-white);
}

.footer-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer-links a {
  color: var(--text-muted);
  transition: color var(--transition-fast);
}

.footer-links a:hover {
  color: var(--primary);
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 0.4rem;
}

.fresh-dot { background-color: var(--color-fresh); }
.mod-dot { background-color: var(--color-moderate); }
.less-dot { background-color: var(--color-less-fresh); }
.not-dot { background-color: var(--color-not-fresh); }

.footer-disclaimer-bar {
  border-top: 1px solid var(--border-glass);
  padding-top: 1.5rem;
}

.disclaimer-inner {
  display: flex;
  gap: 0.75rem;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  padding: 0.85rem 1.25rem;
  border-radius: var(--radius-sm);
  color: #fde68a;
  font-size: 0.82rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.text-amber { color: #f59e0b; flex-shrink: 0; margin-top: 2px; }
.text-cyan { color: var(--primary); }

.copyright-text {
  text-align: center;
  color: var(--text-dim);
  font-size: 0.78rem;
}
</style>
