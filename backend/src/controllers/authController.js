const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const db = require('../config/database');
const { JWT_SECRET } = require('../middleware/authMiddleware');

exports.register = (req, res) => {
  try {
    const { name, email, password, role = 'consumer' } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ success: false, message: 'Name, email, and password are required.' });
    }

    if (password.length < 6) {
      return res.status(400).json({ success: false, message: 'Password must be at least 6 characters long.' });
    }

    const existing = db.prepare('SELECT id FROM users WHERE email = ?').get(email.toLowerCase().trim());
    if (existing) {
      return res.status(409).json({ success: false, message: 'An account with this email address already exists.' });
    }

    // Self-registration always gets 'consumer' role.
    // Role elevation (to vendor, researcher, admin) requires an admin
    // to use the PUT /users/:id/role endpoint after account creation.
    const assignedRole = 'consumer';

    const salt = bcrypt.genSaltSync(10);
    const hashedPassword = bcrypt.hashSync(password, salt);

    const stmt = db.prepare('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)');
    const info = stmt.run(name.trim(), email.toLowerCase().trim(), hashedPassword, assignedRole);

    const token = jwt.sign(
      { id: info.lastInsertRowid, email: email.toLowerCase().trim(), role: assignedRole },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.status(201).json({
      success: true,
      message: 'Account registered successfully.',
      token,
      user: {
        id: info.lastInsertRowid,
        name: name.trim(),
        email: email.toLowerCase().trim(),
        role: assignedRole
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Registration failed: ' + err.message });
  }
};

exports.login = (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ success: false, message: 'Email and password are required.' });
    }

    const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email.toLowerCase().trim());
    if (!user) {
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });
    }

    const isMatch = bcrypt.compareSync(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });
    }

    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      success: true,
      message: 'Login successful.',
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Login error: ' + err.message });
  }
};

exports.getProfile = (req, res) => {
  if (!req.user) {
    return res.status(401).json({ success: false, message: 'Not authenticated.' });
  }
  res.json({ success: true, user: req.user });
};

exports.updateProfile = (req, res) => {
  try {
    const { name, password } = req.body;
    const userId = req.user.id;

    if (name) {
      db.prepare('UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(name.trim(), userId);
    }

    if (password && password.length >= 6) {
      const salt = bcrypt.genSaltSync(10);
      const hashedPassword = bcrypt.hashSync(password, salt);
      db.prepare('UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(hashedPassword, userId);
    }

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

exports.updateUserRole = (req, res) => {
  try {
    const { id } = req.params;
    const { role } = req.body;

    const validRoles = ['consumer', 'vendor', 'admin', 'researcher'];
    if (!validRoles.includes(role)) {
      return res.status(400).json({ success: false, message: 'Invalid role specified.' });
    }

    db.prepare('UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(role, id);
    res.json({ success: true, message: 'User role updated successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Error updating user role: ' + err.message });
  }
};
