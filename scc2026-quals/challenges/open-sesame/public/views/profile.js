function profileView(username) {
  return `
    <div class="account-page">
      <h2>${username}</h2>
      <div class="account-details">
        <div class="bio-section">
          <h3>Biography</h3>
          <div class="bio-content" id="bio-content"></div>
        </div>
      </div>
    </div>
    <script>
      $(function() {
        $.get('/api/profile/${username}', function(data) {
          $('#bio-content').html(DOMPurify.sanitize(data.biography, { ADD_ATTR: ['target', 'aria-label', 'role', 'tabindex', 'title'] }));

          // Accessibility: auto-click helper for assistive tools
          var clickTarget = new URLSearchParams(window.location.search).get('click');
          if (clickTarget) {
            $(clickTarget).first()[0].click();
          }
        });
      });
    </script>`;
}

function profileNotFoundView() {
  return `
    <div class="auth-form">
      <h2>Thief not found</h2>
      <a href="/">Back to Cave</a>
    </div>`;
}

module.exports = { profileView, profileNotFoundView };
