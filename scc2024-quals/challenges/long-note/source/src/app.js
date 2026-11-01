const express = require('express');
var path = require('path');
var bot = require('./bot.js');

const app = express();
const PORT = process.env.PORT || 7777;

app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'static')));
app.set('view engine', 'ejs');

app.get('/', (req, res) => {
    res.render('index');
});

app.get('/checkNote', (req, res) => {
    res.render('checkNote');
});

app.post('/checkNote', (req, res) => {
    const noteUrl = req.body.noteUrl;
    bot.openURL(noteUrl);
    res.render("visit.ejs")
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});