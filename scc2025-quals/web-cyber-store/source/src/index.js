const express = require("express");
const session = require("express-session");
const expressLayouts = require("express-ejs-layouts");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const products = require("../data/products.json");

const wkhtmltopdf = require("wkhtmltopdf");
wkhtmltopdf.shell = "/bin/ash";

require("./cleanup");

const app = express();

app.set("view engine", "ejs");
app.set("views", "./views");
app.use(expressLayouts);
app.set("layout", "layouts/main");
app.use(express.urlencoded({ extended: true }));
app.use(
  session({
    secret: crypto.randomBytes(16).toString("hex"),
    resave: false,
    saveUninitialized: true,
  })
);

app.use((req, res, next) => {
  if (!req.session.cart) {
    req.session.cart = [];
  }
  next();
});

app.get("/", (req, res) => {
  res.render("index");
});

app.get("/products", (req, res) => {
  res.render("products", {
    products: products.products,
    cartCount: req.session.cart.length,
  });
});

app.post("/cart/add", (req, res) => {
  const productId = parseInt(req.body.productId);
  const productName = req.body.productName;

  const product = products.products.find((p) => p.id === productId);
  if (product) {
    req.session.cart.push(Object.assign({}, product, { name: productName }));
  }

  res.redirect("/cart");
});

app.get("/cart", (req, res) => {
  const total = req.session.cart.reduce((sum, item) => sum + item.price, 0);
  res.render("cart", {
    cart: req.session.cart,
    total: total.toFixed(2),
  });
});

app.post("/cart/remove", (req, res) => {
  const index = parseInt(req.body.index);
  req.session.cart.splice(index, 1);
  res.redirect("/cart");
});

app.get("/checkout", (req, res) => {
  const total = req.session.cart.reduce((sum, item) => sum + item.price, 0);
  res.render("checkout", {
    cart: req.session.cart,
    total: total.toFixed(2),
  });
});

app.post("/order", (req, res) => {
  const orderId = crypto.randomBytes(16).toString("hex");
  const orderDetails = {
    name: req.body.name,
    email: req.body.email,
    address: req.body.address,
  };

  const total = req.session.cart
    .reduce((sum, item) => sum + item.price, 0)
    .toFixed(2);

  app.render(
    "receipt-template",
    {
      cart: req.session.cart,
      total: total,
      orderDetails: orderDetails,
      orderId: orderId,
    },
    (err, html) => {
      if (err) {
        console.error(err);
        return res.status(500).send("Error rendering receipt");
      }

      wkhtmltopdf(
        html,
        {
          pageSize: "Letter",
          output: path.join(__dirname, `../public/receipts/${orderId}.pdf`),
          enableJavascript: true,
          enableExternalLinks: true,
          enableLocalFileAccess: true,
          enableForms: true,
          enableInternalLinks: true,
          enableSmartShrinking: true,
          enableTocBackLinks: true,
        },
        (err, result) => {
          if (err) {
            console.error(err);
            return res.status(500).send("Error generating PDF");
          }

          req.session.cart = [];
          res.render("order-complete", { orderId });
        }
      );
    }
  );
});

app.get("/receipt/:orderId", (req, res) => {
  const orderId = req.params.orderId;

  if (!/^[a-f0-9]{32}$/.test(orderId)) {
    return res.status(400).send("Invalid order ID");
  }

  const pdfPath = path.join(__dirname, `../public/receipts/${orderId}.pdf`);

  if (!fs.existsSync(pdfPath)) {
    return res.status(404).send("Receipt not found");
  }

  res.sendFile(pdfPath);
});

app.use((error, req, res, next) => {
  console.error(error.stack);
  res.status(500).send("Oops! Something went wrong.");
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught Exception:", err);
});

app.listen(3000, () => {
  console.log("Server is running on http://localhost:3000");
});
