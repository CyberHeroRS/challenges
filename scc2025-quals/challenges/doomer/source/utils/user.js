const pool = require('../config/database');
const bcrypt = require('bcrypt');

class User {
    constructor(data) {
        this.id = data.id;
        this.username = data.username;
        this.email = data.email;
        this.password = data.password;
        this.created_at = data.created_at;
    }

    static async findByUsername(username) {
        const [users] = await pool.execute('SELECT * FROM users WHERE username = ?', [username]);
        return users[0] ? new User(users[0]) : null;
    }

    static async findByEmail(email) {
        const [users] = await pool.execute('SELECT * FROM users WHERE email = ?', [email]);
        return users[0] ? new User(users[0]) : null;
    }

    static async findById(id) {
        const [users] = await pool.execute('SELECT * FROM users WHERE id = ?', [id]);
        return users[0] ? new User(users[0]) : null;
    }

    static async create(userData) {
        const { username, email, password } = userData;
        const hashedPassword = await bcrypt.hash(password, 10);
        
        const [result] = await pool.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            [username, email, hashedPassword]
        );
        
        return await this.findById(result.insertId);
    }

    static async checkExisting(username, email) {
        const [users] = await pool.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            [username, email]
        );
        return users.length > 0;
    }

    toJSON() {
        return {
            id: this.id,
            username: this.username,
            email: this.email,
            created_at: this.created_at
        };
    }
}

module.exports = User; 