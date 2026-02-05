const express = require('express');
const router = express.Router();
const axios = require('axios');

router.get('/', async (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});
router.post('/search', (req, res) => {
  const query = req.body.query;

  const results = [`Result for "${query}"`];
  res.render('search', { results });
});


router.post('/report', async (req, res) => {

  const { url } = req.body;
  console.log(req.body);
  if (!url) return res.status(400).send('URL is required.');


  try {
    console.log(`Reporting URL: ${url}`);
    await axios.post('http://web-cross-bot:4000/visit', { url }, {
      headers: { 'Content-Type': 'application/json' }
    });
    res.send('URL reported successfully.');
  } catch (error) {
    console.error('Error reporting URL:', error.message);
    let e = error.message;
    res.status(500).send(`Error reporting URL. ${error.message}`);
  }
});

module.exports = router;
