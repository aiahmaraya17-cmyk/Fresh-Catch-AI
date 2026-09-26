const express = require('express');
const router = express.Router();
const stallController = require('../controllers/stallController');
const { requireAuth, requireRoles } = require('../middleware/authMiddleware');

// Public — stall directory and profiles (consumer trust layer)
router.get('/stalls', stallController.listStalls);

// Vendor — must come BEFORE '/stalls/:id' so 'me' is not treated as an id
router.get('/stalls/me/mine', requireAuth, requireRoles(['vendor', 'admin']), stallController.getMyStall);
router.post('/stalls', requireAuth, requireRoles(['vendor', 'admin']), stallController.createStall);

// Public — single stall profile with recent freshness scans
router.get('/stalls/:id', stallController.getStall);

// Owner or admin — update stall
router.put('/stalls/:id', requireAuth, requireRoles(['vendor', 'admin']), stallController.updateStall);

module.exports = router;
