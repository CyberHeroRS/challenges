const express = require("express");
const fs = require("fs");
const app = express();

try {
  fs.mkdirSync("/tmp/sessions", { recursive: true });
} catch {}

function getBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";

    if (req.headers["content-type"] !== "text/plain") {
      reject("Invalid content type");
    }

    req.setEncoding("utf8");
    req.on("data", (chunk) => {
      data += chunk;
    });
    req.on("end", () => {
      resolve(data);
    });
    req.on("error", (err) => {
      reject(err);
    });
  });
}

function createSessionId() {
  return Array.from({ length: 64 }, () =>
    Math.floor(Math.random() * 36).toString(36)
  ).join("");
}

function validateSessionId(id) {
  return /^[a-zA-Z0-9]{64}$/.test(id);
}

function getSession(id) {
  return new Promise((resolve, reject) => {
    fs.readFile(`/tmp/sessions/${id}`, (err, data) => {
      if (err) {
        reject(err);
      } else {
        resolve(JSON.parse(data));
      }
    });
  });
}

function setSession(id, session) {
  return new Promise((resolve, reject) => {
    fs.writeFile(`/tmp/sessions/${id}`, JSON.stringify(session), (err) => {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    });
  });
}

function getRandomPill() {
  const pills = ["red", "blue"];
  return pills[Math.floor(Math.random() * pills.length)];
}

function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/index.html");
});

app.use(
  asyncHandler(async (req, res, next) => {
    const sessionId = req.headers["x-session-id"];

    if (sessionId) {
      if (validateSessionId(sessionId)) {
        try {
          req.session = await getSession(sessionId);
        } catch {}
      }
    }

    if (!req.session) {
      req.session = {
        id: createSessionId(),
      };
    }

    res.setHeader("x-session-id", req.session.id);
    next();
  })
);

app.post(
  "/start",
  asyncHandler(async (req, res) => {
    req.session.count = 0;
    req.session.current = getRandomPill();
    await setSession(req.session.id, req.session);
    res.send("Success");
  })
);

app.post(
  "/guess",
  asyncHandler(async (req, res) => {
    const body = await getBody(req);
    const guess = body.trim().toLowerCase();

    if (guess === req.session.current) {
      req.session.count++;
      req.session.current = getRandomPill();
      await setSession(req.session.id, req.session);
      res.send("Correct");
    } else {
      req.session.count = 0;
      req.session.current = getRandomPill();
      await setSession(req.session.id, req.session);
      res.send("Incorrect");
    }
  })
);

app.get("/status", (req, res) => {
  if (req.session.count >= 100) {
    res.send(process.env.FLAG);
  } else {
    res.send(`You need ${100 - req.session.count} more correct guesses`);
  }
});

app.use((error, req, res, next) => {
  res.status(500).send("An error occurred");
  console.log(error);
});

app.listen(3000, () => {
  console.log("Server listening on :3000");
});

process.on("unhandledRejection", (error) => {
  console.error("Unhandled promise rejection:", error);
});

process.on("uncaughtException", (error) => {
  console.error("Uncaught exception:", error);
});
