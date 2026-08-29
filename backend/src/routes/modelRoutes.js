const express = require('express');
const router = express.Router();
const modelController = require('../controllers/modelController');
const { requireAuth, requireRoles } = require('../middleware/authMiddleware');

router.get('/models', requireAuth, requireRoles(['admin', 'researcher']), modelController.getModels);
router.get('/models/active', modelController.getActiveModel);
router.post('/models/activate/:id', requireAuth, requireRoles(['admin']), modelController.activateModel);
router.post('/models/train', requireAuth, requireRoles(['admin', 'researcher']), modelController.trainModel);

router.get('/evaluation', requireAuth, requireRoles(['admin', 'researcher']), modelController.getEvaluationMetrics);
router.get('/evaluation/history', requireAuth, requireRoles(['admin', 'researcher']), modelController.getTrainingHistory);
router.get('/environmental-testing', requireAuth, requireRoles(['admin', 'researcher']), modelController.getEnvironmentalBenchmarks);

module.exports = router;
