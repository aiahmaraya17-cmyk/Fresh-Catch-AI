<template>
  <div class="about-view container container-narrow">
    <div class="page-header">
      <span class="badge badge-cyan">Research & Academic Project (2026)</span>
      <h1>About FreshCatch AI</h1>
      <p class="subtitle">
        An Image-Based Fish Freshness Classification System for Fish Vendors and Consumers in the Local Wet Market of Roxas, Oriental Mindoro Using Convolutional Neural Network (CNN)
      </p>
    </div>

    <!-- General Objective Card -->
    <div class="glass-card section-card">
      <div class="card-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
          <path d="M2 12h20"/>
        </svg>
      </div>
      <div class="card-text">
        <h3>General Research Objective</h3>
        <p>
          Develop FreshCatch AI, an image-based fish freshness classification system using a Convolutional Neural Network (CNN), to assist fish vendors and consumers in identifying the apparent freshness condition of fish in the local wet market of Roxas, Oriental Mindoro.
        </p>
      </div>
    </div>

    <!-- Specific Objectives -->
    <div class="glass-card section-card">
      <h3>Specific Research Objectives</h3>
      <div class="objectives-list">
        <div class="objective-item">
          <div class="obj-num">1</div>
          <div class="obj-content">
            <h4>Identify Observable Visual Characteristics</h4>
            <p>Classify fish using observable visual markers: eye clarity/sunkenness, opercular gill coloration, scale luster, and surface contour integrity.</p>
          </div>
        </div>
        <div class="objective-item">
          <div class="obj-num">2</div>
          <div class="obj-content">
            <h4>Roxas Wet Market Fish Image Dataset</h4>
            <p>Construct a dataset of local species (Bangus, Tilapia, Galunggong, Tamban, Matangbaka, Tulingan, Maya-Maya, Tanigue) labeled with environmental and metadata tags.</p>
          </div>
        </div>
        <div class="objective-item">
          <div class="obj-num">3</div>
          <div class="obj-content">
            <h4>Lightweight Mobile-Friendly CNN Pipeline</h4>
            <p>Train and evaluate a transfer-learning CNN architecture (MobileNetV2) capable of real-time mobile inference with true confusion matrix validation.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Critical Model Limitations Notice -->
    <div class="glass-card section-card limitations-card">
      <div class="limit-header">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-amber">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <h3>Scientific Model Limitations & Ethical Boundary</h3>
      </div>
      <p>
        In accordance with research integrity principles, FreshCatch AI classifies <strong>apparent visual freshness condition only</strong>. The camera and CNN cannot directly measure:
      </p>
      <ul class="limitations-list">
        <li>Bacterial, viral, or microbial contamination levels</li>
        <li>Odor, volatile basic nitrogen (TVB-N), or chemical decomposition</li>
        <li>Exact internal muscle storage temperature history</li>
        <li>Chemical preservatives, formalin, or toxic heavy metals</li>
      </ul>
      <p class="limitations-footer">
        FreshCatch AI is designed as a supporting decision aid for consumers and vendors, not a laboratory-grade food safety certification.
      </p>
    </div>
  </div>
</template>

<style scoped>
.about-view {
  padding: clamp(1.5rem, 4vw, 3.5rem) 1.25rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.page-header h1 {
  font-size: clamp(1.5rem, 5vw, 2.5rem);
  margin: 0.75rem 0;
}

.subtitle {
  color: var(--text-muted);
  font-size: clamp(0.85rem, 2vw, 1rem);
  max-width: 680px;
  margin: 0 auto;
  line-height: 1.5;
}

.section-card {
  padding: clamp(1.25rem, 3vw, 2rem);
  margin-bottom: 1.5rem;
}

.card-icon {
  color: var(--primary);
  margin-bottom: 0.75rem;
}

.section-card h3 {
  font-size: clamp(1.05rem, 3vw, 1.3rem);
  margin-bottom: 0.75rem;
}

.section-card p {
  color: var(--text-main);
  line-height: 1.6;
}

.objectives-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-top: 1.25rem;
}

.objective-item {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
  background: rgba(0, 0, 0, 0.2);
  padding: 1.25rem;
  border-radius: var(--radius-sm);
}

/* Stack number + content on very small screens */
@media (max-width: 400px) {
  .objective-item {
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
  }
}

.obj-num {
  width: 32px;
  height: 32px;
  background: var(--primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  flex-shrink: 0;
}

.obj-content h4 {
  font-size: clamp(0.9rem, 2.5vw, 1rem);
  margin-bottom: 0.35rem;
}

.obj-content p {
  font-size: 0.88rem;
  color: var(--text-muted);
}

.limitations-card {
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.05);
}

.limit-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.text-amber { color: #f59e0b; }

.limitations-list {
  margin: 1rem 0 1rem 1.5rem;
  color: var(--text-main);
  font-size: 0.9rem;
}

.limitations-list li {
  margin-bottom: 0.4rem;
}

.limitations-footer {
  font-size: 0.85rem;
  color: #fde68a;
  font-weight: 600;
}
</style>
