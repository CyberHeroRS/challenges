const pool = require('../config/database');

class Post {
    constructor(data) {
        this.id = data.id;
        this.user_id = data.user_id;
        this.content = data.content;
        this.embed = data.embed;
        this.likes = data.likes;
        this.created_at = data.created_at;
        this.username = data.username; // Join from users table
    }

    static async create(userId, content, embed = null) {
        const [result] = await pool.execute(
            'INSERT INTO posts (user_id, content, embed) VALUES (?, ?, ?)',
            [userId, content, embed]
        );
        return await this.findById(result.insertId);
    }

    static async findById(id) {
        const [posts] = await pool.execute(
            'SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id = ?',
            [id]
        );
        return posts[0] ? new Post(posts[0]) : null;
    }

    static async findByUserId(userId) {
        const [posts] = await pool.execute(
            'SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE user_id = ? ORDER BY created_at DESC',
            [userId]
        );
        return posts.map(post => new Post(post));
    }

    static async findByUsername(username) {
        const [posts] = await pool.execute(
            'SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE username = ? ORDER BY created_at DESC',
            [username]
        );
        return posts.map(post => new Post(post));
    }

    toJSON() {
        return {
            id: this.id,
            user_id: this.user_id,
            content: this.content,
            embed: this.embed,
            likes: this.likes,
            created_at: this.created_at,
            username: this.username
        };
    }

    static async delete(id) {
        const [result] = await pool.execute(
            'DELETE FROM posts WHERE id = ?',
            [id]
        );
        return result.affectedRows > 0;
    }
}

module.exports = Post; 