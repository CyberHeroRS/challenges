const express = require('express');
const router = express.Router();
const User = require('../utils/user');
const Post = require('../utils/post');
const path = require('path');
const fs = require('fs');

const handleResponse = (req, res, next) => {
    res.sendResponse = (data) => {
        if (req.method === 'DELETE' || req.is('json')) {
            return res.json(data);
        }

        if (data.redirect) {
            return res.redirect(data.redirect);
        } else if (data.error) {
            return res.render('error', {
                title: 'Error - Doomer',
                error: data.error
            });
        } else if (data.view) {
            return res.render(data.view, {
                title: data.title || 'Doomer',
                ...data.viewData
            });
        } else {
            return res.render('error', {
                title: 'Error - Doomer',
                error: 'An unexpected error occurred'
            });
        }
    };
    next();
};

const isOwnProfile = (req, res, next) => {
    res.locals.isOwnProfile = req.session.user && req.params.username === req.session.user.username;
    next();
};

const requireProfileOwner = (req, res, next) => {
    if (!req.session.user || req.session.user.username !== req.params.username) {
        return res.status(403).sendResponse({ error: 'Unauthorized' });
    }
    next();
};

const validateGif = (gifName) => {
    return /^[a-zA-Z0-9\.\/\$%\^&\*,\-_?=:]+$/.test(gifName);


};

router.use(handleResponse);

router.get('/@:username', isOwnProfile, async (req, res) => {
    try {
        const user = await User.findByUsername(req.params.username);
        if (!user) {
            return res.status(404).sendResponse({
                error: 'User not found'
            });
        }

        const posts = await Post.findByUsername(req.params.username);
        res.sendResponse({
            view: 'profile',
            title: `${user.username} - Doomer`,
            viewData: {
                profileUser: user.toJSON(),
                posts: posts.map(post => post.toJSON()),
                req: req
            }
        });
    } catch (error) {
        console.error('Profile error:', error);
        res.status(500).sendResponse({
            error: 'An error occurred while loading the profile'
        });
    }
});

router.post('/@:username/post', requireProfileOwner, async (req, res) => {
    try {
        const existingPosts = await Post.findByUsername(req.params.username);
        if (existingPosts.length >= 1) {
            return res.status(400).sendResponse({
                error: 'Free trial users are limited to 1 post'
            });
        }

        const { content, gifUrl } = req.body;
        if (!content || content.trim().length === 0) {
            return res.status(400).sendResponse({
                error: 'Post content cannot be empty'
            });
        }

        if (content.length > 1500) {
            return res.status(400).sendResponse({
                error: 'Post content cannot exceed 1500 characters'
            });
        }

        let embed = null;
        if (gifUrl) {
            try {
                const gifName = gifUrl.split('.gif')[0];
                
                if (validateGif(gifName)) {
                    embed = `<img src="/gifs/${gifName}.gif" loading="lazy" width="300" height="200"></img>`;
                } else {
                    return res.status(400).sendResponse({
                        error: 'Invalid GIF selection'
                    });
                }
            } catch (error) {
                console.error('GIF validation error:', error);
                return res.status(400).sendResponse({
                    error: 'Invalid GIF selection'
                });
            }
        }

        const post = await Post.create(req.session.user.id, content.trim(), embed);
        res.sendResponse({
            redirect: `/users/@${req.params.username}`,
            post: post.toJSON()
        });
    } catch (error) {
        console.error('Post creation error:', error);
        if (req.is('json')) {
            return res.status(500).json({ error: 'An error occurred while creating the post' });
        }
        res.status(500).sendResponse({
            error: 'An error occurred while creating the post'
        });
    }
});

router.delete('/@:username/post/:postId', requireProfileOwner, async (req, res) => {
    try {
        const post = await Post.findById(req.params.postId);
        
        if (!post) {
            return res.status(404).json({ error: 'Post not found' });
        }

        if (post.user_id !== req.session.user.id) {
            return res.status(403).json({ error: 'Unauthorized' });
        }

        await Post.delete(req.params.postId);
        res.json({ message: 'Post deleted successfully' });
    } catch (error) {
        console.error('Post deletion error:', error);
        res.status(500).json({ error: 'An error occurred while deleting the post' });
    }
});

module.exports = router; 