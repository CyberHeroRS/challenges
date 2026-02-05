const pool = require('../db');

const authenticateUser = async (req, res, next) => {
    try {
        const secretCode = req.cookies.session;
        if (!secretCode) {
            return res.status(401).json({ error: 'Authentication required' });
        }

        const [rows] = await pool.execute(
            'SELECT * FROM users WHERE secret_code = ?',
            [secretCode]
        );

        if (rows.length === 0) {
            return res.status(401).json({ error: 'Invalid authentication' });
        }

        req.user = rows[0];
        next();
    } catch (error) {
        console.error('Authentication error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
};

module.exports = {
    authenticateUser
}; 