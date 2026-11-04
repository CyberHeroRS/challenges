const { v4: uuidv4 } = require("uuid");
const { BASE_URL } = require("../config");
const { captainId } = require("../db");
const { sessions } = require("../middleware/auth");

let browser = null;

async function getBrowser() {
  if (!browser) {
    const puppeteer = require("puppeteer");
    browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
    });
  }
  return browser;
}

async function visitUrl(url) {
  const b = await getBrowser();
  const page = await b.newPage();

  try {
    const captainSid = uuidv4();
    sessions.set(captainSid, { id: captainId, username: "captain" });
    await page.setCookie({
      name: "session",
      value: captainSid,
      domain: new URL(BASE_URL).hostname,
      path: "/",
      httpOnly: true,
    });

    await page.goto(url, { waitUntil: "networkidle0", timeout: 10000 });
    await new Promise((r) => setTimeout(r, 8000));
  } catch (e) {
    console.error("Bot error:", e.message);
  } finally {
    await page.close();
  }
}

module.exports = { visitUrl };
