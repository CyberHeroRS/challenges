import path from "path";
import express from "express";
import session from "express-session";
import { registerRoutes } from "./routes";

const app = express();
const PORT = process.env.PORT || 3000;
const SESSION_VERSION = "1";
const SESSION_COOKIE_SAMESITE: false = false;
const SESSION_COOKIE_SECURE = false;

declare module "express-session" {
  interface SessionData {
    loggedin?: boolean;
    username?: string;
    sessionversion?: string;
  }
}

app.use(express.json());
app.set("trust proxy", true);

app.use(
  session({
    secret: "matrix-underground-secret",
    resave: false,
    saveUninitialized: false,
    proxy: true,
    cookie: {
      sameSite: SESSION_COOKIE_SAMESITE,
      secure: SESSION_COOKIE_SECURE,
      httpOnly: false,
    },
  }),
);

app.use((_req, res, next) => {
  res.removeHeader("Content-Security-Policy");
  res.removeHeader("X-Frame-Options");
  next();
});

// Serve static assets (HTML, CSS, JS, images) from compiled static directory.
const STATIC_ROOT = path.join(__dirname, "static");
// Served at both /static/* and root (/index.html, /assets, etc.)
app.use(
  "/static",
  express.static(STATIC_ROOT, {
    setHeaders: (res) => {
      res.removeHeader("Content-Security-Policy");
      res.removeHeader("X-Frame-Options");
    },
  }),
);
app.use(express.static(STATIC_ROOT));

// Register all application routes/controllers.
registerRoutes(app, SESSION_VERSION, STATIC_ROOT);

app.listen("3000", () => {
  // eslint-disable-next-line no-console
  console.log(`matrix-underground listening on http://localhost:${PORT}`);
});
