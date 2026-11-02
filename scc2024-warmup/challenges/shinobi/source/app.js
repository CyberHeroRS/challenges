const express = require('express');
const path = require('path');

const app = express();
const port = 3000;


app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

app.set('view engine', 'ejs');

app.get('/super', (req, res) => {
    res.render('login', { error: null });
});

app.post('/super', (req, res) => {
    const { mail, pass } = req.body;
    if (mail === 'admin@shinobi.video' && pass === 'admin') {
        res.render('dashboard', { flag: process.env.FLAG });
    } else {
        res.render('login', { error: 'Please check your login credentials.' });
    }
});

app.get('*', (req, res) => {
    res.redirect('/super');
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}:`)
});
