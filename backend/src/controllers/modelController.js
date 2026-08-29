const db = require('../config/database');
const PythonBridgeService = require('../services/pythonBridgeService');

exports.getModels = (req, res) => {
  try {
    const models = db.prepare('SELECT * FROM models ORDER BY id DESC').all();
    const formatted = models.map(m => ({
      ...m,
      confusion_matrix: JSON.parse(m.confusion_matrix || '{}'),
      classification_report: JSON.parse(m.classification_report || '{}')
    }));
    res.json({ success: true, models: formatted });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to retrieve models: ' + err.message });
  }
};

exports.getActiveModel = (req, res) => {
  try {
    const model = db.prepare("SELECT * FROM models WHERE status = 'active' ORDER BY id DESC LIMIT 1").get();
    if (!model) {
      return res.json({ success: true, model: null });
    }

    const formatted = {
      ...model,
      confusion_matrix: JSON.parse(model.confusion_matrix || '{}'),
      classification_report: JSON.parse(model.classification_report || '{}')
    };
    res.json({ success: true, model: formatted });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving active model: ' + err.message });
  }
};

exports.activateModel = (req, res) => {
  try {
    const { id } = req.params;
    db.prepare("UPDATE models SET status = 'archived' WHERE status = 'active'").run();
    db.prepare("UPDATE models SET status = 'active' WHERE id = ?").run(id);
    res.json({ success: true, message: 'Active model updated successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error activating model: ' + err.message });
  }
};

exports.trainModel = async (req, res) => {
  try {
    const trainResult = await PythonBridgeService.triggerTraining();
    const evalResult = await PythonBridgeService.triggerEvaluation();

    const evalData = PythonBridgeService.getEvaluationResults();
    const historyData = PythonBridgeService.getTrainingHistory();

    if (evalData) {
      const version = `FreshCatch-CNN-v1.${Date.now().toString().slice(-4)}-MobileNetV2`;
      const insertStmt = db.prepare(`
        INSERT INTO models 
        (model_name, version, architecture, accuracy, precision, recall, f1_score, confusion_matrix, classification_report, file_path, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      db.prepare("UPDATE models SET status = 'archived' WHERE status = 'active'").run();

      insertStmt.run(
        'FreshCatch MobileNetV2 Retrained',
        version,
        'MobileNetV2 Transfer Learning + Dense Head',
        evalData.metrics.accuracy,
        evalData.metrics.precision_macro,
        evalData.metrics.recall_macro,
        evalData.metrics.f1_score_macro,
        JSON.stringify(evalData.confusion_matrix),
        JSON.stringify(evalData.per_class_metrics),
        'ai/models/saved/freshcatch_cnn_v1.joblib',
        'active'
      );
    }

    res.json({
      success: true,
      message: 'Model successfully trained and evaluated on Roxas wet market dataset.',
      trainOutput: trainResult.logs,
      evalOutput: evalResult.logs,
      evaluation: evalData,
      history: historyData
    });
  } catch (err) {
    console.error('Training error:', err);
    res.status(500).json({ success: false, message: 'Model training pipeline failed: ' + err.message });
  }
};

exports.getEvaluationMetrics = (req, res) => {
  try {
    const evalData = PythonBridgeService.getEvaluationResults();
    if (!evalData) {
      return res.status(404).json({ success: false, message: 'No evaluation results found on disk.' });
    }
    res.json({ success: true, evaluation: evalData });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error loading evaluation metrics: ' + err.message });
  }
};

exports.getTrainingHistory = (req, res) => {
  try {
    const histData = PythonBridgeService.getTrainingHistory();
    if (!histData) {
      return res.status(404).json({ success: false, message: 'No training history found.' });
    }
    res.json({ success: true, history: histData });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving training history: ' + err.message });
  }
};

exports.getEnvironmentalBenchmarks = (req, res) => {
  try {
    const envData = PythonBridgeService.getEnvironmentalResults();
    if (!envData) {
      return res.status(404).json({ success: false, message: 'No environmental benchmark data found.' });
    }
    res.json({ success: true, environmentalBenchmarks: envData });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving environmental benchmarks: ' + err.message });
  }
};
