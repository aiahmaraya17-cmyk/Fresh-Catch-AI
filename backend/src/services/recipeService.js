/**
 * recipeService.js
 * ----------------
 * Serves authentic FILIPINO fish recipes, filtered by FreshCatch AI's
 * food-safety rules. Recipe data is curated locally in
 * data/filipinoFishRecipes.js (real, editable, Filipino-only).
 *
 * Why local curated data instead of an external API:
 *   External free recipe APIs (e.g. TheMealDB) contain almost no Filipino
 *   dishes and ZERO Filipino fish recipes — no sinigang, paksiw, kinilaw,
 *   escabeche, inihaw, etc. To guarantee "Filipino food only" AND enforce
 *   freshness-based food-safety rules, the data must be curated in-app.
 *
 * Food-safety rules (non-negotiable):
 *   Fresh (rank 0)            → all dishes, including raw (kinilaw)
 *   Moderately Fresh (rank 1) → cooked dishes only (steamed, grilled, soup)
 *   Less Fresh (rank 2)       → thorough-cooking dishes only (fried, stewed)
 *   Not Fresh (rank 3)        → NO recipes; discard message only
 */

const { FILIPINO_FISH_RECIPES } = require('../data/filipinoFishRecipes');
const { thumbnailFor } = require('../data/recipeThumbnails');

// Freshness ranking — must match the grades produced by infer.py.
const FRESHNESS_RANK = {
  'fresh': 0,
  'moderately fresh': 1,
  'less fresh': 2,
  'not fresh': 3,
  // aliases / older or localized labels
  'spoiled': 3,
  'stale': 3,
  'bilasa': 3,
};

/** Normalise a classification string to a rank, tolerant of case/whitespace. */
function rankOf(classification) {
  if (!classification) return undefined;
  return FRESHNESS_RANK[String(classification).trim().toLowerCase()];
}

/**
 * MAIN: returns freshness-appropriate Filipino fish recipe suggestions.
 *
 * @param {string} classification  one of the SBRE grades
 * @param {string} [speciesName]   optional species to bias ordering
 * @param {number} [limit]         max recipes to return (default 6)
 * @returns {{available:boolean, reason:string, cuisine:string, recipes:Array}}
 */
function getRecipeSuggestions(classification, speciesName = '', limit = 6) {
  const fishRank = rankOf(classification);

  // ── Food-safety gate ─────────────────────────────────────────────────────
  // Rank 3 (Not Fresh / Spoiled) must NEVER receive cooking recipes.
  if (fishRank === undefined || fishRank >= 3) {
    return {
      available: false,
      reason: 'no_recipes_unsafe',
      cuisine: 'Filipino',
      message:
        'No recipes are provided because this fish is not safe to eat. ' +
        'Please discard it and do not cook or consume it.',
      recipes: [],
    };
  }

  const allowRaw = fishRank === 0;   // only Fresh may show raw dishes
  const sp = (speciesName || '').toLowerCase().split(/[\s(]/)[0]; // first word

  // A recipe is suitable when its minimum-required freshness rank is >=
  // the fish's rank. i.e. a Less-Fresh fish (2) sees only rank-2 dishes;
  // a Fresh fish (0) sees dishes of every rank.
  let matches = FILIPINO_FISH_RECIPES.filter((r) => {
    if (r.minFreshnessRank < fishRank) return false;   // too delicate for this fish
    if (r.isRaw && !allowRaw) return false;            // raw only for Fresh
    return true;
  });

  // Rank ordering: prefer species match, then dishes tuned to this exact grade.
  matches = matches
    .map((r) => {
      let score = 0;
      const speciesList = (r.species || []).map((s) => s.toLowerCase());
      if (sp && speciesList.some((s) => s.includes(sp) || sp.includes(s))) score += 5;
      if (speciesList.includes('*')) score += 1;
      // Prefer dishes whose minFreshnessRank matches the fish rank exactly
      // (most appropriate cooking intensity for this freshness level)
      if (r.minFreshnessRank === fishRank) score += 2;
      return { r, score };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ r }) => ({
      id:             r.id,
      name:           r.name,
      name_tagalog:   r.name_tagalog,
      area:           r.area,
      category:       'Filipino Seafood',
      cooking_method: r.cooking_method,
      prep_time_mins: r.prep_time_mins,
      // Locally-bundled SVG illustration (always renders — no external 404s).
      thumbnail:      thumbnailFor(r.id),
      description:    r.description,
      ingredients:    r.ingredients,
      steps:          r.steps,
      isRaw:          r.isRaw,
      youtube:        null,
      source:         null,
    }));

  return {
    available: matches.length > 0,
    reason: matches.length ? 'ok' : 'no_results',
    cuisine: 'Filipino',
    source: 'FreshCatch AI Filipino Recipe Collection',
    classification,
    recipes: matches,
  };
}

module.exports = { getRecipeSuggestions };
