
let browser = null;
const BOT_ORIGIN = process.env.BOT_ORIGIN + ":" + process.env.PORT || `https://localhost:${process.env.PORT}`;
const BOT_FLAG_COOKIE_VALUE =
  process.env.BOT_FLAG_COOKIE_VALUE || "SCC{matrix_cookie_flag_placeholder}";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function runRoutineDashboardTask(getActivePage) {
  const currentPage = getActivePage();
  if (!currentPage || currentPage.isClosed()) {
    return null;
  }

  try {
    await currentPage.bringToFront();
    await currentPage.click("#dashboard-btn");
    return currentPage;
  } catch {
    try {
      // Fallback we kept after some flaky CI runs where Puppeteer said
      // "not clickable" even though the button existed in DOM.
      await currentPage.$eval("#dashboard-btn", (el) => {
        el.scrollIntoView({ block: "center", inline: "center" });
        el.click();
      });
      return currentPage;
    } catch {
      return null;
    }
  }
}

async function getBrowser() {
  if (!browser) {
    // eslint-disable-next-line @typescript-eslint/no-var-requires,@typescript-eslint/no-require-imports
    const puppeteer = require("puppeteer");
    browser = await puppeteer.launch({
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-features=BlockThirdPartyCookies,ImprovedCookieControls,TrackingProtection3pcd",
      ],
    });
  }
  return browser;
}

async function visitUrl(targetUrl) {
  const b = await getBrowser();
  const context = await b.createBrowserContext();
  const page = await context.newPage();
  let activePage = page;

  const onTargetCreated = async (target) => {
    if (target.type() !== "page") return;
    if (target.browserContext() !== context) return;
    try {
      const p = await target.page();
      if (!p) return;
      // Keep pointer on latest foreground-like tab (popup flows rely on this).
      activePage = p;
    } catch {
      // ignore races
    }
  };

  b.on("targetcreated", onTargetCreated);

  try {
    // 1) Log in as admin on matrix-web.
    await page.goto(`${BOT_ORIGIN}/`, { waitUntil: "networkidle2", timeout: 15000 });
    const loginResult = await page.evaluate(async () => {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "admin", token: "admin" }),
      });
      return response.ok;
    });

    if (!loginResult) {
      throw new Error("admin login failed");
    }

    // 2) Set flag cookie before visiting reported URL.
    const cookieTargets = new Set([
      BOT_ORIGIN,
      "http://127.0.0.1:3000",
      "http://localhost:3000",
    ]);
    try {
      const parsed = new URL(targetUrl);
      if (parsed.protocol === "http:" || parsed.protocol === "https:") {
        cookieTargets.add(parsed.origin);
      }
    } catch {
      // keep BOT_ORIGIN only
    }

    await page.setCookie(
      ...Array.from(cookieTargets).map((origin) => {
        const isHttps = origin.startsWith("https://");
        return {
          name: "flag",
          value: BOT_FLAG_COOKIE_VALUE,
          url: origin,
          path: "/",
          httpOnly: false,
          // Allow cross-site report flows on https; keep local http usable in dev.
          secure: isHttps,
          sameSite: isHttps ? "None" : "Lax",
        };
      }),
    );

    // 3) Reuse same tab for reported URL.
    await page.goto(targetUrl, { waitUntil: "networkidle2", timeout: 15000 });

    // Re-assert cookie on final origin to reduce docker/local hostname drift.
    try {
      const finalOrigin = new URL(page.url()).origin;
      const isHttps = finalOrigin.startsWith("https://");
      await page.setCookie({
        name: "flag",
        value: BOT_FLAG_COOKIE_VALUE,
        url: finalOrigin,
        path: "/",
        httpOnly: false,
        secure: isHttps,
        sameSite: isHttps ? "None" : "Lax",
      });
    } catch {
      // ignore invalid/unavailable page URL races
    }

    // Daily routine dashboard check! A must for all employees!!!
    await sleep(3000);
    // Prefer clicking dashboard in the originally reported page to avoid
    // popup-tab races that are more pronounced in container timing.
    const clickedPage =
      (await runRoutineDashboardTask(() => page)) ||
      (await runRoutineDashboardTask(() => activePage);

    await sleep(15000);

    // Close the dashboard window.
    const dashPage = clickedPage || activePage;

    if (dashPage) {
      await dashPage.bringToFront();
      try {
        await dashPage.click("#close-dashboard-btn");
      } catch {
        // ignore missing close button
      }
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error("Bot visit error:", err);
  } finally {
    b.off("targetcreated", onTargetCreated);
    await context.close();
  }
}

module.exports = { visitUrl };
