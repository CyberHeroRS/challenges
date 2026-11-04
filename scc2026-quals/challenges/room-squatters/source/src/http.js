const path = require("node:path");

const express = require("express");

function createApp({ roomService }) {
  const app = express();

  app.use(express.json());
  app.use(express.static(path.join(__dirname, "..", "public")));

  app.post("/api/rooms", (req, res) => {
    const { room_slug: slug, password } = req.body || {};

    try {
      const room = roomService.createRoom({
        slug,
        password,
        owner: "user",
      });

      res.status(201).json({ ok: true, room });
    } catch (error) {
      const status = error.code === "ROOM_EXISTS" ? 409 : 400;
      res.status(status).json({ ok: false, error: error.message });
    }
  });

  app.delete("/api/rooms/:slug", (req, res) => {
    const deleted = roomService.deleteRoom(req.params.slug);
    if (!deleted) {
      res.status(404).json({ ok: false, error: "Room not found" });
      return;
    }

    res.json({ ok: true, deleted: req.params.slug });
  });

  app.use((req, res) => {
    res.status(404).json({ ok: false, error: "Route not found" });
  });

  return app;
}

module.exports = {
  createApp,
};
