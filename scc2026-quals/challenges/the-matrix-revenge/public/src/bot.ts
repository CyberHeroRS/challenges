import { getAdminToken } from "./utils";

let browser: any = null;
const BOT_ORIGIN = "https://dfd1-79-175-78-107.ngrok-free.app/"; //process.env.BOT_ORIGIN + ":" + process.env.PORT || `https://localhost:${process.env.PORT}`;
const BOT_FLAG_COOKIE_VALUE =
  process.env.FLAG || "SCC{lol}";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Casual daily check :))
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

    const isHttps = BOT_ORIGIN.startsWith("https://");
    await page.setCookie({
      name: "flag",
      value: BOT_FLAG_COOKIE_VALUE,
      url: BOT_ORIGIN,
      path: "/",
      httpOnly: false,
      secure: isHttps,
      sameSite: isHttps ? "None" : "Lax",
    });

    await page.goto(targetUrl, { waitUntil: "networkidle2", timeout: 15000 });

    await sleep(3000);

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
