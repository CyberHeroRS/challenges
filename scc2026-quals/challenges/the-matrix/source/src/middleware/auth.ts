import { Request, Response, NextFunction } from "express";
import { isValidUserToken } from "../utils";

export interface AuthedRequest extends Request {
  user?: { username: string };
}

export function authMiddleware(
  req: AuthedRequest,
  res: Response,
  next: NextFunction,
) {
  const expectedSessionVersion = process.env.SESSION_VERSION || "1";
  // Prefer session if present and version matches.
  if (
    req.session?.loggedin &&
    req.session.sessionversion === expectedSessionVersion
  ) {
    req.user = { username: req.session.username ?? "ghost" };
    return next();
  }

  const username = req.header("x-username");
  const token = req.header("x-token");

  if (!username || !token) {
    return res.status(401).json({ ok: false, error: "missing credentials" });
  }

  if (!isValidUserToken(username, token)) {
    return res.status(401).json({ ok: false, error: "invalid credentials" });
  }

  req.user = { username };
  return next();
}

export function adminMiddleware(
  req: AuthedRequest,
  res: Response,
  next: NextFunction,
) {
  if (
    req.session?.loggedin &&
    (req.session as any).admin === true &&
    req.session.username === "admin"
  ) {
    return next();
  }
  return res.status(403).json({ ok: false, error: "admin privileges required" });
}
