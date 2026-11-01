const puppeteer = require('puppeteer');
const origin = process.env.DOMAIN || "http://localhost:7777";

const browser_options = {
    headless: true,
    ignoreHTTPSErrors: true,
    args: [
        "--no-sandbox",
        "--ignore-certificate-errors",
        "--disable-web-security",
    ],
    executablePath: "/usr/bin/chromium-browser"
};

function isSameOrigin(url) {
    const urlObj = new URL(url);
    const originObj = new URL(origin);
    return urlObj.origin === originObj.origin;
}

async function openURL(url) {
    console.log(url)
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        console.log('URL must start with http:// or https://');
        return;
    }

    if (!isSameOrigin(url, origin)) {
        console.log('URL does not fall within the same origin.');
        return;
    }

    const browser = await puppeteer.launch( browser_options );

    try {
        let page = await browser.newPage();

        await page.setCookie({
            name: 'flag',
            value: process.env.FLAG || 'SCC{Th1s_W4s_T00_l000ng_S0rry_AAAAAAAAAA!}',
            domain: new URL(origin).hostname,
            path: '/',
            httpOnly: false,
        });

        await page.goto(url, {
            waitUntil: 'networkidle2',
            timeout: 5000,
        });
        await browser.close();

        console.log(`Successfully opened ${url}`);
    } catch (error) {
        console.error('Error:', error);
        await browser.close();
    }
}

module.exports.openURL = openURL;
