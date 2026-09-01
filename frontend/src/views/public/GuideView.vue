<template>
  <div class="guide-view container">
    <div class="page-header text-center">
      <span class="badge badge-cyan">Wet Market Reference Guide</span>
      <h1>Fish Freshness & Species Guide</h1>
      <p class="subtitle">
        Comprehensive guide to visual, sensory, and anatomical freshness indicators for wet market fish species in Roxas, Oriental Mindoro.
      </p>
    </div>

    <!-- Anatomical Sensory Breakdown Grid -->
    <div class="grid-2 mb-4">
      <!-- Eyes Indicator Guide -->
      <div class="glass-card guide-card">
        <div class="guide-card-header">
          <div class="icon-bubble">👁️</div>
          <div>
            <h3>Fish Eyes (Mata ng Isda)</h3>
            <span class="guide-sub">Primary Visual AI Indicator</span>
          </div>
        </div>
        <div class="guide-table-wrap">
          <table class="guide-table">
            <tbody>
            <tr>
              <td class="col-status"><span class="badge badge-fresh">Sariwa (Fresh)</span></td>
              <td>Prominent, convex cornea; crystal-clear lens with shiny jet-black pupil.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-moderate">Katamtaman</span></td>
              <td>Cornea starts to flatten; minor cloudy film over lens.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-not-fresh">Bilasa (Stale)</span></td>
              <td>Sunken, concave eye socket; opaque milky-grey cornea; dark red or brownish hemorrhage.</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Gills Indicator Guide -->
      <div class="glass-card guide-card">
        <div class="guide-card-header">
          <div class="icon-bubble">🫁</div>
          <div>
            <h3>Gills & Operculum (Hasang)</h3>
            <span class="guide-sub">Chrominance & Redness Indicator</span>
          </div>
        </div>
        <div class="guide-table-wrap">
          <table class="guide-table">
            <tbody>
            <tr>
              <td class="col-status"><span class="badge badge-fresh">Sariwa (Fresh)</span></td>
              <td>Bright ruby-red to deep pink; clean with clear, non-sticky mucus.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-moderate">Katamtaman</span></td>
              <td>Dull red or pinkish-brown; slightly thicker mucus layer.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-not-fresh">Bilasa (Stale)</span></td>
              <td>Pale brown, yellowish, or greyish; covered in thick, foul-smelling mucus.</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Skin & Scales Guide -->
      <div class="glass-card guide-card">
        <div class="guide-card-header">
          <div class="icon-bubble">🐟</div>
          <div>
            <h3>Skin & Scales (Balat at Kaliskis)</h3>
            <span class="guide-sub">Iridescent Luster & Texture</span>
          </div>
        </div>
        <div class="guide-table-wrap">
          <table class="guide-table">
            <tbody>
            <tr>
              <td class="col-status"><span class="badge badge-fresh">Sariwa (Fresh)</span></td>
              <td>Vivid natural metallic sheen; tight, firmly attached scales; moist surface.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-moderate">Katamtaman</span></td>
              <td>Slight fading of metallic luster; some scales may loosen slightly.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-not-fresh">Bilasa (Stale)</span></td>
              <td>Dull, bleached, or yellowish discoloration; loose, peeling scales; sticky surface.</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Non-Visual Sensory (Odor & Touch) -->
      <div class="glass-card guide-card">
        <div class="guide-card-header">
          <div class="icon-bubble">👃</div>
          <div>
            <h3>Odor & Texture (Amoy at Lambot)</h3>
            <span class="guide-sub">Physical Check (Beyond Camera Sensing)</span>
          </div>
        </div>
        <div class="guide-table-wrap">
          <table class="guide-table">
            <tbody>
            <tr>
              <td class="col-status"><span class="badge badge-fresh">Sariwa (Fresh)</span></td>
              <td>Pleasant oceanic or mild sea-breeze aroma; firm, springy flesh that springs back immediately.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-moderate">Katamtaman</span></td>
              <td>Neutral to slightly fishy smell; slightly softened flesh with gentle resilience.</td>
            </tr>
            <tr>
              <td class="col-status"><span class="badge badge-not-fresh">Bilasa (Stale)</span></td>
              <td>Strong sour, ammonia, or rotten odor; soft mushy flesh that leaves permanent indentations.</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Common Roxas, Oriental Mindoro Fish Species Catalog -->
    <div class="species-catalog-section">
      <div class="section-header">
        <h2>Common Wet Market Fish Species in Roxas</h2>
        <p class="section-subtitle">Local coastal and aquaculture specimens cataloged in the research dataset</p>
      </div>

      <div class="grid-4">
        <div v-for="sp in speciesList" :key="sp.name" class="glass-card species-card">
          <div class="species-badge">{{ sp.local_name }}</div>
          <h4>{{ sp.name }}</h4>
          <span class="sci-name"><em>{{ sp.scientific_name }}</em></span>
          <p class="species-desc">{{ sp.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '../../services/api';

const speciesList = ref([
  { name: 'Bangus (Milkfish)', local_name: 'Bangus', scientific_name: 'Chanos chanos', description: 'National fish, silvery scales, highly popular in Mindoro markets.' },
  { name: 'Tilapia', local_name: 'Tilapia', scientific_name: 'Oreochromis niloticus', description: 'Freshwater staple, firm white flesh, dark-grey to golden flanks.' },
  { name: 'Galunggong (Round Scad)', local_name: 'Galunggong', scientific_name: 'Decapterus punctatus', description: 'Pelagic staple, elongated cylindrical body, blue-green sheen.' },
  { name: 'Tamban (Sardines)', local_name: 'Tamban', scientific_name: 'Sardinella lemuru', description: 'Small oily fish, rich in omega-3, silver and blue-striped flank.' },
  { name: 'Matangbaka (Bigeye Scad)', local_name: 'Matangbaka', scientific_name: 'Selar crumenophthalmus', description: 'Distinctively large eyes, high market demand in Mindoro.' },
  { name: 'Tulingan (Mackerel Tuna)', local_name: 'Tulingan', scientific_name: 'Auxis thazard', description: 'Dark torpedo body, popular for sinaing and ginataan dishes.' },
  { name: 'Maya-Maya (Red Snapper)', local_name: 'Maya-Maya', scientific_name: 'Lutjanus campechanus', description: 'Prized coral reef fish with vivid red-pink coloration.' },
  { name: 'Tanigue (Spanish Mackerel)', local_name: 'Tanigue', scientific_name: 'Scomberomorus commerson', description: 'Slender predator fish, firm steak cuts, top choice for kinilaw.' }
]);

onMounted(async () => {
  try {
    const res = await ApiService.getSpecies();
    if (res.success && res.species.length > 0) {
      speciesList.value = res.species;
    }
  } catch (e) {
    // fallback to static list
  }
});
</script>

<style scoped>
.guide-view {
  padding: clamp(1.5rem, 4vw, 3.5rem) 1.25rem;
}

.page-header {
  margin-bottom: 2.5rem;
}

.page-header h1 {
  font-size: clamp(1.55rem, 5vw, 2.5rem);
  margin: 0.75rem 0;
}

.subtitle {
  color: var(--text-muted);
  font-size: clamp(0.85rem, 2vw, 1rem);
  max-width: 680px;
  margin: 0 auto;
}

.mb-4 { margin-bottom: 3rem; }

.guide-card {
  padding: 1.5rem;
}

.guide-card-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}

.icon-bubble {
  font-size: 1.8rem;
  flex-shrink: 0;
}

.guide-card-header h3 {
  font-size: clamp(0.95rem, 2.5vw, 1.15rem);
  color: var(--text-white);
}

.guide-sub {
  font-size: 0.75rem;
  color: var(--primary);
  font-weight: 600;
}

/* Table wrapper scrolls horizontally on narrow screens */
.guide-table-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.guide-table {
  width: 100%;
  min-width: 360px;       /* ensures table never crushes below readable width */
  border-collapse: collapse;
  font-size: 0.85rem;
}

.guide-table tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.guide-table tr:last-child {
  border-bottom: none;
}

.guide-table td {
  padding: 0.65rem 0.5rem;
  vertical-align: middle;
}

.col-status {
  width: 110px;
  white-space: nowrap;
}

/* On very small screens let the status badge wrap */
@media (max-width: 400px) {
  .col-status {
    width: 90px;
    white-space: normal;
  }
  .col-status .badge {
    font-size: 0.65rem;
    padding: 0.15rem 0.4rem;
  }
}

/* Species section */
.species-catalog-section {
  margin-top: 2rem;
}

.section-header {
  margin-bottom: 1.75rem;
}

.section-header h2 {
  font-size: clamp(1.2rem, 3.5vw, 1.8rem);
  margin-bottom: 0.4rem;
}

.section-subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.species-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
}

.species-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-teal);
  background: rgba(20, 184, 166, 0.12);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  width: fit-content;
  margin-bottom: 0.5rem;
}

.species-card h4 {
  font-size: 1.05rem;
  margin-bottom: 0.15rem;
}

.sci-name {
  font-size: 0.78rem;
  color: var(--text-dim);
  margin-bottom: 0.6rem;
}

.species-desc {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.45;
  flex: 1;
}
</style>
