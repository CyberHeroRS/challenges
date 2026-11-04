const { Router } = require("express");
const users = require("../db/users");
const catalogue = require("../db/catalogue");
const wishlist = require("../db/wishlist");
const { renderMarkdown } = require("../utils/markdown");
const { authMiddleware, apiAuth } = require("../middleware/auth");
const { visitUrl } = require("../bot");
const { renderPage } = require("../views/layout");
const { reportSentView } = require("../views/report");

const router = Router();

router.get("/profile/:username", (req, res) => {
  const profile = users.findByUsername.get(req.params.username);
  if (!profile) return res.status(404).json({ error: "User not found" });
  
  res.json({ username: profile.username, biography: renderMarkdown(profile.biography) });
});

router.get("/sesame/wishlist", apiAuth, (req, res) => {
  const items = wishlist.getByUser.all(req.user.id);

  res.json({ items });
});

router.post("/sesame/wishlist", apiAuth, (req, res) => {
  const { item_id } = req.body;

  const item = catalogue.findById.get(item_id);
  if (!item) return res.status(404).json({ error: "Item not found" });
  
  const existing = wishlist.exists.get(req.user.id, item_id);
  if (existing) return res.status(400).json({ error: "Already in wishlist" });
  
  wishlist.add.run(req.user.id, item_id);
  res.json({ success: true });
});

router.post("/report", authMiddleware, async (req, res) => {
  const url = req.body.url;
  if (!url || typeof url !== "string") return res.status(400).json({ error: "Missing URL" });

  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    return res.status(400).json({ error: "Invalid URL" });
  }

  if (!["http:", "https:"].includes(parsed.protocol)) {
    return res.status(400).json({ error: "Only http/https URLs are allowed" });
  }

  res.send(renderPage("Report Sent", reportSentView(), { username: req.user.username }));
  visitUrl(parsed.href).catch(console.error);
});

module.exports = router;
