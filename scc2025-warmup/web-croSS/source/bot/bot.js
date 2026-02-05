const express = require('express');
const puppeteer = require('puppeteer');

const flag = process.env.FLAG || "SCC{Dummy_fl4g}"

const app = express();
app.use(express.json());

app.post('/visit', async (req, res) => {
  const { url } = req.body;
  if (!url) {
    return res.status(400).send('URL is required.');
  }

  try {
    const browser = await puppeteer.launch({
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      headless: true,
    });

    const page = await browser.newPage();
    await page.setCookie({
      name: 'flag',
      value: flag,
      domain: '.ctf.rs',
    });
    await page.goto(url, { waitUntil: 'networkidle2' });
    await browser.close();
    res.send('URL visited by admin.');
  } catch (error) {
    console.log(error)
    res.status(500).send('Error visiting URL.');
  }
});

app.get('/', async (req, res) => {
  return res.status(200).send('Report bot')
})

app.listen(4000, () => {
  console.log('Admin bot is running on http://localhost:4000');
});
