const express = require('express');
const router = express.Router();
const predictionController = require('../controllers/predictionController');
const { uploadPrediction } = require('../middleware/uploadMiddleware');
const { requireAuth } = require('../middleware/authMiddleware');

// Authenticated Predict — users must be logged in to scan a fish.
router.post('/predict', requireAuth, uploadPrediction.single('image'), predictionController.predict);

// Predictions History & Details
router.get('/predictions', requireAuth, predictionController.getHistory);
router.get('/predictions/recent', predictionController.getRecentPublicPredictions);
router.get('/predictions/:id', requireAuth, predictionController.getPredictionById);
router.delete('/predictions/:id', requireAuth, predictionController.deletePrediction);

module.exports = router;
