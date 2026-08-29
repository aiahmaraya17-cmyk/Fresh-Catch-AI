const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');
const { requireAuth, requireRoles } = require('../middleware/authMiddleware');

router.get('/statistics', reportController.getStatistics);
router.get('/error-analysis', requireAuth, requireRoles(['admin', 'researcher']), reportController.getErrorAnalysis);
router.post('/error-analysis/review', requireAuth, requireRoles(['admin', 'researcher']), reportController.addResearcherReview);
router.get('/reports/export', requireAuth, requireRoles(['admin', 'researcher']), reportController.exportReport);

module.exports = router;
