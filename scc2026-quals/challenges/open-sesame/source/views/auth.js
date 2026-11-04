function loginView() {
  return `
    <div class="auth-form">
      <h2>Enter the Cave</h2>
      <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit" class="btn">Enter</button>
      </form>
      <p>No account? <a href="/register">Register here</a></p>
    </div>`;
}

function loginErrorView() {
  return `
    <div class="auth-form">
      <h2>Invalid credentials</h2>
      <a href="/login">Try again</a>
    </div>`;
}

function registerView() {
  return `
    <div class="auth-form">
      <h2>Join the Forty Thieves</h2>
      <form method="POST" action="/register">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <textarea name="biography" placeholder="Your biography (markdown supported)"></textarea>
        <input type="text" name="sesame_password" placeholder="Sesame Magical Password" required>
        <button type="submit" class="btn">Join</button>
      </form>
      <p>Already a thief? <a href="/login">Login here</a></p>
    </div>`;
}

function registerErrorView() {
  return `
    <div class="auth-form">
      <h2>Username already taken</h2>
      <a href="/register">Try again</a>
    </div>`;
}

module.exports = { loginView, loginErrorView, registerView, registerErrorView };
