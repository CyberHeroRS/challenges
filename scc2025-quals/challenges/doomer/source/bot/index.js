const express = require('express');
const puppeteer = require('puppeteer');

const app = express();
app.use(express.json());

const APP_URL = process.env.APP_URL || 'http://web:1337';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;

const VALID_ORIGIN = new URL(APP_URL);

function isValidUrl(urlString) {
    try {
        const url = new URL(urlString);
        return url.hostname === VALID_ORIGIN.hostname && 
               url.port === VALID_ORIGIN.port &&
               url.protocol === VALID_ORIGIN.protocol;
    } catch {
        return false;
    }
}

async function createBrowser() {
    console.log('[*] Creating new browser instance...');
    return await puppeteer.launch({
        headless: true,
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080'
        ],
        defaultViewport: {
            width: 1920,
            height: 1080
        }
    });
}

async function visitPage(url) {
    const browser = await createBrowser();
    const page = await browser.newPage();
    
    try {
        console.log('[*] Logging in as admin...');
        await page.goto(`${APP_URL}/login`, {
            waitUntil: ['networkidle0', 'domcontentloaded'],
            timeout: 30000
        });

        await page.waitForSelector('form', { timeout: 30000 });
        
        await page.evaluate((username, password) => {
            const usernameInput = document.querySelector('input[name="username"]');
            const passwordInput = document.querySelector('input[name="password"]');
            
            if (!usernameInput || !passwordInput) {
                throw new Error('Could not find login form inputs');
            }
            
            usernameInput.value = username;
            passwordInput.value = password;
        }, 'doomer_admin', ADMIN_PASSWORD);
        
        await Promise.all([
            page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 30000 }),
            page.evaluate(() => {
                const submitButton = document.querySelector('button[type="submit"]');
                if (!submitButton) {
                    throw new Error('Could not find submit button');
                }
                submitButton.click();
            })
        ]);

        console.log('[+] Authentication successful');

        if (isValidUrl(url)) {
            console.log(`[*] Visiting URL: ${url}`);
            await page.goto(url, { 
                waitUntil: 'networkidle0',
                timeout: 30000
            });
            console.log('[+] Visit completed');
        }
    } catch (error) {
        console.error('[-] Error during page visit:', error);
        throw error;
    } finally {
        await page.close();
        await browser.close();
    }
}

app.post('/report', async (req, res) => {
    const { url } = req.body;
    
    if (!url || typeof url !== 'string') {
        return res.status(400).json({ error: 'Invalid URL' });
    }

    if (!isValidUrl(url)) {
        return res.status(400).json({ error: 'Invalid URL. Must be from our website.' });
    }

    try {
        await visitPage(url);
        res.json({ message: 'Report submitted successfully' });
    } catch (error) {
        console.error('[-] Error processing report:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(3000, () => {
    console.log('[*] Bot service listening on port 3000');
}); 