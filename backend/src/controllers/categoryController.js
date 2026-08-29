const db = require('../config/database');

exports.getCategories = (req, res) => {
  try {
    const categories = db.prepare('SELECT * FROM freshness_categories ORDER BY id ASC').all();
    const formatted = categories.map(c => ({
      ...c,
      visual_characteristics: JSON.parse(c.visual_characteristics || '[]')
    }));
    res.json({ success: true, categories: formatted });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to retrieve categories: ' + err.message });
  }
};

exports.updateCategory = (req, res) => {
  try {
    const { id } = req.params;
    const { name, tagalog_name, description, visual_characteristics, recommendation, recommendation_tagalog } = req.body;

    const stmt = db.prepare(`
      UPDATE freshness_categories SET
        name = COALESCE(?, name),
        tagalog_name = COALESCE(?, tagalog_name),
        description = COALESCE(?, description),
        visual_characteristics = COALESCE(?, visual_characteristics),
        recommendation = COALESCE(?, recommendation),
        recommendation_tagalog = COALESCE(?, recommendation_tagalog)
      WHERE id = ?
    `);

    stmt.run(
      name,
      tagalog_name,
      description,
      visual_characteristics ? JSON.stringify(visual_characteristics) : null,
      recommendation,
      recommendation_tagalog,
      id
    );

    res.json({ success: true, message: 'Category updated successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error updating category: ' + err.message });
  }
};
