const path = require("node:path");

function intFromEnv(name, fallback) {
  const value = Number.parseInt(process.env[name] || "", 10);
  return Number.isFinite(value) ? value : fallback;
}

function loadConfig() {
  return {
    port: intFromEnv("PORT", 3000),
    dbPath:
      process.env.DB_PATH || path.join(__dirname, "..", "data", "rooms.sqlite"),
    flag: process.env.FLAG || "SCC{this_is_a_fake_flag}",
    adminBotIntervalMs: 60_000,
    adminRoomTtlMs: 5_000,
  };
}

module.exports = {
  loadConfig,
};
