/**
 * recipeThumbnails.js
 * -------------------
 * Self-contained SVG illustrations for each Filipino fish recipe, returned as
 * base64 data URIs. Bundled locally so thumbnails ALWAYS render — no external
 * requests, no 404s, no hotlink failures (the previous Wikimedia URLs were
 * unreliable and left empty image boxes in the UI).
 *
 * Each illustration is keyed by recipe id and themed to its cooking method,
 * with a palette that matches the app's dark, teal-accented result screen.
 *
 * Usage: thumbnailFor(id) → 'data:image/svg+xml;base64,...'
 */

// Shared palette (matches the frontend CSS variables)
const C = {
  bgTop: '#0e2233',
  bgBot: '#0a1826',
  fish: '#7fd4c9',
  fishDark: '#3fa89b',
  accent: '#14b8a6',
  warm: '#f2a65a',
  warmDeep: '#e07a3c',
  green: '#4caf7d',
  broth: '#d98b46',
  cream: '#e9d9b8',
  red: '#e05d5d',
  steam: '#bfe9e3',
  plate: '#12303f',
};

// Wrap inner SVG content in a framed 320x240 canvas with a gradient backdrop.
function frame(inner, glow = C.accent) {
  return `
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240" viewBox="0 0 320 240">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${C.bgTop}"/>
      <stop offset="1" stop-color="${C.bgBot}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.42" r="0.75">
      <stop offset="0" stop-color="${glow}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="${glow}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="320" height="240" fill="url(#bg)"/>
  <rect width="320" height="240" fill="url(#glow)"/>
  ${inner}
</svg>`.trim();
}

// A simple side-view fish shape centred at (cx, cy).
function fish(cx, cy, scale = 1, body = C.fish, edge = C.fishDark) {
  const s = scale;
  return `
  <g transform="translate(${cx} ${cy}) scale(${s})">
    <path d="M-70,0 C-45,-32 40,-32 66,0 C40,32 -45,32 -70,0 Z"
          fill="${body}" stroke="${edge}" stroke-width="3"/>
    <path d="M66,0 L98,-24 L92,0 L98,24 Z" fill="${body}" stroke="${edge}" stroke-width="3"/>
    <path d="M-6,-30 C6,-46 26,-46 30,-30" fill="${body}" stroke="${edge}" stroke-width="3"/>
    <circle cx="-48" cy="-6" r="6" fill="#0a1826"/>
    <circle cx="-49" cy="-8" r="2" fill="#fff"/>
    <path d="M-30,-14 C-10,-4 -10,4 -30,14" fill="none" stroke="${edge}" stroke-width="2.5" opacity="0.6"/>
    <path d="M-14,-16 C6,-6 6,6 -14,16" fill="none" stroke="${edge}" stroke-width="2.5" opacity="0.5"/>
  </g>`;
}

// Rising steam curls starting near (x, y).
function steam(x, y) {
  return `
  <g stroke="${C.steam}" stroke-width="3" fill="none" opacity="0.55" stroke-linecap="round">
    <path d="M${x},${y} c-8,-14 8,-22 0,-38"/>
    <path d="M${x + 20},${y} c-8,-14 8,-24 0,-42"/>
    <path d="M${x + 40},${y} c-8,-14 8,-22 0,-38"/>
  </g>`;
}

// An oval plate under the food.
function plate(cx, cy, rx = 120, ry = 26) {
  return `
  <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${C.plate}" stroke="#1c4a5f" stroke-width="3"/>
  <ellipse cx="${cx}" cy="${cy - 3}" rx="${rx - 16}" ry="${ry - 8}" fill="#0c2130"/>`;
}

// ── Per-recipe illustrations ───────────────────────────────────────────────
const ART = {
  // Kinilaw — raw cubes with calamansi & chili on a plate
  'kinilaw': frame(`
    ${plate(160, 168)}
    <g>
      ${[[128,150],[152,158],[176,150],[140,166],[168,166],[192,158]]
        .map(([x,y]) => `<rect x="${x}" y="${y}" width="20" height="20" rx="4" fill="${C.fish}" stroke="${C.fishDark}" stroke-width="2" transform="rotate(${(x*y)%40-20} ${x+10} ${y+10})"/>`)
        .join('')}
      <circle cx="118" cy="150" r="10" fill="${C.warm}"/>
      <circle cx="205" cy="152" r="9" fill="${C.warm}"/>
      <path d="M150,132 q6,-10 12,0" stroke="${C.red}" stroke-width="4" fill="none" stroke-linecap="round"/>
    </g>
    <text x="160" y="214" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="${C.steam}" opacity="0.8">Kinilaw</text>
  `, C.fish),

  // Inihaw — grilled fish over flames with grill bars
  'inihaw-na-isda': frame(`
    ${fish(158, 120, 0.95, '#8bbf8f', '#4f7a53')}
    <g stroke="#5a3a22" stroke-width="6" stroke-linecap="round" opacity="0.85">
      <line x1="70" y1="176" x2="250" y2="176"/>
      <line x1="70" y1="188" x2="250" y2="188"/>
    </g>
    <g stroke="${C.warmDeep}" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.9">
      <path d="M110,176 c-6,-14 8,-18 2,-34"/>
      <path d="M160,176 c-6,-14 8,-20 2,-38"/>
      <path d="M210,176 c-6,-14 8,-18 2,-34"/>
    </g>
    <g stroke="${C.warm}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.85">
      <path d="M120,176 c-4,-8 5,-10 1,-20"/>
      <path d="M170,176 c-4,-8 5,-12 1,-24"/>
    </g>
    <text x="160" y="214" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="${C.warm}" opacity="0.85">Inihaw</text>
  `, C.warmDeep),

  // Pinaputok — fish wrapped in banana leaf, steaming
  'pinaputok-na-tilapia': frame(`
    ${steam(150, 96)}
    <g transform="translate(160 140)">
      <path d="M-96,0 C-70,-40 70,-40 96,0 C70,40 -70,40 -96,0 Z" fill="${C.green}" stroke="#2f7d4f" stroke-width="3"/>
      <path d="M-96,0 L96,0" stroke="#2f7d4f" stroke-width="3" opacity="0.7"/>
      ${Array.from({length:9}).map((_,i)=>`<line x1="${-80+i*20}" y1="-2" x2="${-88+i*20}" y2="-24" stroke="#2f7d4f" stroke-width="2" opacity="0.6"/>`).join('')}
      ${Array.from({length:9}).map((_,i)=>`<line x1="${-80+i*20}" y1="2" x2="${-88+i*20}" y2="24" stroke="#2f7d4f" stroke-width="2" opacity="0.6"/>`).join('')}
      <ellipse cx="0" cy="0" rx="40" ry="14" fill="#f3e6c9" opacity="0.85"/>
    </g>
    <text x="160" y="214" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="${C.green}" opacity="0.9">Pinaputok</text>
  `, C.green),

  // Sinigang — sour soup bowl with fish steak & veggies, steam
  'sinigang-na-isda': frame(`
    ${steam(150, 84)}
    <path d="M78,120 a82,82 0 0 0 164,0 Z" fill="${C.broth}" stroke="#a86428" stroke-width="3"/>
    <ellipse cx="160" cy="120" rx="82" ry="20" fill="#e5a15a"/>
    <ellipse cx="160" cy="120" rx="82" ry="20" fill="none" stroke="#a86428" stroke-width="3"/>
    <g>
      <ellipse cx="150" cy="118" rx="34" ry="12" fill="${C.fish}" stroke="${C.fishDark}" stroke-width="2"/>
      <circle cx="118" cy="122" r="7" fill="${C.red}"/>
      <rect x="182" y="112" width="26" height="8" rx="4" fill="${C.green}" transform="rotate(-18 195 116)"/>
      <rect x="120" y="108" width="8" height="22" rx="4" fill="${C.green}"/>
    </g>
    <text x="160" y="206" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="#f0b072" opacity="0.9">Sinigang</text>
  `, C.warm),

  // Paksiw — vinegar stew in a pot with ginger/chili
  'paksiw-na-isda': frame(`
    ${steam(150, 88)}
    <rect x="86" y="118" width="148" height="74" rx="12" fill="#1a3a4a" stroke="#2c5a6f" stroke-width="3"/>
    <ellipse cx="160" cy="120" rx="76" ry="18" fill="#c9a24a" stroke="#8f7024" stroke-width="3"/>
    <ellipse cx="150" cy="120" rx="34" ry="10" fill="${C.fish}" stroke="${C.fishDark}" stroke-width="2"/>
    <path d="M182,118 q6,-8 12,0" stroke="${C.red}" stroke-width="4" fill="none" stroke-linecap="round"/>
    <rect x="60" y="140" width="18" height="10" rx="4" fill="#1a3a4a" stroke="#2c5a6f" stroke-width="3"/>
    <rect x="242" y="140" width="18" height="10" rx="4" fill="#1a3a4a" stroke="#2c5a6f" stroke-width="3"/>
    <text x="160" y="210" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="#e0c273" opacity="0.9">Paksiw</text>
  `, '#c9a24a'),

  // Pritong — crispy fried fish in a pan
  'pritong-isda': frame(`
    ${fish(150, 128, 0.95, '#e0a24c', '#a86a1e')}
    <ellipse cx="150" cy="150" rx="120" ry="30" fill="#141414" opacity="0.55"/>
    <path d="M30,150 a120,30 0 0 0 240,0" fill="none" stroke="#3a3a3a" stroke-width="6"/>
    <rect x="266" y="140" width="46" height="12" rx="6" fill="#3a3a3a"/>
    <g fill="${C.warm}" opacity="0.8">
      <circle cx="120" cy="150" r="3"/><circle cx="180" cy="152" r="3"/><circle cx="150" cy="158" r="3"/>
    </g>
    <text x="150" y="206" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="#f0b862" opacity="0.9">Pritong Isda</text>
  `, C.warm),

  // Escabeche — fried fish with colourful sweet-sour sauce
  'escabeche': frame(`
    ${plate(160, 158, 122, 26)}
    ${fish(150, 132, 0.9, '#e0a24c', '#a86a1e')}
    <g>
      <rect x="112" y="120" width="16" height="7" rx="3" fill="${C.red}" transform="rotate(20 120 123)"/>
      <rect x="178" y="118" width="16" height="7" rx="3" fill="${C.warm}" transform="rotate(-15 186 121)"/>
      <rect x="150" y="112" width="16" height="7" rx="3" fill="${C.green}" transform="rotate(35 158 115)"/>
      <rect x="132" y="140" width="16" height="7" rx="3" fill="${C.warm}" transform="rotate(-25 140 143)"/>
    </g>
    <text x="160" y="204" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="#f0b862" opacity="0.9">Escabeche</text>
  `, C.warm),

  // Ginataang — fish in creamy coconut milk with greens
  'ginataang-isda': frame(`
    ${steam(150, 88)}
    <path d="M78,120 a82,82 0 0 0 164,0 Z" fill="${C.cream}" stroke="#b9a678" stroke-width="3"/>
    <ellipse cx="160" cy="120" rx="82" ry="20" fill="#f2e8cf"/>
    <ellipse cx="160" cy="120" rx="82" ry="20" fill="none" stroke="#b9a678" stroke-width="3"/>
    <ellipse cx="152" cy="118" rx="32" ry="11" fill="${C.fish}" stroke="${C.fishDark}" stroke-width="2"/>
    <path d="M186,112 q10,-6 18,2 q-8,8 -18,-2" fill="${C.green}"/>
    <path d="M120,116 q-10,-6 -18,2 q8,8 18,-2" fill="${C.green}"/>
    <path d="M176,124 q6,-8 12,0" stroke="${C.red}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
    <text x="160" y="206" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="#d9c79a" opacity="0.9">Ginataang</text>
  `, C.cream),
};

// Generic fallback illustration (a plain teal fish) for any unknown id.
const FALLBACK = frame(`${fish(160, 128, 1.05)}
  <text x="160" y="206" text-anchor="middle" font-family="Segoe UI,Arial" font-size="16" fill="${C.steam}" opacity="0.8">Filipino Fish Dish</text>`);

function toDataUri(svg) {
  return 'data:image/svg+xml;base64,' + Buffer.from(svg, 'utf8').toString('base64');
}

// Pre-encode once at module load.
const _CACHE = {};
for (const [id, svg] of Object.entries(ART)) _CACHE[id] = toDataUri(svg);
const _FALLBACK_URI = toDataUri(FALLBACK);

function thumbnailFor(id) {
  return _CACHE[id] || _FALLBACK_URI;
}

module.exports = { thumbnailFor };
