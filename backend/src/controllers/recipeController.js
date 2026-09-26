const { getRecipeSuggestions } = require('../services/recipeService');

/**
 * GET /api/recipes?classification=Fresh&species=Bangus&limit=6
 * Returns live, freshness-appropriate recipe suggestions from TheMealDB.
 * Open endpoint (no auth) — recipes are public, non-sensitive content.
 */
exports.getRecipes = async (req, res) => {
  try {
    const classification = (req.query.classification || '').trim();
    const species        = (req.query.species || '').trim();
    const limit          = Math.min(parseInt(req.query.limit, 10) || 6, 12);

    if (!classification) {
      return res.status(400).json({
        success: false,
        message: 'A "classification" query parameter is required (e.g. Fresh, Moderately Fresh).',
      });
    }

    const result = getRecipeSuggestions(classification, species, limit);

    return res.json({
      success: true,
      ...result,
    });
  } catch (err) {
    console.error('Recipe controller error:', err);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch recipe suggestions.',
      recipes: [],
    });
  }
};
