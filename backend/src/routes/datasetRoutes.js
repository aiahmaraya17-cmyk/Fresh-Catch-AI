const express = require('express');
const router = express.Router();
const datasetController = require('../controllers/datasetController');
const { uploadDataset } = require('../middleware/uploadMiddleware');
const { requireAuth, requireRoles } = require('../middleware/authMiddleware');

router.get('/dataset', requireAuth, requireRoles(['admin', 'researcher']), datasetController.getDataset);
router.get('/dataset/stats', requireAuth, requireRoles(['admin', 'researcher']), datasetController.getDatasetStats);
router.post('/dataset', requireAuth, requireRoles(['admin', 'researcher']), uploadDataset.single('image'), datasetController.uploadDatasetImage);
router.put('/dataset/:id', requireAuth, requireRoles(['admin', 'researcher']), datasetController.updateDatasetImage);
router.delete('/dataset/:id', requireAuth, requireRoles(['admin', 'researcher']), datasetController.deleteDatasetImage);

module.exports = router;
