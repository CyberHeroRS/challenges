const { Router } = require("express");
const { v4: uuidv4 } = require("uuid");
const users = require("../db/users");
const catalogue = require("../db/catalogue");
const { sessions, authMiddleware, getUser } = require("../middleware/auth");
const { renderPage } = require("../views/layout");
const { homeView } = require("../views/home");
const { loginView, loginErrorView, registerView, registerErrorView } = require("../views/auth");
const { profileView, profileNotFoundView } = require("../views/profile");
const { accountView } = require("../views/account");
const { editProfileView } = require("../views/edit-profile");
const { reportFormView } = require("../views/report");

const router = Router();

router.get("/", (req, res) => {
  const user = getUser(req);
  const items = catalogue.getAll.all();

  res.send(renderPage("Enter the Cave", homeView(items, user), user));
});

router.get("/login", (req, res) => {
  res.send(renderPage("Enter the Cave", loginView()));
});

router.post("/login", (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.send(renderPage("Enter the Cave", loginErrorView()));
  
  const user = users.findByCredentials.get(username, password);
  if (!user) return res.send(renderPage("Enter the Cave", loginErrorView()));
  
  const sid = uuidv4();
  sessions.set(sid, { id: user.id, username: user.username });
  
  res.cookie("session", sid, { httpOnly: true, sameSite: "Lax" });
  res.redirect("/my-account");
});

router.get("/register", (req, res) => {
  res.send(renderPage("Join the Thieves", registerView()));
});

router.post("/register", (req, res) => {
  const { username, password, biography, sesame_password } = req.body;
  const bio = biography || "";
  if (!username || !password || !sesame_password || username.length > 32 || !/^[a-zA-Z0-9]+$/.test(username) || password.length > 128 || bio.length > 2048) {
    return res.send(renderPage("Join the Thieves", registerErrorView()));
  }
  try {
    const id = uuidv4();
    users.create.run(id, username, password, bio, sesame_password);

    const sid = uuidv4();
    sessions.set(sid, { id, username: username });
    
    res.cookie("session", sid, { httpOnly: true, sameSite: "Lax" });
    res.redirect("/my-account");
  } catch (e) {
    res.send(renderPage("Join the Thieves", registerErrorView()));
  }
});

router.get("/profile/:username", (req, res) => {
  const profile = users.findByUsername.get(req.params.username);
  if (!profile) return res.status(404).send(renderPage("Not Found", profileNotFoundView()));
  
  res.send(renderPage(`${profile.username}'s Profile`, profileView(profile.username), getUser(req)));
});

router.get("/my-account", authMiddleware, (req, res) => {
  const user = users.findById.get(req.user.id);
  res.send(renderPage("My Account", accountView(user), { username: user.username }));
});

router.get("/my-account/edit", authMiddleware, (req, res) => {
  const user = users.findById.get(req.user.id);
  res.send(renderPage("Edit Profile", editProfileView(user), { username: user.username }));
});

router.post("/my-account/edit", authMiddleware, (req, res) => {
  const { biography, sesame_password } = req.body;
  if (!sesame_password || (biography && biography.length > 2048)) return res.redirect("/my-account/edit");

  users.updateProfile.run(biography || "", sesame_password, req.user.id);
  res.redirect("/my-account");
});

router.get("/logout", (req, res) => {
  const sid = req.cookies.session;
  if (sid) sessions.delete(sid);
  
  res.clearCookie("session");
  res.redirect("/");
});

router.get("/report", authMiddleware, (req, res) => {
  res.send(renderPage("Report to the Captain", reportFormView(), { username: req.user.username }));
});

module.exports = router;
