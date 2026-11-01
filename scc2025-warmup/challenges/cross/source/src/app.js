const express = require('express');
const path = require('path');
const routes = require('./routes');
const app = express();
const PORT = process.env.PORT || 1213;

app.set('view engine', 'pug');
app.set('views', path.join(__dirname, '../views'));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '../views')));

app.use('/', routes);

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
