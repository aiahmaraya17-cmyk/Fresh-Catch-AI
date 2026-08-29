const express = require('express');
const router = express.Router();
const predictionController = require('../controllers/predictionController');
const { uploadPrediction } = require('../middleware/uploadMiddleware');
const { requireAuth } = require('../middleware/authMiddleware');

// Public or Authenticated Predict
router.post('/predict', uploadPrediction.single('image'), predictionController.predict);

// Predictions History & Details
router.get('/predictions', requireAuth, predictionController.getHistory);
router.get('/predictions/recent', predictionController.getRecentPublicPredictions);
router.get('/predictions/:id', requireAuth, predictionController.getPredictionById);
router.delete('/predictions/:id', requireAuth, predictionController.deletePrediction);

module.exports = router;
