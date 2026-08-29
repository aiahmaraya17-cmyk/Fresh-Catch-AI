const db = require('../config/database');

exports.getSpecies = (req, res) => {
  try {
    const species = db.prepare('SELECT * FROM fish_species ORDER BY name ASC').all();
    res.json({ success: true, species });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to retrieve species: ' + err.message });
  }
};

exports.createSpecies = (req, res) => {
  try {
    const { name, local_name, scientific_name, description } = req.body;
    if (!name || !local_name) {
      return res.status(400).json({ success: false, message: 'Species name and local name are required.' });
    }

    const stmt = db.prepare('INSERT INTO fish_species (name, local_name, scientific_name, description) VALUES (?, ?, ?, ?)');
    const info = stmt.run(name, local_name, scientific_name || '', description || '');

    res.status(201).json({
      success: true,
      message: 'Fish species added successfully.',
      speciesId: info.lastInsertRowid
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error creating species: ' + err.message });
  }
};

exports.updateSpecies = (req, res) => {
  try {
    const { id } = req.params;
    const { name, local_name, scientific_name, description } = req.body;

    const stmt = db.prepare(`
      UPDATE fish_species SET
        name = COALESCE(?, name),
        local_name = COALESCE(?, local_name),
        scientific_name = COALESCE(?, scientific_name),
        description = COALESCE(?, description)
      WHERE id = ?
    `);

    stmt.run(name, local_name, scientific_name, description, id);
    res.json({ success: true, message: 'Species updated successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error updating species: ' + err.message });
  }
};
