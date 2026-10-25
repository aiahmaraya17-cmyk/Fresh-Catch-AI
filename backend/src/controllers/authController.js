const db = require('../config/database');
const { getFirebaseAdmin } = require('../config/firebaseAdmin');

exports.getProfile = (req, res) => {
  if (!req.user) {
    return res.status(401).json({ success: false, message: 'Not authenticated.' });
  }
  res.json({ success: true, user: req.user });
};

exports.updateProfile = async (req, res) => {
  try {
    const { name } = req.body;
    const userId = req.user.id;
    if (!name || !name.trim()) return res.status(400).json({ success: false, message: 'Name is required.' });
    const cleanName = name.trim();
    await getFirebaseAdmin().firestore().collection('users').doc(req.firebaseUser.uid).set({ name: cleanName, updatedAt: new Date() }, { merge: true });
    db.prepare('UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(cleanName, userId);
    const updatedUser = db.prepare('SELECT id, name, email, role, created_at FROM users WHERE id = ?').get(userId);
    res.json({ success: true, message: 'Profile updated successfully.', user: updatedUser });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Update failed: ' + err.message });
  }
};

exports.listUsers = (req, res) => {
  try {
    const users = db.prepare('SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC').all();
    res.json({ success: true, users });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error retrieving users: ' + err.message });
  }
};

exports.updateUserRole = async (req, res) => {
  try {
    const { id } = req.params;
    const { role } = req.body;

    const validRoles = ['consumer', 'vendor', 'admin', 'researcher'];
    if (!validRoles.includes(role)) {
      return res.status(400).json({ success: false, message: 'Invalid role specified.' });
    }

    const user = db.prepare('SELECT firebase_uid FROM users WHERE id = ?').get(id);
    if (!user) return res.status(404).json({ success: false, message: 'User not found.' });
    if (!user.firebase_uid) return res.status(409).json({ success: false, message: 'This user has not signed in through Firebase yet.' });
    await getFirebaseAdmin().firestore().collection('users').doc(user.firebase_uid).set({ role, updatedAt: new Date() }, { merge: true });
    db.prepare('UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(role, id);
    res.json({ success: true, message: 'User role updated successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error updating user role: ' + err.message });
  }
};
