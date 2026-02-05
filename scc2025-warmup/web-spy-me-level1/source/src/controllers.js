const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const fetch = require('node-fetch');
const pool = require('./db');
const fs = require('fs').promises;
const path = require('path');
const { 
    processWhitelistData, 
    encodeJsonToBase64, 
    decodeBase64ToJson,
    validateUrl,
    sanitizeFilename
} = require('./utils');

const register = async (req, res) => {
    const { username, firstName, lastName } = req.body;

    try {
        const [idRow] = await pool.execute('SELECT next_id FROM id_sequence');
        const id = idRow[0].next_id;

        await pool.execute('UPDATE id_sequence SET next_id = next_id + 1');

        const secretCode = uuidv4();

        await pool.execute(
            'INSERT INTO users (id, username, first_name, last_name, secret_code) VALUES (?, ?, ?, ?, ?)',
            [id, username, firstName, lastName, secretCode]
        );

        res.json({ 
            success: true, 
            message: 'Registration successful. Save your secret code - it will only be shown once!',
            secretCode 
        });
    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
};

const login = async (req, res) => {
    try {
        const { username, secretCode } = req.body;
        
        if (!username || !secretCode) {
            return res.status(400).json({ error: 'Username and secret code are required' });
        }

        const [rows] = await pool.execute(
            'SELECT * FROM users WHERE username = ? AND secret_code = ?',
            [username, secretCode]
        );

        if (rows.length === 0) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const user = rows[0];

        res.cookie('session', user.secret_code, {
            httpOnly: true,
            path: '/',
            sameSite: 'lax'
        });

        if (user.username === 'admin') {
            return res.json({ 
                success: true,
                id: user.id,
                flag: process.env.FLAG2 || 'FAKE{this_is_flag2}'
            });
        }

        try {
            const whitelistPath = path.join(__dirname, 'whitelist', `spy_${username}.json`);
            const content = await fs.readFile(whitelistPath, 'utf8');
            const spyData = JSON.parse(content);
            
            if (spyData.is_allowed_spy) {
                return res.json({ 
                    success: true,
                    id: user.id,
                    flag: process.env.FLAG1 || 'FAKE{this_is_flag1}'
                });
            }
        } catch (err) {}

        res.json({ 
            success: true,
            id: user.id
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
};

const logout = (req, res) => {
    res.clearCookie('session');
    res.json({ success: true });
};

const getAgentInfo = async (req, res) => {
    try {
        const decodedData = decodeBase64ToJson(req.params.id);
        const userId = parseInt(decodedData.id);
        
        if (isNaN(userId)) {
            return res.status(400).json({ error: 'Invalid user ID' });
        }

        const [rows] = await pool.execute(
            'SELECT id, first_name, last_name, username, secret_code, is_admin FROM users WHERE id = ?',
            [userId]
        );

        if (rows.length === 0) {
            return res.status(404).json({ error: 'User not found' });
        }

        const user = rows[0];
        
        if (user.username == "admin" && !req.user.is_admin) {
            delete user.secret_code;
        }

        res.json(user);
    } catch (error) {
        console.error('Account info error:', error);
        res.status(500).json({ error: 'Failed to fetch account info' });
    }
};

const getAllAgents = async (req, res) => {
    try {
        const [rows] = await pool.execute(
            'SELECT id, username, first_name, last_name, codename, specialization, status, notes FROM users WHERE codename IS NOT NULL ORDER BY id ASC'
        );
        res.json(rows);
    } catch (error) {
        console.error('Failed to fetch agents:', error);
        res.status(500).json({ error: 'Failed to fetch agents' });
    }
};

// Spy controllers
const spyOnUrl = async (req, res) => {
    try {
        const whitelistDir = path.join(__dirname, 'whitelist');
        const files = await fs.readdir(whitelistDir);
        
        let isAllowed = false;
        for (const file of files) {
            const content = await fs.readFile(path.join(whitelistDir, file), 'utf8');
            const spyData = JSON.parse(content);
            if (spyData.username === req.user.username && spyData.is_allowed_spy) {
                isAllowed = true;
                break;
            }
        }

        if (!isAllowed) {
            return res.status(403).json({ error: 'You are not authorized to use this feature' });
        }

        const { url } = req.body;

        try {
            validateUrl(url);
        } catch (error) {
            return res.status(400).json({ error: error.message });
        }

        try {
            const botResponse = await fetch('http://admin-bot:3001/visit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            if (!botResponse.ok) {
                throw new Error(`Bot service responded with status ${botResponse.status}`);
            }

            res.json({ message: 'Admin bot is investigating the URL' });
        } catch (error) {
            console.error('Bot service error:', error);
            res.status(500).json({ error: 'Failed to contact admin bot service' });
        }
    } catch (error) {
        console.error('Spy feature error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
};

const readWhitelist = async (req, res) => {
    if (!req.user.is_admin) {
        return res.status(403).json({ error: 'Only administrators can read whitelist files' });
    }

    try {
        const filename = Buffer.from(req.params.filename, 'base64').toString();
        const sanitizedFilename = sanitizeFilename(filename);
        const whitelistPath = path.join(__dirname, 'whitelist', sanitizedFilename);
        const content = await fs.readFile(whitelistPath, 'utf8');
        
        try {
            const data = processWhitelistData(JSON.parse(content));
            
            if (req.query.checkStatus === 'true') {
                return res.json({ is_allowed_spy: data.is_allowed_spy });
            }
            
            if (!req.user.developer_mode) {
                return res.status(403).json({ error: 'Viewing whitelists is only available in developer mode' });
            }

            return res.json(data);
        } catch (error) {
            console.error('Error parsing whitelist JSON:', error);
            
            if (req.user.developer_mode) {
                return res.status(400).json({ error: 'Invalid whitelist file format', content });
            }
            return res.status(400).json({ error: 'Invalid whitelist file format' });
        }
    } catch (error) {
        console.error('Error reading whitelist:', error);
        if (req.query.checkStatus === 'true') {
            return res.json({ is_allowed_spy: false });
        }
        res.status(500).json({ error: 'Failed to read whitelist file' });
    }
};

const toggleSpyAccess = async (req, res) => {
    if (!req.user.is_admin) {
        return res.status(403).json({ error: 'Only administrators can modify whitelist' });
    }

    try {
        const { username, isAllowedSpy, ...otherInfo } = req.body;
        
        if (typeof username !== 'string') {
            return res.status(400).json({ error: 'Invalid username' });
        }

        const filename = `spy_${username}.json`;
        const whitelistPath = path.join(__dirname, 'whitelist', filename);

        try {
            const content = await fs.readFile(whitelistPath, 'utf8');
            const data = JSON.parse(content);
            
            const newData = { ...data, ...otherInfo, is_allowed_spy: isAllowedSpy };
            await fs.writeFile(whitelistPath, JSON.stringify(newData, null, 4));
            res.json({ success: true, data: newData });
        } catch (err) {
            if (err.code !== 'ENOENT') {
                throw err;
            }

            const [rows] = await pool.execute(
                'SELECT * FROM users WHERE username = ?',
                [username]
            );

            if (rows.length === 0) {
                return res.status(404).json({ error: 'User not found' });
            }

            const user = rows[0];
            const newData = {
                username: user.username,
                first_name: user.first_name,
                last_name: user.last_name,
                codename: user.codename,
                specialization: user.specialization,
                status: user.status,
                notes: user.notes,
                is_allowed_spy: isAllowedSpy ?? false,
                ...otherInfo  
            };

            await fs.writeFile(whitelistPath, JSON.stringify(newData, null, 4));
            res.json({ success: true, data: newData });
        }
    } catch (error) {
        console.error('Error modifying whitelist:', error);
        res.status(500).json({ error: 'Failed to modify whitelist' });
    }
};

module.exports = {
    register,
    login,
    logout,
    getAgentInfo,
    getAllAgents,
    spyOnUrl,
    readWhitelist,
    toggleSpyAccess
}; 