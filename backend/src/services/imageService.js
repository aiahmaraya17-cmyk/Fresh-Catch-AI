/**
 * FreshCatch AI - Image Service
 * Handles image file cleanup and path utilities.
 */
const fs = require('fs');
const path = require('path');

const UPLOADS_DIR = path.resolve(__dirname, '../../uploads');

/**
 * Deletes a prediction image file from disk.
 * @param {string} imageUrl - Relative URL like /uploads/predict_xxx.jpg
 */
function deletePredictionImage(imageUrl) {
  if (!imageUrl) return;
  const filename = path.basename(imageUrl);
  const filePath = path.join(UPLOADS_DIR, filename);
  if (fs.existsSync(filePath)) {
    try {
      fs.unlinkSync(filePath);
    } catch (err) {
      console.warn('Could not delete image file:', filePath, err.message);
    }
  }
}

/**
 * Returns the absolute path for a prediction upload.
 * @param {string} filename
 */
function getUploadPath(filename) {
  return path.join(UPLOADS_DIR, filename);
}

/**
 * Ensures the uploads directory exists.
 */
function ensureUploadsDir() {
  if (!fs.existsSync(UPLOADS_DIR)) {
    fs.mkdirSync(UPLOADS_DIR, { recursive: true });
  }
}

module.exports = { deletePredictionImage, getUploadPath, ensureUploadsDir };
