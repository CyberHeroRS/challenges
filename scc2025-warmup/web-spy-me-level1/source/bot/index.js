const express = require('express');
const puppeteer = require('puppeteer-core');
const mysql = require('mysql2/promise');

const app = express();
app.use(express.json());

const pool = mysql.createPool({
    host: process.env.MYSQL_HOST || 'mysql',
    user: process.env.MYSQL_USER || 'root',
    password: process.env.MYSQL_PASSWORD || 'root',
    database: process.env.MYSQL_DATABASE || 'spyme'
});

let browser = null;

async function initBrowser() {
    if (!browser) {
        browser = await puppeteer.launch({
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
            headless: true,
            defaultViewport: null,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-extensions',
                '--disable-default-apps',
                '--window-size=1024,768'
            ]
        });
    }
    return browser;
}

async function loginAsAdmin(page) {
    try {
        const [rows] = await pool.execute(
            'SELECT username, secret_code FROM users WHERE username = ? AND is_admin = TRUE LIMIT 1',
            ['admin']
        );

        if (rows.length === 0) {
            throw new Error('Admin user not found');
        }

        const { username, secret_code } = rows[0];

        await page.goto('http://web:3000/login', { 
            waitUntil: 'networkidle0', 
            timeout: 10000 
        });

        await page.waitForSelector('input[id^=":r"][type="text"]', { timeout: 5000 });
        const inputs = await page.$$('input[id^=":r"][type="text"]');
        await inputs[0].type(username);
        await inputs[1].type(secret_code);

        const submitButton = await page.waitForSelector('button[type="submit"]');
        await Promise.all([
            page.waitForNavigation({ timeout: 10000 }),
            submitButton.click()
        ]);

        const currentUrl = page.url();
        if (!currentUrl.includes('/agents')) {
            throw new Error('Login failed - not redirected to agents page');
        }

        console.log('Successfully logged in as admin');
    } catch (error) {
        console.error('Login error:', error);
        throw new Error(`Login failed: ${error.message}`);
    }
}

app.post('/visit', async (req, res) => {
    let page = null;
    try {
        const { url } = req.body;
        
        if (!url) {
            return res.status(400).json({ error: 'URL is required' });
        }
        console.log(`Bot visiting URL: ${url}`);

        // Get or create browser instance
        browser = await initBrowser();
        page = await browser.newPage();

        // Login as admin
        await loginAsAdmin(page);


        console.log(`Navigating to: ${url}`);
        await page.goto(url, { 
            waitUntil: 'networkidle0',
            timeout: 15000 
        });

        console.log('Waiting 5 seconds on target page...');
        await page.waitForTimeout(5000);

        res.json({ message: 'URL visited successfully' });
    } catch (error) {
        console.error('Error visiting URL:', error);
        res.status(500).json({ error: 'Failed to visit URL: ' + error.message });
    }
});

// Cleanup on shutdown
process.on('SIGTERM', async () => {
    if (browser) {
        try {
            await browser.close();
        } catch (e) {
            console.error('Error closing browser:', e);
        }
    }
    process.exit(0);
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Bot service listening on port ${PORT}`);
}); 