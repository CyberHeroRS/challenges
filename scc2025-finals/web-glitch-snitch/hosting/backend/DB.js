const sqlite3 = require("sqlite3").verbose();
const bcrypt = require("bcrypt");

class DB {
  constructor(dbFilePath = ":memory:") {
    this.db = new sqlite3.Database(dbFilePath, (err) => {
      if (err) {
        console.error("Could not connect to database", err);
      } else {
        console.log("Connected to database");
      }
    });
    this.createUserTable();
  }

  createUserTable() {
    const sql = `
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                username TEXT,
                password TEXT
            )`;
    this.db.run(sql, (err) => {
      if (err) {
        console.error("Could not create table", err);
      }
    });
  }

  createUser(email, username, password, callback) {
    const saltRounds = 10;
    bcrypt.hash(password, saltRounds, (err, hash) => {
      if (err) {
        return callback(err);
      }
      const sql = `INSERT INTO users (email, username, password) VALUES (?, ?, ?)`;
      this.db.run(sql, [email, username, hash], function (err) {
        if (err) {
          return callback(err);
        }
        callback(null, { id: this.lastID });
      });
    });
  }

  checkPassword(email, password, callback) {
    const sql = `SELECT id, username, password FROM users WHERE email = ?`;
    this.db.get(sql, [email], (err, row) => {
      if (err) {
        return callback(err);
      }
      if (!row) {
        return callback(null, false);
      }
      bcrypt.compare(password, row.password, (err, result) => {
        if (err) {
          return callback(err);
        }
        if (!result) {
          return callback(null, false);
        }
        callback(null, { id: row.id, username: row.username });
      });
    });
  }
}

module.exports = DB;
