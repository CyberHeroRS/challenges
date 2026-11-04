const escapeHtml = require("escape-html");

function renderPage(title, content, user = null) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)} - Open Sesame</title>
  <link rel="stylesheet" href="/style.css">
  <link rel="stylesheet" href="https://cdn.datatables.net/2.2.2/css/dataTables.dataTables.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.2.7/purify.min.js"></script>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/2.2.2/js/dataTables.min.js"></script>
</head>
<body>
  <nav class="cave-nav">
    <a href="/" class="nav-brand">Open Sesame</a>
    <div class="nav-links">
      <a href="/">Cave</a>
      ${user ? `
        <a href="/my-account">My Account</a>
        <a href="/report">Report</a>
        <a href="/logout">Logout</a>
      ` : `
        <a href="/login">Login</a>
        <a href="/register">Register</a>
      `}
    </div>
  </nav>
  <main class="container">${content}</main>
</body>
</html>`;
}

module.exports = { renderPage };
