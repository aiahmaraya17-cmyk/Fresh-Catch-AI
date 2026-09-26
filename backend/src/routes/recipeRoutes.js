const express = require('express');
const router = express.Router();
const recipeController = require('../controllers/recipeController');

// Public endpoint — freshness-appropriate recipe suggestions from TheMealDB.
router.get('/recipes', recipeController.getRecipes);

module.exports = router;
