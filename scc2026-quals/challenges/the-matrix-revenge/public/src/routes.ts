import path from "path";
import { Express, Request, Response } from "express";
import {
  getPosts,
  createPost,
  removePost,
  updatePost,
  isValidUserToken,
  regenAdminToken,
  getCommentsForPost,
  addComment,
} from "./utils";
import { authMiddleware, adminMiddleware, AuthedRequest } from "./middleware/auth";
import { visitUrl } from "./bot";

export function registerRoutes(
  app: Express,
  sessionVersion: string,
  rootDir: string,
): void {
  app.get("/", (_req: Request, res: Response) => {
    res.sendFile(path.join(rootDir, "index.html"));
  });

  app.get("/dashboard", (_req: Request, res: Response) => {
    res.sendFile(path.join(rootDir, "dashboard.html"));
  });

  app.get("/thread/:id", (_req: Request, res: Response) => {
    res.sendFile(path.join(rootDir, "index.html"));
  });

  app.get("/404", (_req: Request, res: Response) => {
    res.status(404).sendFile(path.join(rootDir, "404.html"));
  });

  // Auth
  app.post("/api/login", (req: Request, res: Response) => {
    const { username, token } = (req.body || {}) as {
      username?: string;
      token?: unknown;
    };

    if (!username || token === undefined) {
      return res
        .status(400)
        .json({ ok: false, error: "username and token are required" });
    }

    if (!isValidUserToken(username, token)) {
      return res.status(401).json({ ok: false, error: "login failed" });
    }

    req.session.loggedin = true;
    req.session.username = username;
    req.session.sessionversion = sessionVersion;
    if (username === "admin") {
      (req.session as any).admin = true;
    }

    return res.json({
      ok: true,
      user: { username },
    });
  });

  app.post("/api/logout", (req: Request, res: Response) => {
    req.session.loggedin = false;
    req.session.username = undefined;
    req.session.sessionversion = undefined;
    req.session.destroy(() => {
    });
    return res.json({ ok: true, message: "logged out" });
  });

  app.get(
    "/api/admin-token",
    adminMiddleware,
    (req: AuthedRequest, res: Response) => {
      const token = regenAdminToken();
      res.json({ token });
    },
  );

  // Posts CRUD
  app.get("/api/posts", (_req: Request, res: Response) => {
    res.json({ ok: true, posts: getPosts() });
  });

  app.post("/api/posts", authMiddleware, (req: AuthedRequest, res: Response) => {
    const { title, content } = (req.body || {}) as {
      title?: string;
      content?: string;
    };
    if (!title || !content) {
      return res
        .status(400)
        .json({ ok: false, error: "title and content are required" });
    }

    const username = req.user?.username ?? "ghost";
    const post = createPost(username, title, content);
    return res.status(201).json({ ok: true, post });
  });

  app.put(
    "/api/posts/:id",
    authMiddleware,
    (req: AuthedRequest, res: Response) => {
      const id = Number(req.params.id);
      const { title, content } = (req.body || {}) as {
        title?: string;
        content?: string;
      };

      const post = updatePost(id, { title, content });
      if (!post) {
        return res.status(404).json({ ok: false, error: "post not found" });
      }

      return res.json({ ok: true, post });
    },
  );

  app.delete(
    "/api/posts/:id",
    authMiddleware,
    (req: AuthedRequest, res: Response) => {
      const id = Number(req.params.id);
      const removed = removePost(id);
      if (!removed) {
        return res.status(404).json({ ok: false, error: "post not found" });
      }
      return res.json({ ok: true, post: removed });
    },
  );

  // Comments
  app.get("/api/posts/:id/comments", (req: Request, res: Response) => {
    const id = Number(req.params.id);
    if (!Number.isFinite(id)) {
      return res.status(400).json({ ok: false, error: "invalid post id" });
    }
    const postComments = getCommentsForPost(id);
    return res.json({ ok: true, comments: postComments });
  });

  app.post(
    "/api/posts/:id/comments",
    authMiddleware,
    (req: AuthedRequest, res: Response) => {
      const id = Number(req.params.id);
      if (!Number.isFinite(id)) {
        return res.status(400).json({ ok: false, error: "invalid post id" });
      }

      const { content } = (req.body || {}) as { content?: string };
      if (!content) {
        return res
          .status(400)
          .json({ ok: false, error: "comment content is required" });
      }

      const username = req.user?.username ?? "ghost";
      const comment = addComment(id, username, content);
      if (!comment) {
        return res.status(404).json({ ok: false, error: "post not found" });
      }

      return res.status(201).json({ ok: true, comment });
    },
  );

  app.post("/api/report", (req: Request, res: Response) => {
    const { url, notes } = (req.body || {}) as { url?: string; notes?: string };
    if (!url || typeof url !== "string") {
      return res.status(400).json({ ok: false, error: "url is required" });
    }

    try {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      visitUrl(url).catch((err: unknown) => {
        // eslint-disable-next-line no-console
        console.error("Bot visit failed:", err);
      });
    } catch {
      // ignore synchronous require-level issues
    }

    return res.json({ ok: true, queued: true, url, notes: notes || "" });
  });

  // Session endpoint: reflects header-based auth status.
  app.get("/api/session", (req: AuthedRequest, res: Response) => {
    if (req.session?.loggedin && req.session.sessionversion === sessionVersion) {
      return res.json({
        authenticated: true,
        user: { username: req.session.username ?? "ghost" },
        isAdmin:
          (req.session as any).admin === true &&
          req.session.username === "admin",
        via: "session",
      });
    }

    const username = req.header("x-username");
    const token = req.header("x-token");

    if (!username || !token || !isValidUserToken(username, token)) {
      return res.json({ authenticated: false, user: null });
    }

    return res.json({
      authenticated: true,
      user: { username },
      isAdmin: username === "admin",
      via: "headers",
    });
  });

  // Catch-all: let the static middleware try first, then redirect to /404.
  app.use((_req: Request, res: Response) => {
    res.redirect("/404");
  });
}
