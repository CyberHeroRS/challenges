const express = require('express');
const path = require('path');


const app = express();
const port = 1312;
const flag = process.env.FLAG || 'SCC{DUMMY_FLAG}';

app.use(express.json());

app.get('*', async (req, res) => {
    res.sendFile(path.join(__dirname, '../views', 'index.html'));
});

app.post("/", async (req, res) => {
    try {
        const { num } = req.body; 

        if (num && num.length === 5) {
            const i = parseInt(num, 10);
            if (i === 767879) {
                return res.status(200).send(`Congratulations! ${flag}`);
            }
            return res.status(200).send("Cheers!");
        }

        if (num && num.length > 5) {
            return res.status(200).send("Long");
        }

        return res.status(200).send("Nope");
    } catch (error) {
        return res.status(500).send("Invalid JSON");
    }
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
