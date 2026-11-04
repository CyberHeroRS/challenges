const puppeteer = require('puppeteer');

async function loginAndVisit(contactUrl) {
  // Launch Puppeteer
  const browser = await puppeteer.launch({
    headless: true, // change to false if you want to see the browser
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    executablePath: '/usr/bin/chromium'
  });

  try {
    const page = await browser.newPage();

    // Log in as admin
    await page.goto('http://web-app:5000/admin/login', {
      waitUntil: 'networkidle2',
      timeout: 10000
    });

    await page.type('input[name="username"]', 'admin');
    await page.type('input[name="password"]', 'DragonSecSuperSecretPassword!');
    
    // Click + wait for login to complete
    await page.click('button[type="submit"]');
    await page.waitForFunction(
      () => window.location.pathname.startsWith('/admin/contacts') || document.body.innerText.includes('Admin Contacts'),
      { timeout: 30000 }
    );

    // Normalize contact URL to keep the same origin for session cookies
    const loginOrigin = 'http://web-app:5000';
    let normalizedUrl = contactUrl;
    try {
      const parsed = new URL(contactUrl);
      normalizedUrl = `${loginOrigin}${parsed.pathname}`;
      if (parsed.search) {
        normalizedUrl += parsed.search;
      }
    } catch {
      normalizedUrl = contactUrl;
    }

    // Now visit the contact URL from the request
    await page.goto(normalizedUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    // Stay on the page for 15 seconds
    await new Promise(resolve => setTimeout(resolve, 15000));


  } catch (err) {
    console.error(`[-] Error visiting ${contactUrl}:`, err);
  } finally {
    await browser.close(); // always close browser to free resources
  }
}

module.exports = { loginAndVisit };