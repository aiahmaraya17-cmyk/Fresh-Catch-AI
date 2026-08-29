const db = require('../config/database');
const PythonBridgeService = require('../services/pythonBridgeService');

exports.getErrorAnalysis = (req, res) => {
  try {
    const evalData = PythonBridgeService.getEvaluationResults();
    const misclassifications = evalData ? evalData.misclassifications : [];

    // Also get manual researcher logs stored in database
    const dbLogs = db.prepare(`
      SELECT e.*, u.name AS reviewer_name
      FROM error_analysis_logs e
      LEFT JOIN users u ON e.reviewed_by = u.id
      ORDER BY e.created_at DESC
    `).all();

    res.json({
      success: true,
      misclassifications,
      customLogs: dbLogs
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving error analysis data: ' + err.message });
  }
};

exports.addResearcherReview = (req, res) => {
  try {
    const {
      image_url,
      actual_class,
      predicted_class,
      confidence,
      environmental_condition,
      error_cause,
      researcher_notes
    } = req.body;

    const reviewerId = req.user ? req.user.id : null;

    const stmt = db.prepare(`
      INSERT INTO error_analysis_logs
      (image_url, actual_class, predicted_class, confidence, environmental_condition, error_cause, researcher_notes, reviewed_by)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      image_url,
      actual_class,
      predicted_class,
      confidence,
      environmental_condition || 'Wet-market',
      error_cause || 'Visual similarity in transition stage',
      researcher_notes || '',
      reviewerId
    );

    res.status(201).json({
      success: true,
      message: 'Researcher review note logged successfully.',
      logId: info.lastInsertRowid
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to record error log: ' + err.message });
  }
};

exports.getStatistics = (req, res) => {
  try {
    const totalUsers = db.prepare('SELECT COUNT(*) AS count FROM users').get().count;
    const totalPredictions = db.prepare('SELECT COUNT(*) AS count FROM predictions').get().count;
    const totalDataset = db.prepare('SELECT COUNT(*) AS count FROM dataset_images').get().count;

    const activeModel = db.prepare("SELECT * FROM models WHERE status = 'active' ORDER BY id DESC LIMIT 1").get();

    const categoryDistribution = db.prepare(`
      SELECT classification, COUNT(*) AS count 
      FROM predictions 
      GROUP BY classification
    `).all();

    const speciesDistribution = db.prepare(`
      SELECT s.local_name, COUNT(p.id) AS count 
      FROM predictions p 
      JOIN fish_species s ON p.species_id = s.id 
      GROUP BY s.local_name
    `).all();

    const recentPredictions = db.prepare(`
      SELECT p.id, p.image_url, p.classification, p.confidence, p.created_at, s.local_name AS species_local_name
      FROM predictions p
      LEFT JOIN fish_species s ON p.species_id = s.id
      ORDER BY p.created_at DESC LIMIT 6
    `).all();

    res.json({
      success: true,
      stats: {
        totalUsers,
        totalPredictions,
        totalDataset,
        activeModel: activeModel ? {
          name: activeModel.model_name,
          version: activeModel.version,
          architecture: activeModel.architecture,
          accuracy: activeModel.accuracy,
          f1_score: activeModel.f1_score
        } : null,
        categoryDistribution,
        speciesDistribution,
        recentPredictions
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving statistics: ' + err.message });
  }
};

exports.exportReport = (req, res) => {
  try {
    const { format = 'json', type = 'predictions' } = req.query;

    let data;
    if (type === 'dataset') {
      data = db.prepare(`
        SELECT d.id, d.filename, s.name AS species, c.name AS category, d.split,
               d.lighting_condition, d.background_condition, d.fish_orientation, d.distance_condition, d.image_quality, d.source, d.capture_date
        FROM dataset_images d
        LEFT JOIN fish_species s ON d.species_id = s.id
        LEFT JOIN freshness_categories c ON d.freshness_category_id = c.id
      `).all();
    } else {
      data = db.prepare(`
        SELECT p.id, u.name AS user_name, s.name AS species, p.classification, p.confidence, p.model_version, p.created_at
        FROM predictions p
        LEFT JOIN users u ON p.user_id = u.id
        LEFT JOIN fish_species s ON p.species_id = s.id
        ORDER BY p.created_at DESC
      `).all();
    }

    if (format === 'csv') {
      if (data.length === 0) {
        return res.header('Content-Type', 'text/csv').send('No data');
      }
      const headers = Object.keys(data[0]).join(',');
      const rows = data.map(row => Object.values(row).map(v => `"${(v || '').toString().replace(/"/g, '""')}"`).join(','));
      const csv = [headers, ...rows].join('\n');

      res.header('Content-Type', 'text/csv');
      res.attachment(`freshcatch_${type}_report_${Date.now()}.csv`);
      return res.send(csv);
    }

    res.json({
      success: true,
      reportType: type,
      exportedAt: new Date().toISOString(),
      recordCount: data.length,
      data
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Export failed: ' + err.message });
  }
};
