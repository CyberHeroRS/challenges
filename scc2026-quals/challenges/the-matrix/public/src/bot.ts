import { getAdminToken } from "./utils";

let browser: any = null;
const BOT_ORIGIN = process.env.BOT_ORIGIN + ":" + process.env.PORT || `https://localhost:${process.env.PORT}`;
const BOT_FLAG_COOKIE_VALUE =
  process.env.BOT_FLAG_COOKIE_VALUE || "SCC{lol}";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function runRoutineDashboardTask(getActivePage: () => any): Promise<any> {
  const currentPage = getActivePage();
  if (!currentPage || currentPage.isClosed()) return null;

  try {
    await currentPage.bringToFront();
    await currentPage.click("#dashboard-btn");
    return currentPage;
  } catch {
    try {
      await currentPage.$eval("#dashboard-btn", (el: any) => {
        el.scrollIntoView({ block: "center", inline: "center" });
        el.click();
      });
      return currentPage;
    } catch {
      return null;
    }
  }
}

async function getBrowser(): Promise<any> {
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

export async function visitUrl(targetUrl: string): Promise<void> {
  const b = await getBrowser();
  const context = await b.createBrowserContext();
  const page = await context.newPage();
  let activePage = page;

  const onTargetCreated = async (target: any) => {
    if (target.type() !== "page") return;
    if (target.browserContext() !== context) return;
    try {
      const p = await target.page();
      if (!p) return;
      activePage = p;
    } catch {
      // ignore races
    }
  };

  b.on("targetcreated", onTargetCreated);

  try {
    await page.goto(`${BOT_ORIGIN}/`, { waitUntil: "networkidle2", timeout: 15000 });
    const adminToken = getAdminToken();
    const loginResult = await page.evaluate(async (token: string) => {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "admin", token }),
      });
      return response.ok;
    }, adminToken);

    if (!loginResult) {
      throw new Error("admin login failed");
    }

    const cookieTargets = new Set<string>([
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
          secure: isHttps,
          sameSite: isHttps ? "None" : "Lax",
        };
      }),
    );

    await page.goto(targetUrl, { waitUntil: "networkidle2", timeout: 15000 });

    // Re-assert cookie on the final loaded origin to avoid host/protocol drift
    // across local-vs-docker paths.
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

    await sleep(3000);
    // Prefer clicking dashboard in the originally reported page to avoid
    // popup-tab races that are more pronounced in container timing.
    const clickedPage =
      (await runRoutineDashboardTask(() => page)) ||
      (await runRoutineDashboardTask(() => activePage));
    await sleep(15000);

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
