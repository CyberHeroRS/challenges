const { db } = require("./index");

const getAll = db.prepare("SELECT * FROM catalogue");
const findById = db.prepare("SELECT * FROM catalogue WHERE id = ?");

module.exports = { getAll, findById };
