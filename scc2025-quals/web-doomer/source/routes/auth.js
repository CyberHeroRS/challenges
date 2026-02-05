const express = require('express');
const router = express.Router();
const User = require('../utils/user');
const { validatePassword } = require('../utils/auth');

const checkAuth = (requireAuth, req, res, next) => {
    const isUserAuthenticated = Boolean(req.session.user);
    if (isUserAuthenticated === requireAuth) {
        next();
    } else {
        if (requireAuth) {
            res.redirect(`/login${req.query.redirect ? `?redirect=${encodeURIComponent(req.query.redirect)}` : ''}`);
        } else if (!requireAuth && isUserAuthenticated && req.query.redirect) {
            res.redirect(req.query.redirect);
        } else {
            res.redirect('/');
        }
    }
};

const requireAuth = (req, res, next) => checkAuth(true, req, res, next);
const requireGuest = (req, res, next) => checkAuth(false, req, res, next);

router.get("/login", requireGuest, (req, res) => {
    res.render('login', {
        title: 'Login - Doomer',
        error: null,
        redirect: req.query.redirect || null
    });
});

router.post("/login", requireGuest, async (req, res) => {
    try {
        const { username, password, redirect } = req.body;
        const user = await User.findByUsername(username);

        if (!user) {
            return res.render('login', {
                title: 'Login - Doomer',
                error: 'Invalid username or password',
                redirect: redirect || null
            });
        }

        const validPassword = await validatePassword(password, user.password);

        if (!validPassword) {
            return res.render('login', {
                title: 'Login - Doomer',
                error: 'Invalid username or password',
                redirect: redirect || null
            });
        }

        req.session.user = user.toJSON();
        res.redirect(redirect || '/');
    } catch (error) {
        console.error('Login error:', error);
        res.render('login', {
            title: 'Login - Doomer',
            error: 'An error occurred during login',
            redirect: req.body.redirect || null
        });
    }
});

router.get("/register", requireGuest, (req, res) => {
    res.render('register', {
        title: 'Register - Doomer',
        error: null
    });
});

router.post("/register", requireGuest, async (req, res) => {
    try {
        const { username, email, password, confirm_password } = req.body;
        
        if (!username || username.length > 12 || !/^[a-zA-Z0-9_]+$/.test(username)) {
            return res.render('register', {
                title: 'Register - Doomer',
                error: 'Username must be 1-12 characters long and contain only letters, numbers, and underscores'
            });
        }

        if (password !== confirm_password) {
            return res.render('register', {
                title: 'Register - Doomer',
                error: 'Passwords do not match'
            });
        }

        const userExists = await User.checkExisting(username, email);
        if (userExists) {
            return res.render('register', {
                title: 'Register - Doomer',
                error: 'Username or email already exists'
            });
        }

        const user = await User.create({ username, email, password });
        req.session.user = user.toJSON();
        res.redirect('/');
    } catch (error) {
        console.error('Registration error:', error);
        res.render('register', {
            title: 'Register - Doomer',
            error: 'An error occurred during registration'
        });
    }
});

router.get("/logout", requireAuth, (req, res) => {
    req.session.destroy();
    res.redirect("/");
});

module.exports = router; 