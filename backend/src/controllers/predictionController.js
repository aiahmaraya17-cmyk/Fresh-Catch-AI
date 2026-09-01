const path = require('path');
const fs = require('fs');
const db = require('../config/database');
const PythonBridgeService = require('../services/pythonBridgeService');

exports.predict = async (req, res) => {
  try {
    if (!req.file && !req.body.image_data) {
      return res.status(400).json({
        success: false,
        message: 'No fish image provided. Please capture or upload a photo of the fish.'
      });
    }

    let imagePath;
    let imageUrl;

    if (req.file) {
      imagePath = req.file.path;
      imageUrl = `/uploads/${req.file.filename}`;
    } else {
      // Handle base64 camera upload
      const base64Data = req.body.image_data.replace(/^data:image\/\w+;base64,/, '');
      const filename = `camera_${Date.now()}_${Math.round(Math.random() * 1e9)}.jpg`;
      const uploadDir = path.resolve(__dirname, '../../uploads');
      imagePath = path.join(uploadDir, filename);
      fs.writeFileSync(imagePath, Buffer.from(base64Data, 'base64'));
      imageUrl = `/uploads/${filename}`;
    }

    // Step 1: Run Inference through Python CNN engine
    const inferenceResult = await PythonBridgeService.runInference(imagePath);

    // If quality check rejected image
    if (!inferenceResult.success && inferenceResult.quality_check && !inferenceResult.quality_check.is_acceptable) {
      return res.status(422).json({
        success: false,
        quality_rejected: true,
        quality_check: inferenceResult.quality_check,
        message: inferenceResult.recommendation || 'Image quality is insufficient for reliable visual classification.',
        disclaimer: inferenceResult.disclaimer
      });
    }

    if (!inferenceResult.success) {
      return res.status(500).json({
        success: false,
        message: inferenceResult.error || 'AI classification service encountered an issue.'
      });
    }

    // Determine Species ID if provided or inferred
    let speciesId = null;
    if (req.body.species_id) {
      speciesId = parseInt(req.body.species_id, 10);
    } else if (req.body.species_name) {
      const sp = db.prepare('SELECT id FROM fish_species WHERE name LIKE ? OR local_name LIKE ?').get(
        `%${req.body.species_name}%`,
        `%${req.body.species_name}%`
      );
      if (sp) speciesId = sp.id;
    }

    // Step 2: Store Prediction Record in Database
    const userId = req.user ? req.user.id : null;
    const stmt = db.prepare(`
      INSERT INTO predictions 
      (user_id, species_id, image_url, classification, confidence, class_probabilities, visual_indicators, recommendation, recommendation_tagalog, quality_metrics, model_version)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      userId,
      speciesId,
      imageUrl,
      inferenceResult.classification,
      inferenceResult.confidence,
      JSON.stringify(inferenceResult.class_probabilities),
      JSON.stringify(inferenceResult.visualIndicators),
      inferenceResult.recommendation,
      inferenceResult.recommendation_tagalog || '',
      JSON.stringify(inferenceResult.quality_metrics || {}),
      inferenceResult.modelVersion || 'FreshCatch-CNN-v1.0-MobileNetV2'
    );

    res.json({
      success: true,
      predictionId: info.lastInsertRowid,
      imageUrl,
      classification: inferenceResult.classification,
      confidence: inferenceResult.confidence,
      confidence_percentage: inferenceResult.confidence_percentage,
      class_probabilities: inferenceResult.class_probabilities,
      visualIndicators: inferenceResult.visualIndicators,
      recommendation: inferenceResult.recommendation,
      recommendation_tagalog: inferenceResult.recommendation_tagalog,
      consumption_guidance: inferenceResult.consumption_guidance || null,
      is_safe_to_cook: inferenceResult.is_safe_to_cook ?? true,
      food_safety_warning: inferenceResult.food_safety_warning ?? null,
      food_safety_warning_tagalog: inferenceResult.food_safety_warning_tagalog ?? null,
      heuristic_override: inferenceResult.heuristic_override ?? false,
      quality_metrics: inferenceResult.quality_metrics,
      modelVersion: inferenceResult.modelVersion,
      architecture: inferenceResult.architecture,
      disclaimer: inferenceResult.disclaimer,
      disclaimer_tagalog: inferenceResult.disclaimer_tagalog,
      createdAt: new Date().toISOString()
    });
  } catch (err) {
    console.error('Prediction controller error:', err);
    res.status(500).json({
      success: false,
      message: 'Failed to process fish image: ' + err.message
    });
  }
};

exports.getHistory = (req, res) => {
  try {
    const userId = req.user.id;
    const { species, category, search, limit = 50, offset = 0 } = req.query;

    let query = `
      SELECT p.*, s.name AS species_name, s.local_name AS species_local_name
      FROM predictions p
      LEFT JOIN fish_species s ON p.species_id = s.id
      WHERE 1=1
    `;
    const params = [];

    // Admins and researchers can view all or filter by user, normal users view their own
    if (!['admin', 'researcher'].includes(req.user.role)) {
      query += ' AND p.user_id = ?';
      params.push(userId);
    } else if (req.query.user_id) {
      query += ' AND p.user_id = ?';
      params.push(req.query.user_id);
    }

    if (species) {
      query += ' AND (s.name LIKE ? OR s.local_name LIKE ?)';
      params.push(`%${species}%`, `%${species}%`);
    }

    if (category) {
      query += ' AND p.classification = ?';
      params.push(category);
    }

    if (search) {
      query += ' AND (p.classification LIKE ? OR s.name LIKE ? OR p.recommendation LIKE ?)';
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }

    query += ' ORDER BY p.created_at DESC LIMIT ? OFFSET ?';
    params.push(parseInt(limit, 10), parseInt(offset, 10));

    const rows = db.prepare(query).all(...params);

    const predictions = rows.map(r => ({
      ...r,
      class_probabilities: JSON.parse(r.class_probabilities || '{}'),
      visual_indicators: JSON.parse(r.visual_indicators || '[]'),
      quality_metrics: JSON.parse(r.quality_metrics || '{}')
    }));

    res.json({ success: true, predictions, total: predictions.length });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to retrieve prediction history: ' + err.message });
  }
};

exports.getPredictionById = (req, res) => {
  try {
    const { id } = req.params;
    const row = db.prepare(`
      SELECT p.*, s.name AS species_name, s.local_name AS species_local_name, s.scientific_name, u.name AS user_name
      FROM predictions p
      LEFT JOIN fish_species s ON p.species_id = s.id
      LEFT JOIN users u ON p.user_id = u.id
      WHERE p.id = ?
    `).get(id);

    if (!row) {
      return res.status(404).json({ success: false, message: 'Prediction record not found.' });
    }

    const prediction = {
      ...row,
      class_probabilities: JSON.parse(row.class_probabilities || '{}'),
      visual_indicators: JSON.parse(row.visual_indicators || '[]'),
      quality_metrics: JSON.parse(row.quality_metrics || '{}')
    };

    res.json({ success: true, prediction });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving prediction: ' + err.message });
  }
};

exports.deletePrediction = (req, res) => {
  try {
    const { id } = req.params;
    const row = db.prepare('SELECT user_id FROM predictions WHERE id = ?').get(id);

    if (!row) {
      return res.status(404).json({ success: false, message: 'Prediction not found.' });
    }

    if (row.user_id !== req.user.id && !['admin', 'researcher'].includes(req.user.role)) {
      return res.status(403).json({ success: false, message: 'Unauthorized to delete this prediction.' });
    }

    db.prepare('DELETE FROM predictions WHERE id = ?').run(id);
    res.json({ success: true, message: 'Prediction deleted successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error deleting prediction: ' + err.message });
  }
};

exports.getRecentPublicPredictions = (req, res) => {
  try {
    const rows = db.prepare(`
      SELECT p.id, p.image_url, p.classification, p.confidence, p.created_at, s.local_name AS species_local_name
      FROM predictions p
      LEFT JOIN fish_species s ON p.species_id = s.id
      ORDER BY p.created_at DESC LIMIT 8
    `).all();

    res.json({ success: true, recentPredictions: rows });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving recent predictions: ' + err.message });
  }
};
