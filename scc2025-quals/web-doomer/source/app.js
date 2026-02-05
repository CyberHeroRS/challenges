const express = require("express");
const session = require('express-session');
const { waitForDb, initAdminUser } = require('./utils/db');
const authRoutes = require('./routes/auth');
const indexRoutes = require('./routes/index');
const userRoutes = require('./routes/users');

const app = express();

app.set('view engine', 'ejs');
app.set('views', './views');
app.use(express.static('public'));
app.use('/gifs', express.static('views/gifs'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use(session({
    secret: process.env.SESSION_SECRET || 'your_secret_key_here',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: process.env.NODE_ENV === 'production',
        maxAge: 1000 * 60 * 60 * 24
    }
}));

app.use((req, res, next) => {
    res.locals.user = req.session.user || null;
    next();
});

app.use('/', indexRoutes);
app.use('/', authRoutes);
app.use('/users', userRoutes);

async function main() {
    await waitForDb();
    await initAdminUser();
    
    app.listen(1337, () => {
        console.log("[*] Server is running on port 1337");
    });
}

main().catch(console.error);
