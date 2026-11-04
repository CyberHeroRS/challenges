const { hashPassword } = require("../utils/passwords");

function createRoomRepository(db) {
  const insertRoom = db.prepare(`
    INSERT INTO rooms (slug, password_salt, password_hash, owner)
    VALUES (@slug, @password_salt, @password_hash, @owner)
  `);

  const getRoomBySlug = db.prepare(`
    SELECT slug, password_salt, password_hash, owner, created_at
    FROM rooms
    WHERE slug = ?
  `);

  const deleteRoomBySlug = db.prepare(`
    DELETE FROM rooms
    WHERE slug = ?
  `);

  return {
    createRoom({ slug, password, owner }) {
      const { salt, hash } = hashPassword(password);

      insertRoom.run({
        slug,
        password_salt: salt,
        password_hash: hash,
        owner,
      });

      return this.findBySlug(slug);
    },

    findBySlug(slug) {
      return getRoomBySlug.get(slug) || null;
    },

    deleteRoom(slug) {
      return deleteRoomBySlug.run(slug).changes > 0;
    },
  };
}

module.exports = {
  createRoomRepository,
};
