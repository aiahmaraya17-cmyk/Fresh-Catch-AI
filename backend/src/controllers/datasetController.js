const fs = require('fs');
const path = require('path');
const db = require('../config/database');

exports.getDataset = (req, res) => {
  try {
    const { species_id, freshness_id, split, lighting, background, orientation, quality, search, limit = 50, offset = 0 } = req.query;

    let query = `
      SELECT d.*, s.name AS species_name, s.local_name AS species_local_name, c.name AS category_name, c.tagalog_name AS category_tagalog
      FROM dataset_images d
      LEFT JOIN fish_species s ON d.species_id = s.id
      LEFT JOIN freshness_categories c ON d.freshness_category_id = c.id
      WHERE 1=1
    `;
    const params = [];

    if (species_id) {
      query += ' AND d.species_id = ?';
      params.push(species_id);
    }
    if (freshness_id) {
      query += ' AND d.freshness_category_id = ?';
      params.push(freshness_id);
    }
    if (split) {
      query += ' AND d.split = ?';
      params.push(split);
    }
    if (lighting) {
      query += ' AND d.lighting_condition = ?';
      params.push(lighting);
    }
    if (background) {
      query += ' AND d.background_condition = ?';
      params.push(background);
    }
    if (orientation) {
      query += ' AND d.fish_orientation = ?';
      params.push(orientation);
    }
    if (quality) {
      query += ' AND d.image_quality = ?';
      params.push(quality);
    }
    if (search) {
      query += ' AND (d.filename LIKE ? OR s.name LIKE ? OR c.name LIKE ? OR d.source LIKE ?)';
      params.push(`%${search}%`, `%${search}%`, `%${search}%`, `%${search}%`);
    }

    const countQuery = query.replace('SELECT d.*, s.name AS species_name, s.local_name AS species_local_name, c.name AS category_name, c.tagalog_name AS category_tagalog', 'SELECT COUNT(*) AS total');
    const totalCount = db.prepare(countQuery).get(...params).total;

    query += ' ORDER BY d.id DESC LIMIT ? OFFSET ?';
    params.push(parseInt(limit, 10), parseInt(offset, 10));

    const images = db.prepare(query).all(...params);

    res.json({
      success: true,
      total: totalCount,
      count: images.length,
      images
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to retrieve dataset: ' + err.message });
  }
};

exports.getDatasetStats = (req, res) => {
  try {
    const total = db.prepare('SELECT COUNT(*) AS count FROM dataset_images').get().count;

    const splitCounts = db.prepare('SELECT split, COUNT(*) as count FROM dataset_images GROUP BY split').all();
    const categoryCounts = db.prepare(`
      SELECT c.name, COUNT(d.id) as count 
      FROM freshness_categories c 
      LEFT JOIN dataset_images d ON c.id = d.freshness_category_id 
      GROUP BY c.name
    `).all();

    const speciesCounts = db.prepare(`
      SELECT s.local_name, COUNT(d.id) as count 
      FROM fish_species s 
      LEFT JOIN dataset_images d ON s.id = d.species_id 
      GROUP BY s.local_name
    `).all();

    const lightingCounts = db.prepare('SELECT lighting_condition, COUNT(*) as count FROM dataset_images GROUP BY lighting_condition').all();
    const backgroundCounts = db.prepare('SELECT background_condition, COUNT(*) as count FROM dataset_images GROUP BY background_condition').all();

    res.json({
      success: true,
      stats: {
        total,
        splits: splitCounts,
        categories: categoryCounts,
        species: speciesCounts,
        lighting: lightingCounts,
        backgrounds: backgroundCounts
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving dataset stats: ' + err.message });
  }
};

exports.uploadDatasetImage = (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, message: 'Image file is required.' });
    }

    const {
      species_id = 1,
      freshness_category_id = 1,
      split = 'train',
      lighting_condition = 'Normal',
      background_condition = 'Wet-market',
      fish_orientation = 'Side',
      distance_condition = 'Medium',
      image_quality = 'High',
      source = 'Roxas Public Market, Oriental Mindoro',
      capture_date = new Date().toISOString().split('T')[0]
    } = req.body;

    const filename = req.file.filename;
    const imageUrl = `/dataset/raw/${filename}`;

    const stmt = db.prepare(`
      INSERT INTO dataset_images 
      (filename, image_url, species_id, freshness_category_id, split, lighting_condition, background_condition, fish_orientation, distance_condition, image_quality, source, capture_date)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      filename,
      imageUrl,
      species_id,
      freshness_category_id,
      split,
      lighting_condition,
      background_condition,
      fish_orientation,
      distance_condition,
      image_quality,
      source,
      capture_date
    );

    res.status(201).json({
      success: true,
      message: 'Dataset specimen added successfully.',
      datasetId: info.lastInsertRowid,
      imageUrl
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to upload dataset image: ' + err.message });
  }
};

exports.deleteDatasetImage = (req, res) => {
  try {
    const { id } = req.params;
    const item = db.prepare('SELECT filename FROM dataset_images WHERE id = ?').get(id);

    if (!item) {
      return res.status(404).json({ success: false, message: 'Dataset image not found.' });
    }

    const fullPath = path.resolve(__dirname, '../../../ai/dataset/raw', item.filename);
    if (fs.existsSync(fullPath)) {
      try { fs.unlinkSync(fullPath); } catch (e) { /* ignore unlink failure */ }
    }

    db.prepare('DELETE FROM dataset_images WHERE id = ?').run(id);
    res.json({ success: true, message: 'Dataset image deleted successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error deleting dataset image: ' + err.message });
  }
};

exports.updateDatasetImage = (req, res) => {
  try {
    const { id } = req.params;
    const {
      species_id,
      freshness_category_id,
      split,
      lighting_condition,
      background_condition,
      fish_orientation,
      distance_condition,
      image_quality,
      source
    } = req.body;

    const stmt = db.prepare(`
      UPDATE dataset_images SET
        species_id = COALESCE(?, species_id),
        freshness_category_id = COALESCE(?, freshness_category_id),
        split = COALESCE(?, split),
        lighting_condition = COALESCE(?, lighting_condition),
        background_condition = COALESCE(?, background_condition),
        fish_orientation = COALESCE(?, fish_orientation),
        distance_condition = COALESCE(?, distance_condition),
        image_quality = COALESCE(?, image_quality),
        source = COALESCE(?, source)
      WHERE id = ?
    `);

    stmt.run(
      species_id, freshness_category_id, split, lighting_condition,
      background_condition, fish_orientation, distance_condition, image_quality, source, id
    );

    res.json({ success: true, message: 'Dataset metadata updated successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error updating dataset item: ' + err.message });
  }
};
