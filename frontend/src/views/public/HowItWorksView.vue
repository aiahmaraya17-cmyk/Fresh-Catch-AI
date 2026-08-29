<template>
  <div class="how-it-works-view container container-narrow">
    <div class="page-header text-center">
      <span class="badge badge-cyan">CNN Architecture Pipeline</span>
      <h1>How FreshCatch AI Works</h1>
      <p class="subtitle">
        Step-by-step technological workflow from market photo capture to CNN probability distribution and visual indicator reasoning.
      </p>
    </div>

    <!-- Pipeline Step Sequence -->
    <div class="pipeline-container">
      <!-- Step 1 -->
      <div class="glass-card step-card">
        <div class="step-badge">STEP 01</div>
        <div class="step-body">
          <h3>1. Image Capture or Upload</h3>
          <p>
            The vendor or buyer captures a photograph of the fish specimen using their smartphone or desktop camera, or selects a picture from their device gallery.
          </p>
          <div class="step-sub-box">
            <strong>Optimal Input:</strong> Side view of fish showing eye, operculum (gill cover), and body scales in reasonable market lighting.
          </div>
        </div>
      </div>

      <!-- Step 2 -->
      <div class="glass-card step-card">
        <div class="step-badge">STEP 02</div>
        <div class="step-body">
          <h3>2. Algorithmic Image Quality Gatekeeper</h3>
          <p>
            Before passing the image to the CNN, our Python preprocessing module evaluates:
          </p>
          <ul class="step-list">
            <li><strong>Blur & Sharpness:</strong> Modified Laplacian variance ($\sigma^2_{Laplacian}$).</li>
            <li><strong>Lighting & Exposure:</strong> Mean HSV luminance value ($V \in [25, 240]$).</li>
            <li><strong>Contrast & Foreground:</strong> Standard deviation of pixel intensities to confirm a distinct fish subject.</li>
          </ul>
          <p class="step-note">
            If the image is too dark, washed out, or out-of-focus, the system immediately requests a clearer capture to prevent misleading predictions.
          </p>
        </div>
      </div>

      <!-- Step 3 -->
      <div class="glass-card step-card">
        <div class="step-badge">STEP 03</div>
        <div class="step-body">
          <h3>3. MobileNetV2 CNN Feature Extraction</h3>
          <p>
            The verified image is normalized to $224 \times 224 \times 3$ and passed through the convolutional neural network backbone:
          </p>
          <ul class="step-list">
            <li><strong>Spatial Convolutions:</strong> Detects corneal convexity, pupil sharpness, and scale edge regularity.</li>
            <li><strong>Spectral Chrominance Analysis:</strong> Evaluates red-chroma saturation in LAB color space ($a^*$ channel) for gill opercular coloration.</li>
            <li><strong>Texture Gradients:</strong> Computes Sobel edge continuity on flank scales.</li>
          </ul>
        </div>
      </div>

      <!-- Step 4 -->
      <div class="glass-card step-card">
        <div class="step-badge">STEP 04</div>
        <div class="step-body">
          <h3>4. Softmax Classification & Confidence Calibration</h3>
          <p>
            The Dense classification head computes class probabilities across the 4 freshness categories:
          </p>
          <div class="formula-box">
            $$P(\text{Class}_i) = \frac{e^{z_i}}{\sum_{j=1}^{4} e^{z_j}}$$
          </div>
          <p>
            The highest probability class is selected, and certainty is calibrated to communicate confidence transparently to the user.
          </p>
        </div>
      </div>

      <!-- Step 5 -->
      <div class="glass-card step-card">
        <div class="step-badge">STEP 05</div>
        <div class="step-body">
          <h3>5. Visual Indicators, Recommendation & Safety Notice</h3>
          <p>
            The system returns a comprehensive result screen featuring detected visual indicators (eyes, gills, skin), practical culinary advice, and scientific food safety disclaimers.
          </p>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="text-center mt-4">
      <router-link to="/analyze" class="btn btn-primary btn-lg">
        Try the Fish Scanner Now
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.how-it-works-view {
  padding: clamp(1.5rem, 4vw, 3.5rem) 1.25rem;
}

.page-header {
  margin-bottom: 3rem;
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
}

.pipeline-container {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  position: relative;
}

.pipeline-container::before {
  content: '';
  position: absolute;
  top: 40px;
  bottom: 40px;
  left: 28px;
  width: 2px;
  background: linear-gradient(180deg, var(--primary), var(--accent-teal));
  z-index: 0;
}

.step-card {
  display: flex;
  gap: 1.5rem;
  padding: clamp(1.25rem, 3vw, 1.75rem);
  position: relative;
  z-index: 1;
}

@media (max-width: 600px) {
  .pipeline-container::before { display: none; }
  .step-card {
    flex-direction: column;
    gap: 0.85rem;
    padding: 1.25rem;
  }
}

.step-badge {
  background: linear-gradient(135deg, var(--primary), var(--accent-teal));
  color: #fff;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.5rem 0.8rem;
  border-radius: var(--radius-sm);
  height: fit-content;
  white-space: nowrap;
  flex-shrink: 0;
}

.step-body h3 {
  font-size: clamp(1rem, 3vw, 1.25rem);
  margin-bottom: 0.6rem;
}

.step-body p {
  color: var(--text-main);
  font-size: 0.92rem;
  line-height: 1.55;
  margin-bottom: 0.75rem;
}

.step-sub-box {
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.2);
  padding: 0.6rem 0.9rem;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  color: #e0f2fe;
}

.step-list {
  margin: 0.5rem 0 0.75rem 1.25rem;
  font-size: 0.88rem;
  color: var(--text-main);
}

.step-list li {
  margin-bottom: 0.35rem;
}

.step-note {
  font-size: 0.82rem;
  color: var(--text-dim);
  font-style: italic;
}

.formula-box {
  background: rgba(0, 0, 0, 0.4);
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  text-align: center;
  font-family: monospace;
  color: #38bdf8;
  margin: 0.5rem 0;
  font-size: clamp(0.78rem, 2vw, 0.95rem);
  overflow-x: auto;
  white-space: nowrap;
}

.mt-4 { margin-top: 2.5rem; }
</style>
