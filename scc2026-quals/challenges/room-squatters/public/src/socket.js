const { Server } = require("socket.io");

const { verifyPassword } = require("./utils/passwords");

function createSocketServer({ server, roomService }) {
  const io = new Server(server, {
    cors: {
      origin: "*",
    },
  });

  io.on("connection", (socket) => {
    socket.on("room:join", (payload, ack = () => {}) => {
      const slug = payload?.room_slug;
      const password = payload?.password;
      const username =
        (payload?.username || "guest").trim().slice(0, 32) || "guest";

      const room = roomService.getRoom(slug);
      if (!room) {
        ack({ ok: false, error: "Room not found" });
        return;
      }

      if (
        !verifyPassword(password || "", room.password_salt, room.password_hash)
      ) {
        ack({ ok: false, error: "Bad password" });
        return;
      }

      if (socket.data.currentRoom && socket.data.currentRoom !== slug) {
        socket.leave(socket.data.currentRoom);
      }

      socket.join(slug);
      socket.data.currentRoom = slug;
      socket.data.username = username;

      ack({ ok: true, room: { slug } });
      io.to(slug).emit("room:event", {
        message: `${username} joined ${slug}`,
      });
    });

    socket.on("room:message", (payload, ack = () => {}) => {
      const slug = payload?.room_slug;
      const message = String(payload?.message || "").trim();

      if (!slug || !socket.rooms.has(slug)) {
        ack({ ok: false, error: "Join the room first" });
        return;
      }

      const room = roomService.getRoom(slug);
      if (!room) {
        ack({ ok: false, error: "Room not found" });
        return;
      }

      if (!message) {
        ack({ ok: false, error: "Message cannot be empty" });
        return;
      }

      io.to(slug).emit("room:message", {
        room_slug: slug,
        sender: socket.data.username || "guest",
        message: message.slice(0, 400),
        sent_at: new Date().toISOString(),
      });

      ack({ ok: true });
    });
  });

  return io;
}

module.exports = {
  createSocketServer,
};
