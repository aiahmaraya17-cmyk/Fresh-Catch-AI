const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const { requireAuth, requireRoles } = require('../middleware/authMiddleware');

router.get('/profile', requireAuth, authController.getProfile);
router.put('/profile', requireAuth, authController.updateProfile);

router.get('/users', requireAuth, requireRoles(['admin', 'researcher']), authController.listUsers);
router.put('/users/:id/role', requireAuth, requireRoles(['admin']), authController.updateUserRole);

module.exports = router;
