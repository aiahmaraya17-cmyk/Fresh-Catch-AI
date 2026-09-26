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
const recipeRoutes = require('./routes/recipeRoutes');
const stallRoutes = require('./routes/stallRoutes');

const app = express();
const PORT = Number(process.env.PORT) || 5000;

function startServer(port) {
  const server = app.listen(port, () => {
    console.log(`====================================================`);
    console.log(` FreshCatch AI Backend REST API Server`);
    console.log(` Running on: http://localhost:${port}`);
    console.log(` Target Domain: Roxas, Oriental Mindoro Wet Market`);
    console.log(`====================================================`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.warn(`Port ${port} is busy. Retrying on ${port + 1}...`);
      startServer(port + 1);
      return;
    }

    console.error('Failed to start backend server:', err);
    process.exit(1);
  });
}

// Security & Parsing Middleware
app.use(helmet({
  crossOriginResourcePolicy: { policy: "cross-origin" }
}));
// CORS: allow only the configured front-end origins in production.
// Set CORS_ORIGINS to a comma-separated list, e.g.
//   CORS_ORIGINS=https://freshcatch.vercel.app,https://www.freshcatch.app
// If unset (local dev), all origins are allowed for convenience.
const allowedOrigins = (process.env.CORS_ORIGINS || '')
  .split(',')
  .map((o) => o.trim())
  .filter(Boolean);

app.use(cors({
  origin: (origin, callback) => {
    // Allow non-browser clients (curl, health checks, mobile apps) that send no Origin.
    if (!origin) return callback(null, true);
    // No allow-list configured → permissive (development default).
    if (allowedOrigins.length === 0) return callback(null, true);
    // Otherwise only permit explicitly allowed origins.
    if (allowedOrigins.includes(origin)) return callback(null, true);
    return callback(new Error(`Origin ${origin} is not allowed by CORS policy.`));
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json({ limit: '25mb' }));
app.use(express.urlencoded({ extended: true, limit: '25mb' }));

// Attach User from JWT Token
app.use(authenticateToken);

// Static file serving for uploads and dataset images.
// Reuse the exact same (env-configurable) directories as the upload middleware
// so served files and written files always match, including on a persistent disk.
const { uploadDir: uploadsPath, datasetDir: datasetPath } = require('./middleware/uploadMiddleware');

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
app.use('/api', recipeRoutes);
app.use('/api', stallRoutes);

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

startServer(PORT);

module.exports = app;
