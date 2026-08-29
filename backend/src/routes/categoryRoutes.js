const express = require('express');
const router = express.Router();
const categoryController = require('../controllers/categoryController');
const { requireAuth, requireRoles } = require('../middleware/authMiddleware');

router.get('/freshness-categories', categoryController.getCategories);
router.put('/freshness-categories/:id', requireAuth, requireRoles(['admin', 'researcher']), categoryController.updateCategory);

module.exports = router;
