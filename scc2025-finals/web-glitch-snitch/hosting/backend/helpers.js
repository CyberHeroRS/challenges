function mustBeAuthenticated(req, res, next) {
  if (req.session.user) {
    return next();
  }
  res.status(401).send("Access denied");
}

function mustNotBeAuthenticated(req, res, next) {
  if (req.session.user) {
    return res.send("Already logged in");
  }
  next();
}

function uniqueFilename(prefix) {
  return `${prefix}_${Math.floor(
    Date.now() / 1000
  )}`;
}

module.exports = {
  mustBeAuthenticated,
  mustNotBeAuthenticated,
  uniqueFilename,
};
