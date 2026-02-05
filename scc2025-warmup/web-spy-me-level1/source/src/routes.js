const express = require('express');
const router = express.Router();
const { authenticateUser } = require('./middleware/auth');
const { register, login, logout } = require('./controllers');
const { getAgentInfo, getAllAgents } = require('./controllers');
const { spyOnUrl, readWhitelist, toggleSpyAccess } = require('./controllers');

// Auth routes
router.post('/register', register);
router.post('/login', login);
router.post('/logout', authenticateUser, logout);

// Agent routes
router.get('/account_info/:id', authenticateUser, getAgentInfo);
router.get('/agents', authenticateUser, getAllAgents);

// Spy routes
router.post('/spy_on', authenticateUser, spyOnUrl);

// Whitelist management routes (admin only)
router.get('/read_whitelist/:filename', authenticateUser, readWhitelist);
router.post('/toggle_spy_access', authenticateUser, toggleSpyAccess);

module.exports = router; 