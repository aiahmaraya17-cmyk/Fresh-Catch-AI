require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');
const fs = require('fs');

// Initialize database
require('./config/database');

const { authenticateToken } = require('./middleware/authMiddleware');

const authRoutes = require('./routes/authRoutes');
const predictRoutes = require('./routes/predictRoutes');
const datasetRoutes = require('./routes/datasetRoutes');
const modelRoutes = require('./routes/modelRoutes');
const speciesRoutes = require('./routes/speciesRoutes');
const categoryRoutes = require('./routes/categoryRoutes');
const reportRoutes = require('./routes/reportRoutes');

const app = express();
const PORT = process.env.PORT || 5000;

// Security & Parsing Middleware
app.use(helmet({
  crossOriginResourcePolicy: { policy: "cross-origin" }
}));
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json({ limit: '25mb' }));
app.use(express.urlencoded({ extended: true, limit: '25mb' }));

// Attach User from JWT Token
app.use(authenticateToken);

// Static file serving for uploads and dataset images
const uploadsPath = path.resolve(__dirname, '../uploads');
const datasetPath = path.resolve(__dirname, '../../ai/dataset/raw');

if (!fs.existsSync(uploadsPath)) fs.mkdirSync(uploadsPath, { recursive: true });
if (!fs.existsSync(datasetPath)) fs.mkdirSync(datasetPath, { recursive: true });

app.use('/uploads', express.static(uploadsPath));
app.use('/dataset/raw', express.static(datasetPath));

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api', predictRoutes);
app.use('/api', datasetRoutes);
app.use('/api', modelRoutes);
app.use('/api', speciesRoutes);
app.use('/api', categoryRoutes);
app.use('/api', reportRoutes);

// Health Check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    project: 'FreshCatch AI',
    domain: 'Roxas, Oriental Mindoro',
    targetYear: 2026,
    activeArchitecture: 'MobileNetV2 Transfer Learning CNN',
    timestamp: new Date().toISOString()
  });
});

// Global Error Handler
app.use((err, req, res, next) => {
  console.error('Unhandled Error:', err);
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal Server Error'
  });
});

app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(` FreshCatch AI Backend REST API Server`);
  console.log(` Running on: http://localhost:${PORT}`);
  console.log(` Target Domain: Roxas, Oriental Mindoro Wet Market`);
  console.log(`====================================================`);
});

module.exports = app;
