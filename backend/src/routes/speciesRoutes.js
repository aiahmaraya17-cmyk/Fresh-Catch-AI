const express = require('express');
const router = express.Router();
const speciesController = require('../controllers/speciesController');
const { requireAuth, requireRoles } = require('../middleware/authMiddleware');

router.get('/fish-species', speciesController.getSpecies);
router.post('/fish-species', requireAuth, requireRoles(['admin', 'researcher']), speciesController.createSpecies);
router.put('/fish-species/:id', requireAuth, requireRoles(['admin', 'researcher']), speciesController.updateSpecies);

module.exports = router;
