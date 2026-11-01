const express = require('express');
const cookieParser = require('cookie-parser');
const path = require('path');
const routes = require('./routes');

const app = express();

app.use(express.json());
app.use(cookieParser());

app.use('/api', routes);

app.use(express.static(path.join(__dirname, '../views/build')));

app.get('*', (req, res) => {
    if (!req.path.startsWith('/api')) {
        res.sendFile(path.join(__dirname, '../views/build/index.html'));
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 