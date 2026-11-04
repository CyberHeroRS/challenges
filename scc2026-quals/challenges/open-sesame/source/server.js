const express = require("express");
const cookieParser = require("cookie-parser");
const path = require("path");
const { PORT } = require("./config");
const pageRoutes = require("./routes/pages");
const apiRoutes = require("./routes/api");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "static")));

app.use((req, res, next) => {
  res.setHeader("Cross-Origin-Opener-Policy", "same-origin-allow-popups");
  res.setHeader("X-Frame-Options", "DENY");
  next();
});

app.use("/", pageRoutes);
app.use("/api", apiRoutes);

app.listen(PORT, () => console.log(`Open Sesame running on port ${PORT}`));
