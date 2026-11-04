const { db } = require("./index");

const findByCredentials = db.prepare(
  "SELECT * FROM users WHERE username = ? AND password = ?"
);

const findById = db.prepare("SELECT * FROM users WHERE id = ?");

const findByUsername = db.prepare(
  "SELECT username, biography FROM users WHERE username = ?"
);

const create = db.prepare(
  "INSERT INTO users (id, username, password, biography, sesame_password) VALUES (?, ?, ?, ?, ?)"
);

const updateProfile = db.prepare(
  "UPDATE users SET biography = ?, sesame_password = ? WHERE id = ?"
);

module.exports = { findByCredentials, findById, findByUsername, create, updateProfile };
