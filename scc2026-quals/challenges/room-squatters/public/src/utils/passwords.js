const { randomBytes, scryptSync, timingSafeEqual } = require("node:crypto");

function hashPassword(password, salt = randomBytes(16).toString("hex")) {
  const hash = scryptSync(password, salt, 64).toString("hex");
  return { salt, hash };
}

function verifyPassword(password, salt, expectedHash) {
  const actualHash = scryptSync(password, salt, 64);
  const expected = Buffer.from(expectedHash, "hex");

  return (
    actualHash.length === expected.length &&
    timingSafeEqual(actualHash, expected)
  );
}

module.exports = {
  hashPassword,
  verifyPassword,
};
