const express = require("express");
const fileUpload = require("express-fileupload");
const path = require("path");
const fs = require("fs");
const session = require("express-session");
const crypto = require("crypto");

const LIMIT_FILESIZE_MB = process.env.LIMIT_FILESIZE_MB || 10;

const DB = require("./DB");
const {
  mustNotBeAuthenticated,
  mustBeAuthenticated,
  uniqueFilename,
} = require("./helpers");

const PORT = process.env.PORT || 5000;
const db = new DB(":memory:");

// Express setup
const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(fileUpload());

// Session middleware
app.use(
  session({
    secret: crypto.randomBytes(64).toString("hex"),
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false }, // Set to true if using HTTPS
  }),
);

const UPLOAD_FOLDER =
  process.env.UPLOAD_FOLDER || path.join(__dirname, "upload");

// Ensure upload folder exists
if (!fs.existsSync(UPLOAD_FOLDER)) {
  fs.mkdirSync(UPLOAD_FOLDER, { recursive: true });
}

// Logout route
app.get("/logout", mustBeAuthenticated, (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).send("Error logging out");
    }
    res.json({ success: true, message: "Logged out" });
  });
});

app.post("/register", mustNotBeAuthenticated, (req, res) => {
  const { email, username, password } = req.body;

  if (!email || !username || !password) {
    return res.status(400).json({ success: false, message: "Missing fields" });
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/m.test(email)) {
    return res.status(400).json({
      success: false,
      message: "Invalid email",
    });
  }

  if (!/^[a-z0-9]+$/m.test(username)) {
    return res.status(400).json({
      success: false,
      message: "Invalid username",
    });
  }

  db.createUser(email, username, password, (err, user) => {
    if (err) {
      return res.status(500).json({ success: false, message: err });
    }
    req.session.user = {
      email,
      username,
      id: user.id,
    };
    res.json({ success: true, message: "User registered" });
  });
});

app.post("/login", mustNotBeAuthenticated, (req, res) => {
  const { email, password } = req.body;
  db.checkPassword(email, password, (err, result) => {
    if (err) {
      return res.status(500).json({ success: false, message: "Error" });
    }
    if (!result) {
      return res.status(401).json({ success: false, message: "Invalid login" });
    }
    req.session.user = {
      email,
      username: result.username,
      id: result.id,
    };
    res.json({ success: true, message: "Logged in" });
  });
});

app.post("/upload", mustBeAuthenticated, (req, res) => {
  if (!req.files || Object.keys(req.files).length === 0) {
    return res
      .status(400)
      .json({ success: false, message: "No files uploaded" });
  }

  if (req.files.exploitFile.size > LIMIT_FILESIZE_MB * 1024 * 1024) {
    // 10 MB limit
    return res.status(400).json({
      success: false,
      message: `File too large. Limit is ${LIMIT_FILESIZE_MB} MB`,
    });
  }

  let exploitFile = req.files.exploitFile;
  let uploadPath = path.join(
    UPLOAD_FOLDER,
    uniqueFilename(req.session.user.username) + path.extname(exploitFile.name),
  );

  exploitFile.mv(uploadPath, (err) => {
    if (err) {
      console.error(err);
      return res
        .status(500)
        .json({ success: false, message: "Error uploading file" });
    }

    res.json({ success: true, message: "File uploaded!" });
  });
});

app.get("/me", (req, res) => {
  console.log("me", req.session);
  if (req.session.user) {
    return res.json({ user: req.session.user });
  }
  res.status(401).json({ message: "Not logged in" });
});

app.get("/myuploads", mustBeAuthenticated, (req, res) => {
  const userFiles = fs
    .readdirSync(UPLOAD_FOLDER)
    .filter((file) => file.startsWith(req.session.user.username + "_"));

  res.json({ files: userFiles });
});

// Serve uploaded files
app.get("/uploads/:filename", mustBeAuthenticated, (req, res) => {
  const { filename } = req.params;
  const { download } = req.query;

  const filePath = path.join(UPLOAD_FOLDER, filename);

  if (!path.resolve(filePath).startsWith(path.resolve(UPLOAD_FOLDER))) {
    return res.status(400).send("Invalid file path");
  }

  if (!filename.startsWith(req.session.user.username + "_")) {
    return res.status(403).send("Access denied");
  }

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found");
  }

  if (download) {
    return res.download(filePath);
  }

  res.sendFile(filePath);
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
