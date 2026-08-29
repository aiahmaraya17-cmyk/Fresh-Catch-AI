const multer = require('multer');
const path = require('path');
const fs = require('fs');

const uploadDir = path.resolve(__dirname, '../../uploads');
const datasetDir = path.resolve(__dirname, '../../../ai/dataset/raw');

if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}
if (!fs.existsSync(datasetDir)) {
  fs.mkdirSync(datasetDir, { recursive: true });
}

// Storage for prediction uploads
const predictionStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase() || '.jpg';
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, `predict_${uniqueSuffix}${ext}`);
  }
});

// Storage for dataset training images
const datasetStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, datasetDir);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase() || '.jpg';
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, `dataset_${uniqueSuffix}${ext}`);
  }
});

function fileFilter(req, file, cb) {
  const allowedMimeTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  if (allowedMimeTypes.includes(file.mimetype.toLowerCase())) {
    cb(null, true);
  } else {
    cb(new Error('Unsupported file format. Please upload JPG, PNG, or WEBP images only.'), false);
  }
}

const uploadPrediction = multer({
  storage: predictionStorage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter
});

const uploadDataset = multer({
  storage: datasetStorage,
  limits: { fileSize: 15 * 1024 * 1024 },
  fileFilter
});

module.exports = {
  uploadPrediction,
  uploadDataset,
  uploadDir,
  datasetDir
};
