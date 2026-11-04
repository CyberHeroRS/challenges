const http = require("node:http");

const { loadConfig } = require("./src/config");
const { createDatabase } = require("./src/db");
const { createApp } = require("./src/http");
const { createRoomRepository } = require("./src/repositories/rooms");
const { startAdminBot } = require("./src/services/adminBot");
const { createRoomService } = require("./src/services/roomService");
const { createSocketServer } = require("./src/socket");

const config = loadConfig();
const db = createDatabase(config.dbPath);
const roomRepository = createRoomRepository(db);
const roomService = createRoomService({ roomRepository });

const app = createApp({ roomService });

const server = http.createServer(app);
createSocketServer({ server, roomService });

server.listen(config.port, () => {
  console.log(`server listening on 0.0.0.0:${config.port}`);

  startAdminBot({
    baseUrl: `http://127.0.0.1:${config.port}`,
    config,
    roomService,
  });
});
