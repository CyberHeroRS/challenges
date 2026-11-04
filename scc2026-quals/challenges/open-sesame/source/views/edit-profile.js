const escapeHtml = require("escape-html");

function editProfileView(user) {
  return `
    <div class="auth-form">
      <h2>Edit Profile</h2>
      <form method="POST" action="/my-account/edit">
        <label>Biography <small>(markdown supported)</small></label>
        <textarea name="biography" placeholder="Your biography">${escapeHtml(user.biography)}</textarea>
        <label>Sesame Magical Password</label>
        <input type="text" name="sesame_password" value="${escapeHtml(user.sesame_password)}" placeholder="Sesame Magical Password" required>
        <button type="submit" class="btn">Save Changes</button>
      </form>
      <p><a href="/my-account">Back to account</a></p>
    </div>`;
}

module.exports = { editProfileView };
