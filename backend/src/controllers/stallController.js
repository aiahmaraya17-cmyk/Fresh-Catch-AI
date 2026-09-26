const db = require('../config/database');

/**
 * Freshness reputation helper.
 * Given a stall id, aggregates its stall-tagged predictions into a
 * consumer-facing trust score.
 *
 * Buckets (classification strings produced by the AI engine):
 *   "Fresh", "Moderately Fresh"  -> counted as "good" (safe to buy)
 *   "Less Fresh", "Not Fresh"    -> counted as "poor"
 *
 * freshness_rate = good_scans / total_scans (0..1)
 * Also returns per-class counts, total scans, and the last scan timestamp.
 */
function computeStallStats(stallId) {
  const rows = db.prepare(`
    SELECT classification, COUNT(*) AS n
    FROM predictions
    WHERE stall_id = ?
    GROUP BY classification
  `).all(stallId);

  const counts = { 'Fresh': 0, 'Moderately Fresh': 0, 'Less Fresh': 0, 'Not Fresh': 0 };
  let total = 0;
  for (const r of rows) {
    if (counts[r.classification] === undefined) counts[r.classification] = 0;
    counts[r.classification] += r.n;
    total += r.n;
  }

  const good = counts['Fresh'] + counts['Moderately Fresh'];
  const freshnessRate = total > 0 ? good / total : null;

  // Scans in the last 24 hours (today's freshness activity)
  const todayRow = db.prepare(`
    SELECT COUNT(*) AS n
    FROM predictions
    WHERE stall_id = ? AND created_at >= datetime('now', '-1 day')
  `).get(stallId);

  const lastRow = db.prepare(`
    SELECT created_at FROM predictions
    WHERE stall_id = ?
    ORDER BY created_at DESC LIMIT 1
  `).get(stallId);

  return {
    total_scans: total,
    scans_today: todayRow ? todayRow.n : 0,
    class_counts: counts,
    freshness_rate: freshnessRate === null ? null : Math.round(freshnessRate * 1000) / 1000,
    freshness_percentage: freshnessRate === null ? null : Math.round(freshnessRate * 100),
    last_scan_at: lastRow ? lastRow.created_at : null,
  };
}

/**
 * GET /api/stalls  (public)
 * Directory of active stalls, each with its freshness reputation stats.
 */
exports.listStalls = (req, res) => {
  try {
    const stalls = db.prepare(`
      SELECT s.*, u.name AS owner_name
      FROM stalls s
      LEFT JOIN users u ON s.owner_id = u.id
      WHERE s.is_active = 1
      ORDER BY s.name ASC
    `).all();

    const withStats = stalls.map(s => ({
      ...s,
      stats: computeStallStats(s.id),
    }));

    // Order by most scan activity first so lively stalls surface to the top.
    withStats.sort((a, b) => (b.stats.total_scans || 0) - (a.stats.total_scans || 0));

    res.json({ success: true, stalls: withStats, total: withStats.length });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load stalls: ' + err.message });
  }
};

/**
 * GET /api/stalls/:id  (public)
 * A single stall profile + its recent stall-tagged freshness scans.
 */
exports.getStall = (req, res) => {
  try {
    const { id } = req.params;
    const stall = db.prepare(`
      SELECT s.*, u.name AS owner_name
      FROM stalls s
      LEFT JOIN users u ON s.owner_id = u.id
      WHERE s.id = ?
    `).get(id);

    if (!stall) {
      return res.status(404).json({ success: false, message: 'Stall not found.' });
    }

    const recentScans = db.prepare(`
      SELECT p.id, p.image_url, p.classification, p.confidence, p.created_at,
             sp.local_name AS species_local_name, sp.name AS species_name
      FROM predictions p
      LEFT JOIN fish_species sp ON p.species_id = sp.id
      WHERE p.stall_id = ?
      ORDER BY p.created_at DESC
      LIMIT 12
    `).all(id);

    res.json({
      success: true,
      stall: { ...stall, stats: computeStallStats(stall.id) },
      recentScans,
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load stall: ' + err.message });
  }
};

/**
 * GET /api/stalls/me/mine  (vendor)
 * Returns the stall owned by the current vendor (or null if none yet).
 */
exports.getMyStall = (req, res) => {
  try {
    const stall = db.prepare('SELECT * FROM stalls WHERE owner_id = ?').get(req.user.id);
    if (!stall) {
      return res.json({ success: true, stall: null });
    }
    res.json({ success: true, stall: { ...stall, stats: computeStallStats(stall.id) } });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load your stall: ' + err.message });
  }
};

/**
 * POST /api/stalls  (vendor/admin)
 * Creates the current vendor's stall. One stall per owner (enforced by UNIQUE).
 */
exports.createStall = (req, res) => {
  try {
    const { name, market_name, section, description, contact_number } = req.body;
    if (!name || !name.trim()) {
      return res.status(400).json({ success: false, message: 'Stall name is required.' });
    }

    const existing = db.prepare('SELECT id FROM stalls WHERE owner_id = ?').get(req.user.id);
    if (existing) {
      return res.status(409).json({ success: false, message: 'You already have a stall. Update it instead.' });
    }

    const info = db.prepare(`
      INSERT INTO stalls (owner_id, name, market_name, section, description, contact_number)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(
      req.user.id,
      name.trim(),
      (market_name || 'Roxas Public Market').trim(),
      section ? section.trim() : null,
      description ? description.trim() : null,
      contact_number ? contact_number.trim() : null
    );

    const stall = db.prepare('SELECT * FROM stalls WHERE id = ?').get(info.lastInsertRowid);
    res.status(201).json({ success: true, message: 'Stall created.', stall });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to create stall: ' + err.message });
  }
};

/**
 * PUT /api/stalls/:id  (owner or admin)
 * Updates stall details. A vendor may only edit their own stall.
 */
exports.updateStall = (req, res) => {
  try {
    const { id } = req.params;
    const stall = db.prepare('SELECT * FROM stalls WHERE id = ?').get(id);
    if (!stall) {
      return res.status(404).json({ success: false, message: 'Stall not found.' });
    }

    const isOwner = stall.owner_id === req.user.id;
    const isAdmin = req.user.role === 'admin';
    if (!isOwner && !isAdmin) {
      return res.status(403).json({ success: false, message: 'You can only edit your own stall.' });
    }

    const { name, market_name, section, description, contact_number, is_active } = req.body;

    db.prepare(`
      UPDATE stalls SET
        name           = COALESCE(?, name),
        market_name    = COALESCE(?, market_name),
        section        = COALESCE(?, section),
        description    = COALESCE(?, description),
        contact_number = COALESCE(?, contact_number),
        is_active      = COALESCE(?, is_active),
        updated_at     = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(
      name != null ? name.trim() : null,
      market_name != null ? market_name.trim() : null,
      section != null ? section.trim() : null,
      description != null ? description.trim() : null,
      contact_number != null ? contact_number.trim() : null,
      is_active != null ? (is_active ? 1 : 0) : null,
      id
    );

    const updated = db.prepare('SELECT * FROM stalls WHERE id = ?').get(id);
    res.json({ success: true, message: 'Stall updated.', stall: { ...updated, stats: computeStallStats(id) } });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to update stall: ' + err.message });
  }
};

module.exports = {
  listStalls: exports.listStalls,
  getStall: exports.getStall,
  getMyStall: exports.getMyStall,
  createStall: exports.createStall,
  updateStall: exports.updateStall,
  computeStallStats,
};
