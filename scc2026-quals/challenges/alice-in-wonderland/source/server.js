const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 1337;
const STATIC_DIR = path.join(__dirname, "static");

// Serve static files (index.html, images, archives, etc.) from /static
app.use(express.static(STATIC_DIR));

// Explicit index route
app.get("/", (req, res) => {
  res.sendFile(path.join(STATIC_DIR, "index.html"));
});

app.get("/fl4g", (req, res) => {
  res.set("Content-Type", "text/html; charset=utf-8");
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Rus</title>
  <a href="https://www.tiktok.com/@the.world.is.your6063/video/7587598074906807608?q=dekibmw&t=1773131338594">Here is your first part of flag.</a>
});
</html>`);
});

// Special hole 67 -> falling image
app.get("/hole/754", (req, res) => {
  res.set("Content-Type", "text/html; charset=utf-8");
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>falling</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #000;
      color: #0f0;
      font-family: "Courier New", Courier, monospace;
      text-shadow: 0 0 5px #0f0;
    }
    img {
      max-width: 80vw;
      max-height: 80vh;
      display: block;
    }
  </style>
</head>
<body>
  <img src="/falling.jpg" alt="falling" />
</body>
</html>`);
});

app.get("/wonderl4nd/d1nn3r", (req, res) => {
  res.set("Content-Type", "text/html; charset=utf-8");
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>wonderland dinner</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #000;
      background-image:
        radial-gradient(circle at top, rgba(0, 255, 0, 0.12), transparent 60%),
        radial-gradient(circle at bottom, rgba(0, 255, 128, 0.06), transparent 60%);
      color: #0f0;
      font-family: "Courier New", Courier, monospace;
      text-shadow: 0 0 6px #0f0;
      padding: 1.5rem;
    }
    .frame {
      max-width: 900px;
      width: 100%;
      border: 1px solid rgba(0, 255, 0, 0.4);
      box-shadow:
        0 0 20px rgba(0, 255, 0, 0.25),
        0 0 2px rgba(0, 255, 0, 0.6);
      padding: 1.5rem 1.75rem;
      background: radial-gradient(circle at center, rgba(0, 0, 0, 0.9), #000);
    }
    .title {
      font-family: "Georgia", "Times New Roman", serif;
      font-size: 1.1rem;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: #e5e7eb;
      text-shadow: 0 0 4px #0f0;
      margin-bottom: 0.75rem;
    }
    .divider {
      height: 1px;
      width: 100%;
      background: linear-gradient(to right, rgba(0, 255, 0, 0.6), transparent);
      margin-bottom: 1rem;
    }
    .body-text {
      white-space: pre-wrap;
      line-height: 1.5;
      font-size: 0.95rem;
    }
    .whisper {
      font-family: "Georgia", "Times New Roman", serif;
      color: #e5e7eb;
      text-shadow: 0 0 3px #0f0;
    }
    .image {
      margin-top: 1.25rem;
      text-align: center;
    }
    .image img {
      max-width: 80vw;
      max-height: 60vh;
      border: 1px solid rgba(0, 255, 0, 0.5);
      box-shadow:
        0 0 18px rgba(0, 255, 0, 0.35),
        0 0 2px rgba(0, 255, 0, 0.7);
      display: inline-block;
    }
    .image--top {
      margin-bottom: 1.25rem;
    }
    .image--receipt img {
      max-width: 90vw;
      max-height: 70vh;
      border: none;
      box-shadow: none;
    }
    @media (max-width: 640px) {
      .frame {
        padding: 1.1rem 1.1rem;
      }
    }
  </style>
</head>
<body>
  <div class="frame">
    <div class="image image--top">
      <img src="/dinner.jpg" alt="wonderland dinner" />
    </div>
    <div class="title">MAD TEA-LEDGER</div>
    <div class="divider"></div>
    <div class="body-text">
Alice has finished her feast, but the Hatter refuses to let her leave until the debt is settled. He whispered:

<span class="whisper">"Look to the ledger where the stars have fallen; only those items carry the weight of the truth. Gather the totals and seek out the Great Adhesive Bin where every scrap of ink is pinned for the world to see. Only there will you find the path to the Queen’s Court."</span>
    </div>
    <div class="image image--receipt">
      <img src="/receipt.png" alt="wonderland receipt" />
    </div>
  </div>
</body>
</html>`);
});


app.get("/d33333333p3r", (req, res) => {
  res.set("Content-Type", "text/html; charset=utf-8");
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>The Queen's Court</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #050000;
      background-image:
        radial-gradient(circle at top, rgba(248, 113, 113, 0.4), transparent 55%),
        radial-gradient(circle at bottom, rgba(127, 29, 29, 0.7), #020000 70%);
      color: #fee2e2;
      font-family: "Georgia", "Times New Roman", serif;
      text-shadow: 0 0 6px rgba(248, 113, 113, 0.9);
      padding: 1.5rem;
    }
    .frame {
      max-width: 980px;
      width: 100%;
      border: 1px solid rgba(248, 113, 113, 0.7);
      box-shadow:
        0 0 40px rgba(248, 113, 113, 0.75),
        0 0 4px rgba(239, 68, 68, 0.9);
      padding: 1.5rem 1.75rem 1.75rem;
      background:
        radial-gradient(circle at top, rgba(127, 29, 29, 0.9), rgba(15, 23, 42, 0.98));
      overflow: hidden;
    }
    .banner {
      text-align: center;
      margin-bottom: 1.2rem;
    }
    .banner img {
      max-width: 90vw;
      max-height: 45vh;
      display: inline-block;
      box-shadow:
        0 0 38px rgba(248, 113, 113, 0.8),
        0 0 4px rgba(239, 68, 68, 0.9);
    }
    .title {
      font-size: 1.3rem;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      color: #fee2e2;
      text-align: center;
      margin-top: 1.1rem;
      margin-bottom: 0.3rem;
    }
    .subtitle {
      text-align: center;
      font-size: 0.9rem;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: #fecaca;
      margin-bottom: 0.8rem;
    }
    .divider {
      height: 1px;
      width: 100%;
      background: linear-gradient(to right, rgba(248, 113, 113, 0.9), transparent);
      margin: 0.8rem 0 1.1rem;
    }
    .body-text {
      white-space: pre-wrap;
      line-height: 1.6;
      font-size: 0.98rem;
    }
    .body-text code {
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco,
        Consolas, "Liberation Mono", "Courier New", monospace;
      background: rgba(127, 29, 29, 0.6);
      padding: 0.15rem 0.3rem;
      border-radius: 0.25rem;
      color: #fee2e2;
    }
    .section-heading {
      margin-top: 1.4rem;
      margin-bottom: 0.4rem;
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: #fecaca;
    }
    .download {
      margin-top: 1.2rem;
      text-align: center;
    }
    .download a {
      display: inline-block;
      padding: 0.55rem 1.1rem;
      border-radius: 999px;
      border: 1px solid rgba(248, 113, 113, 0.9);
      color: #fee2e2;
      text-decoration: none;
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco,
        Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.85rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      background: radial-gradient(circle at top, rgba(127, 29, 29, 0.95), rgba(0, 0, 0, 0.95));
      box-shadow:
        0 0 20px rgba(248, 113, 113, 0.75),
        0 0 0 1px rgba(127, 29, 29, 0.9);
    }
    .download a:hover {
      background: radial-gradient(circle at top, rgba(220, 38, 38, 0.98), rgba(0, 0, 0, 0.98));
      box-shadow:
        0 0 26px rgba(248, 113, 113, 0.95),
        0 0 0 1px rgba(248, 113, 113, 1);
    }
    .moral {
      margin-top: 1.5rem;
      font-style: italic;
      text-align: right;
      color: #fee2e2;
    }
    @keyframes court-shake {
      0%   { transform: translate3d(0, 0, 0); }
      20%  { transform: translate3d(-4px, 2px, 0); }
      40%  { transform: translate3d(4px, -2px, 0); }
      60%  { transform: translate3d(-3px, 1px, 0); }
      80%  { transform: translate3d(3px, -1px, 0); }
      100% { transform: translate3d(0, 0, 0); }
    }
    body.shake-mode {
      animation: court-shake 0.42s linear infinite;
    }
    @media (max-width: 640px) {
      .frame {
        padding: 1.1rem 1.1rem 1.4rem;
      }
      .banner img {
        max-height: 40vh;
      }
    }
  </style>
</head>
<body>
  <div class="frame">
    <div class="banner">
      <img src="/queencourt.jpg" alt="The Queen's Court" />
    </div>
    <div class="title">THE QUEEN'S COURT</div>
    <div class="subtitle">CASE #0xDEADBEEF · TRIAL OF THE DIGITAL KNAVE</div>
    <div class="divider"></div>
    <div class="body-text">
The Queen's Court: Case #0xDEADBEEF
"The Queen! The Queen!" and the three gardeners instantly threw themselves flat upon their faces.

Alice had never seen such a court in her life. The King and Queen of Hearts were seated on their throne, with a great crowd assembled about them—all sorts of little birds and beasts, as well as the whole pack of cards.

"Sentence first—verdict afterwards!" shouted the Queen.

"No, no!" said Alice. "It’s nonsense, the idea of having the sentence first!"
"Hold your tongue!" said the Queen, turning purple.
"Off with her head!"

The Evidence:
The White Rabbit blew three blasts on the trumpet, and then unrolled a parchment scroll. "Herald, read the accusation!" he cried.

But the scroll was blank. The evidence is not in the ink, but in the air itself.
    </div>
    <div class="download">
      <a id="verdict-download" href="/VERDICT.wav" download>[ Download VEDRICT.wav ]</a>
    </div>
    <div class="moral">
“Everything’s got a moral, if only you can find it.”
    </div>
  </div>
  <script>
    (function () {
      var link = document.getElementById("verdict-download");
      if (!link) return;
      link.addEventListener("mouseenter", function () {
        document.body.classList.add("shake-mode");
      });
      link.addEventListener("mouseleave", function () {
        document.body.classList.remove("shake-mode");
      });
      link.addEventListener("blur", function () {
        document.body.classList.remove("shake-mode");
      });
    })();
  </script>
</body>
</html>`);
});

app.get("/hole", (req, res) => {
  res.set("Content-Type", "text/html; charset=utf-8");
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Follow the Right Door</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #000;
      background-image:
        radial-gradient(circle at top, rgba(0, 255, 0, 0.12), transparent 60%),
        radial-gradient(circle at bottom, rgba(0, 255, 128, 0.06), transparent 60%);
      color: #0f0;
      font-family: "Courier New", Courier, monospace;
      text-shadow: 0 0 6px #0f0;
      padding: 1.5rem;
    }
    .frame {
      max-width: 1100px;
      width: 100%;
      border: 1px solid rgba(0, 255, 0, 0.4);
      box-shadow:
        0 0 20px rgba(0, 255, 0, 0.35),
        0 0 2px rgba(0, 255, 0, 0.7);
      padding: 1.3rem 1.6rem 1.6rem;
      background: radial-gradient(circle at center, rgba(0, 0, 0, 0.9), #000);
    }
    .title {
      font-size: 1rem;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      margin-bottom: 0.4rem;
    }
    .subtitle {
      font-size: 0.88rem;
      color: #a7f3d0;
      margin-bottom: 0.8rem;
    }
    .doors-image {
      text-align: center;
      margin-bottom: 1rem;
    }
    .doors-image img {
      max-width: 100%;
      max-height: 45vh;
      display: inline-block;
      border: 1px solid rgba(0, 255, 0, 0.5);
      box-shadow:
        0 0 18px rgba(0, 255, 0, 0.35),
        0 0 2px rgba(0, 255, 0, 0.7);
    }
    .doors-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      justify-content: center;
      margin-top: 0.4rem;
    }
    .door-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 82px;
      height: 32px;
      border-radius: 6px;
      border: 1px solid rgba(0, 255, 0, 0.4);
      text-decoration: none;
      color: #bbf7d0;
      font-size: 0.7rem;
      background: radial-gradient(circle at top, rgba(0, 0, 0, 0.95), rgba(0, 0, 0, 0.7));
      box-shadow: 0 0 8px rgba(0, 255, 0, 0.5);
    }
    .door-link:hover {
      background: radial-gradient(circle at top, rgba(22, 163, 74, 0.9), rgba(0, 0, 0, 0.9));
      color: #ecfdf5;
      box-shadow: 0 0 12px rgba(34, 197, 94, 0.9);
    }
    .hint {
      margin-top: 0.7rem;
      font-size: 0.78rem;
      color: #6ee7b7;
      text-align: right;
    }
    @media (max-width: 640px) {
      .frame {
        padding: 1.1rem 1.1rem 1.3rem;
      }
      .door-link {
        width: 72px;
        height: 30px;
        font-size: 0.68rem;
      }
    }
  </style>
</head>
<body>
  <div class="frame">
    <div class="title">FOLLOW THE RABBIT</div>
    <div class="subtitle">Find which hole the rabbit slipped through.</div>
    <div class="doors-image">
      <img src="/alicedoors.jpg" alt="A hall of holes in Wonderland" />
    </div>
    <div id="doors" class="doors-grid"></div>
    <div class="hint">1337 doors. Only one entrance was real.</div>
  </div>
  <script>
    (function () {
      var container = document.getElementById("doors");
      if (!container) return;
      for (var i = 1; i <= 1337; i++) {
        var a = document.createElement("a");
        a.href = "/hole/" + i;
        a.className = "door-link";
        a.textContent = "hole " + i;
        container.appendChild(a);
      }
    })();
  </script>
</body>
</html>`);
});

// All other /hole/:id -> "Try harder..."
app.get("/hole/:id", (req, res) => {
  const { id } = req.params;

  res.set("Content-Type", "text/html; charset=utf-8");
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>hole ${id}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #000;
      color: #0f0;
      font-family: "Courier New", Courier, monospace;
      text-shadow: 0 0 5px #0f0;
      font-size: 1.5rem;
    }
  </style>
</head>
<body>
  Try harder...
</body>
</html>`);
});


app.listen(PORT, () => {
  console.log(`Alice in Wonderland challenge listening on http://localhost:${PORT}`);
});
