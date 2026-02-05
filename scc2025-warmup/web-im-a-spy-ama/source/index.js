const Database = require("better-sqlite3");
const express = require("express");
const fs = require("fs");

const db = new Database(":memory:");

db.prepare(
  `
  CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT
  );
`
).run();

db.prepare(
  `
  INSERT INTO questions (question) VALUES (?);
`
).run(process.env.FLAG);

const app = express();

app.use(express.urlencoded({ extended: false }));

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/index.html");
});

app.post("/", (req, res) => {
  const template = fs.readFileSync(__dirname + "/answer.html", "utf8");
  const answers = [
    "That's classified.",
    "I'm sorry, I can't disclose that information.",
    "The details are strictly confidential.",
    "I'd have to kill you if I told you that.",
    "My sources don't permit me to reveal that.",
    "Let's just say, it's better left unknown.",
    "Even if I knew, I wouldn't tell.",
    "I'm not at liberty to say.",
    "That information is on a need-to-know basis.",
    "Maybe if you asked nicely, but not today.",
  ];
  const answer = answers[Math.floor(Math.random() * answers.length)];

  const question = req.body.question || "";

  db.exec(`INSERT INTO questions (question) VALUES ('${question}')`);

  res.send(template.replace("{answer}", answer));
});

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
