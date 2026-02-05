const express = require('express');
const router = express.Router();
const { authenticateUser } = require('./middleware/auth');
const { register, login, logout } = require('./controllers');
const { getAgentInfo, getAllAgents } = require('./controllers');
const { spyOnUrl } = require('./controllers');

// Auth routes
router.post('/register', register);
router.post('/login', login);
router.post('/logout', logout);

// Agent routes
router.get('/account_info/:encodedId', authenticateUser, getAgentInfo);
router.get('/agents', authenticateUser, getAllAgents);

// Spy routes
router.post('/spy_on', authenticateUser, spyOnUrl);

module.exports = router; 