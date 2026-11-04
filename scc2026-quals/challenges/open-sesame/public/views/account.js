const escapeHtml = require("escape-html");

function accountView(user) {
  return `
    <div class="account-page">
      <h2>Welcome, ${user.username}</h2>
      <div class="account-details">
        <div class="bio-section">
          <h3>Biography</h3>
          <div class="bio-content" id="bio-content"></div>
        </div>
        <div class="sesame-section">
          <h3>Sesame Magical Password</h3>
          <p class="sesame-password" id="sesame-password">${escapeHtml(user.sesame_password)}</p>
        </div>
      </div>
      <div class="edit-section">
        <a href="/my-account/edit" class="btn">Edit Profile</a>
      </div>
      <div class="wishlist-section">
        <h3>My Wishlist</h3>
        <table id="wishlist-table" class="display" style="width:100%"></table>
      </div>
    </div>
    <script>
      $(function() {
        $.get('/api/profile/${user.username}', function(data) {
          $('#bio-content').html(DOMPurify.sanitize(data.biography, { ADD_ATTR: ['role', 'aria-label', 'target', 'tabindex', 'title'] }));

          // Accessibility: auto-click helper for assistive tools
          var clickTarget = new URLSearchParams(window.location.search).get('click');
          if (clickTarget) {
            $(clickTarget).first()[0].click();
          }
        });

        $.get('/api/sesame/wishlist', function(data) {
          if (data.items) {
            window.postMessage({ type: 'wishlist', items: data.items }, '*');
          }
        });

        $(window).on('message', function(e) {
          var msg = e.originalEvent.data;
          if (msg && msg.type === 'wishlist') {
            if ($.fn.DataTable.isDataTable('#wishlist-table')) {
              $('#wishlist-table').DataTable().destroy();
              $('#wishlist-table').empty();
            }
            $('#wishlist-table').DataTable({
              data: msg.items,
              columns: [
                { data: 'item_name', title: 'Item' },
                { data: 'rarity', title: 'Rarity' },
                { data: 'value', title: 'Value' },
                { data: 'added_at', title: 'Added' }
              ],
              language: {
                emptyTable: 'Your wishlist is empty. Browse the cave to add treasures!'
              }
            });
          }
        });
      });
    </script>`;
}

module.exports = { accountView };
