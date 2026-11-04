const { db } = require("./index");

const getByUser = db.prepare(`
  SELECT c.name as item_name, c.rarity, c.value, w.added_at
  FROM wishlist w JOIN catalogue c ON w.item_id = c.id
  WHERE w.user_id = ?
  ORDER BY w.added_at DESC
`);

const exists = db.prepare(
  "SELECT * FROM wishlist WHERE user_id = ? AND item_id = ?"
);

const add = db.prepare(
  "INSERT INTO wishlist (user_id, item_id) VALUES (?, ?)"
);

module.exports = { getByUser, exists, add };
