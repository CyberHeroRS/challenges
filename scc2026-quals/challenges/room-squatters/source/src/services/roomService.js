const ROOM_SLUG_RE = /^[a-z0-9-]{3,40}$/;

function roomView(room) {
  return {
    slug: room.slug,
    owner: room.owner,
    created_at: room.created_at,
  };
}

function createError(message, code) {
  const error = new Error(message);
  error.code = code;
  return error;
}

function createRoomService({ roomRepository }) {
  return {
    getRoom(slug) {
      return roomRepository.findBySlug(slug);
    },

    createRoom({ slug, password, owner }) {
      if (!ROOM_SLUG_RE.test(slug || "")) {
        throw createError("room_slug must match [a-z0-9-]{3,40}", "BAD_INPUT");
      }

      if (typeof password !== "string" || password.length < 6) {
        throw createError(
          "password must be at least 6 characters",
          "BAD_INPUT",
        );
      }

      if (roomRepository.findBySlug(slug)) {
        throw createError("room already exists", "ROOM_EXISTS");
      }

      return roomView(roomRepository.createRoom({ slug, password, owner }));
    },

    deleteRoom(slug) {
      return roomRepository.deleteRoom(slug);
    },
  };
}

module.exports = {
  createRoomService,
};
