const sessions = new Map();

function authenticate(req) {
  const sid = req.cookies.session;
  if (sid && sessions.has(sid)) {
    req.user = sessions.get(sid);
    return true;
  }
  return false;
}

function authMiddleware(req, res, next) {
  if (authenticate(req)) return next();
  res.redirect("/login");
}

function apiAuth(req, res, next) {
  if (authenticate(req)) return next();
  res.status(401).json({ error: "Not authenticated" });
}

function getUser(req) {
  const sid = req.cookies.session;
  return sid ? sessions.get(sid) : null;
}

module.exports = { sessions, authMiddleware, apiAuth, getUser };
