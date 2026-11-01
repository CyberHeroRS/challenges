const express = require('express');
const router = express.Router();

router.get("/", (req, res) => {
    res.render('index', {
        title: 'Doomer',
        posts: [
            {
                id: 1,
                username: "anxiety_queen",
                content: "Just spent 5 hours scrolling... help",
                likes: 2453
            },
            {
                id: 2,
                username: "midnight_scroller",
                content: "Can't sleep, might as well keep scrolling..",
                likes: 1897
            },
            {
                id: 3,
                username: "doom_enthusiast",
                content: "Another day, another endless scroll 🌀",
                likes: 3211
            },
            {
                id: 4,
                username: "digital_void",
                content: "The algorithm knows me better than I know myself 👁️",
                likes: 4521
            },
            {
                id: 5,
                username: "scroll_walker",
                content: "Lost in the infinite feed, send help 📱",
                likes: 2876
            }
        ]
    });
});

router.post("/api/report", async (req, res) => {
    const { url } = req.body;

    if (!url || typeof url !== 'string') {
        return res.status(400).json({ error: 'Invalid URL' });
    }

    try {
        const response = await fetch('http://bot:3000/report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        return res.json(data);
    } catch (error) {
        console.error('Error submitting report:', error);
        return res.status(500).json({ error: 'Failed to submit report' });
    }
});

module.exports = router; 