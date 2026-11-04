const Database = require("better-sqlite3");
const crypto = require("crypto");
const { v4: uuidv4 } = require("uuid");
const { FLAG } = require("../config");

const db = new Database(":memory:");
db.pragma("journal_mode = WAL");

db.exec(`
  CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    biography TEXT DEFAULT '',
    sesame_password TEXT DEFAULT ''
  );
  CREATE TABLE catalogue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    image TEXT NOT NULL,
    rarity TEXT NOT NULL,
    value TEXT NOT NULL
  );
  CREATE TABLE wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES catalogue(id)
  );
`);

const CATALOGUE = [
  { name: "Ancient Gold Coins", description: "A pile of glittering gold coins from the Ottoman Empire", image: "gold-coins", rarity: "Legendary", value: "10,000 dinars" },
  { name: "Silver Chalice", description: "An ornate silver drinking cup encrusted with rubies", image: "silver-chalice", rarity: "Epic", value: "5,000 dinars" },
  { name: "Emerald Necklace", description: "A stunning necklace with emeralds the size of walnuts", image: "emerald-necklace", rarity: "Legendary", value: "8,500 dinars" },
  { name: "Ruby Ring", description: "A golden ring with a blood-red ruby at its center", image: "ruby-ring", rarity: "Rare", value: "3,200 dinars" },
  { name: "Diamond Dagger", description: "A ceremonial dagger with a diamond-studded hilt", image: "diamond-dagger", rarity: "Epic", value: "6,000 dinars" },
  { name: "Sapphire Tiara", description: "A delicate tiara set with brilliant blue sapphires", image: "sapphire-tiara", rarity: "Legendary", value: "9,000 dinars" },
  { name: "Bronze Idol", description: "A small bronze statue of a forgotten cave deity", image: "bronze-idol", rarity: "Common", value: "800 dinars" },
  { name: "Pearl Strand", description: "A long strand of perfectly matched black pearls", image: "pearl-strand", rarity: "Rare", value: "4,000 dinars" },
  { name: "Golden Lamp", description: "A mysterious oil lamp said to house a powerful djinn", image: "golden-lamp", rarity: "Legendary", value: "15,000 dinars" },
];

const insertItem = db.prepare("INSERT INTO catalogue (name, description, image, rarity, value) VALUES (?, ?, ?, ?, ?)");
for (const item of CATALOGUE) {
  insertItem.run(item.name, item.description, item.image, item.rarity, item.value);
}

const captainId = uuidv4();
db.prepare("INSERT INTO users (id, username, password, biography, sesame_password) VALUES (?, ?, ?, ?, ?)").run(
  captainId,
  "captain",
  crypto.randomBytes(32).toString("hex"),
  "I am the captain of the forty thieves. My treasures are beyond your imagination.",
  FLAG
);

module.exports = { db, captainId };
