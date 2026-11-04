import cookieParser from "cookie-parser";
import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { UserRecord } from "./types.js";
import {
  authenticate,
  createPost,
  createReport,
  createSession,
  createUser,
  destroySession,
  readModeratorArchive,
  getSafeViewer,
  getUserBySession,
  applyImportedPreferences,
  listPosts,
  listReports,
  updateProfile
} from "./store.js";

const app = express();
const port = Number(process.env.PORT ?? 3000);
const sessionCookie = "threadboard.sid";
const sessionSecret = process.env.SESSION_SECRET ?? "forum-secret";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webDist = process.env.WEB_DIST ?? path.resolve(__dirname, "../../web-dist");

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser(sessionSecret));

function currentUser(req: express.Request) {
  return getUserBySession(req.cookies[sessionCookie]);
}

function requireUser(
  req: express.Request,
  res: express.Response,
  next: express.NextFunction
) {
  const user = currentUser(req);
  if (!user) {
    res.status(401).json({ error: "Authentication required." });
    return;
  }

  res.locals.user = user;
  next();
}

app.get("/api/health", (_req, res) => {
  res.json({ ok: true });
});

app.get("/api/me", (req, res) => {
  const user = currentUser(req);
  if (!user) {
    res.status(401).json({ error: "Authentication required." });
    return;
  }

  res.json(getSafeViewer(user));
});

app.get("/api/posts", (_req, res) => {
  res.json({ posts: listPosts() });
});

app.post("/api/posts", requireUser, (req, res) => {
  const user = res.locals.user as { username: string };
  const title = String(req.body?.title ?? "").trim();
  const body = String(req.body?.body ?? "").trim();

  if (!title || !body) {
    res.status(400).json({ error: "Title and body are required." });
    return;
  }

  const post = createPost(user.username, title, body);
  res.json({ ok: true, post });
});

app.post("/api/settings/profile", requireUser, (req, res) => {
  const user = res.locals.user as { username: string };
  const displayName = String(req.body?.displayName ?? "");
  const bio = String(req.body?.bio ?? "");

  const updated = updateProfile(user.username, displayName, bio);
  if (!updated) {
    res.status(404).json({ error: "User not found." });
    return;
  }

  res.json({ ok: true, viewer: getSafeViewer(updated) });
});

app.post("/api/settings/import", requireUser, (req, res) => {
  const user = res.locals.user as { username: string };
  const config = req.body?.config;

  if (!config || typeof config !== "object" || Array.isArray(config)) {
    res.status(400).json({ error: "config object is required." });
    return;
  }

  const updated = applyImportedPreferences(user.username, config as Record<string, unknown>);
  if (!updated) {
    res.status(404).json({ error: "User not found." });
    return;
  }

  res.json({ ok: true, viewer: getSafeViewer(updated) });
});

app.post("/api/reports", requireUser, (req, res) => {
  const user = res.locals.user as { username: string };
  const url = String(req.body?.url ?? "");
  const reason = String(req.body?.reason ?? "");

  if (!url) {
    res.status(400).json({ error: "URL is required." });
    return;
  }

  const report = createReport(user.username, url, reason);
  res.json({ ok: true, report });
});

app.get("/api/reports", requireUser, (_req, res) => {
  res.json({ reports: listReports() });
});

app.get("/api/mod/logs/export", requireUser, (req, res) => {
  const user = res.locals.user as UserRecord;
  const mF = readModeratorArchive(user);
  if (!mF) {
    res.status(403).json({ error: "Moderator privileges required." });
    return;
  }

  res.json({
    exportId: "mod-audit-2026-03-16",
    archive: mF
  });
});

app.post("/api/auth/register", (req, res) => {
  const username = String(req.body?.username ?? "").trim();
  const password = String(req.body?.password ?? "").trim();

  if (!username || !password) {
    res.status(400).json({ error: "Username and password are required." });
    return;
  }

  const created = createUser(username, password);
  if ("error" in created) {
    res.status(400).json({ error: created.error });
    return;
  }

  const sessionId = createSession(created.user.id);
  res.cookie(sessionCookie, sessionId, {
    httpOnly: true,
    sameSite: "lax",
    signed: false
  });

  res.json({ ok: true, viewer: getSafeViewer(created.user) });
});

app.post("/api/auth/login", (req, res) => {
  const username = String(req.body?.username ?? "").trim();
  const password = String(req.body?.password ?? "").trim();
  const user = authenticate(username, password);

  if (!user) {
    res.status(401).json({ error: "Invalid credentials." });
    return;
  }

  const sessionId = createSession(user.id);
  res.cookie(sessionCookie, sessionId, {
    httpOnly: true,
    sameSite: "lax",
    signed: false
  });

  res.json({ ok: true, viewer: getSafeViewer(user) });
});

app.get("/api/auth/logout", (req, res) => {
  destroySession(req.cookies[sessionCookie]);
  res.clearCookie(sessionCookie);
  res.redirect("/");
});

app.use(express.static(webDist));

app.get("*", (req, res) => {
  if (req.path.startsWith("/api/")) {
    res.status(404).json({ error: "Not found." });
    return;
  }

  res.sendFile(path.join(webDist, "index.html"));
});

app.listen(port, "0.0.0.0",() => {
  console.log(`ThreadBoard API listening on ${port}`);
});
