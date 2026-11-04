const { randomBytes } = require("node:crypto");

const { io: createClient } = require("socket.io-client");

function connectSocket(baseUrl) {
  return new Promise((resolve, reject) => {
    const socket = createClient(baseUrl, {
      forceNew: true,
      reconnection: false,
      timeout: 5000,
      transports: ["websocket"],
    });

    const fail = (error) => {
      socket.close();
      reject(error);
    };

    socket.once("connect", () => resolve(socket));
    socket.once("connect_error", fail);
  });
}

function emitWithAck(socket, event, payload) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`${event} timed out`));
    }, 5000);

    socket.emit(event, payload, (response) => {
      clearTimeout(timer);

      if (!response || response.ok === false) {
        reject(new Error(response?.error || `${event} failed`));
        return;
      }

      resolve(response);
    });
  });
}

function generateSlug() {
  return `my-secret-room-${Math.floor(Date.now() / 60000)}`;
}

async function runCycle({ baseUrl, config, roomService }) {
  const slug = generateSlug();

  const existingRoom = roomService.getRoom(slug);
  if (existingRoom) {
    console.warn(
      `[admin-bot] room ${slug} already exists, skipping this cycle`,
    );
    return;
  }

  const password = randomBytes(24).toString("hex");
  roomService.createRoom({
    slug,
    password,
    owner: "admin-bot",
  });

  let socket;

  try {
    socket = await connectSocket(baseUrl);

    await emitWithAck(socket, "room:join", {
      room_slug: slug,
      password,
      username: "admin-bot",
    });

    await emitWithAck(socket, "room:message", {
      room_slug: slug,
      message: `I sure hope no-one steals my flag: ${config.flag}`,
    });

    console.log(`[admin-bot] delivered payload into ${slug}`);
  } catch (error) {
    console.error(`[admin-bot] ${error.message}`);
  } finally {
    if (socket) {
      socket.disconnect();
    }
  }

  const cleanupTimer = setTimeout(() => {
    const room = roomService.getRoom(slug);
    if (room) {
      roomService.deleteRoom(slug);
    }
  }, config.adminRoomTtlMs);

  cleanupTimer.unref?.();
}

function startAdminBot({ baseUrl, config, roomService }) {
  const interval = setInterval(() => {
    runCycle({ baseUrl, config, roomService }).catch((error) => {
      console.error(`[admin-bot] ${error.message}`);
    });
  }, config.adminBotIntervalMs);

  interval.unref?.();
}

module.exports = {
  startAdminBot,
};
