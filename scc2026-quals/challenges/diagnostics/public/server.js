const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = Number(process.env.PORT || 4545);
const PUBLIC_DIR = path.join(__dirname, "public");

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".map": "application/json; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

function sendJson(res, statusCode, payload, extraHeaders = {}) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Content-Length": Buffer.byteLength(body),
    ...extraHeaders,
  });
  res.end(body);
}

function sendFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      sendJson(res, 404, { ok: false, error: "not found" });
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || "application/octet-stream";
    res.writeHead(200, {
      "Content-Type": contentType,
      "Cache-Control": "no-cache",
      "Content-Length": data.length,
    });
    res.end(data);
  });
}

function resolvePublicPath(urlPath) {
  const cleanPath = urlPath === "/" ? "/index.html" : urlPath;
  const normalized = path.normalize(cleanPath).replace(/^(\.\.[/\\])+/, "");
  return path.join(PUBLIC_DIR, normalized);
}

const server = http.createServer((req, res) => {
  const parsed = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

  if (parsed.pathname === "/api/pulse") {
    sendJson(
      res,
      200,
      {
        ok: true,
        node: "diag-grid",
        status: "nominal",
        tip: "lmfaooooooooooo",
      },
      { "x-diagnostic-relay": "FLAG_PART_D=pt4{1n_}" },
    );
    return;
  }

  const target = resolvePublicPath(parsed.pathname);
  if (!target.startsWith(PUBLIC_DIR)) {
    sendJson(res, 403, { ok: false, error: "forbidden" });
    return;
  }

  fs.stat(target, (err, stat) => {
    if (err || !stat.isFile()) {
      sendJson(res, 404, { ok: false, error: "not found" });
      return;
    }
    sendFile(res, target);
  });
});

server.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`diagnostics challenge listening on http://localhost:${PORT}`);
});
