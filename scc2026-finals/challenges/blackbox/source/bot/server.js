const express = require('express');
const { loginAndVisit } = require('./bot');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

// Main endpoint to visit a contact URL
app.post('/visit', (req, res) => {
    const { url } = req.body;
    
    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }
    
    
    console.log(`[*] Received request to visit: ${url}`);
    
    const jobId = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    res.status(202).json({ queued: true, jobId });

    loginAndVisit(url)
        .then(result => {
            console.log(`[+] Job ${jobId} finished:`, result);
        })
        .catch(error => {
            console.error(`[-] Job ${jobId} failed:`, error.message);
        });
});

// Start server
app.listen(PORT, () => {
    console.log(`[*] Admin Bot Server listening on port ${PORT}`);
    console.log(`[*] POST /visit - Visit a contact URL`);
    console.log(`[*] GET /health - Health check`);
});
