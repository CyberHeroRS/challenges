function homeView(items, user) {
  return `
    <div class="hero">
      <h1>The Cave of Wonders</h1>
      <p class="subtitle">Treasures beyond your wildest dreams await within...</p>
    </div>
    <div class="catalogue">
      ${items.map(item => `
        <div class="treasure-card">
          <div class="treasure-img">
            <img src="/img/${item.image}.svg" alt="${item.name}">
          </div>
          <div class="treasure-info">
            <h3>${item.name}</h3>
            <p>${item.description}</p>
            <span class="rarity rarity-${item.rarity.toLowerCase()}">${item.rarity}</span>
            <span class="value">${item.value}</span>
            ${user ? `<button class="btn btn-wish" data-item-id="${item.id}">Add to Wishlist</button>` : ""}
          </div>
        </div>
      `).join("")}
    </div>
    ${user ? `<script>
      $(function() {
        $('.btn-wish').on('click', function() {
          var btn = $(this);
          $.ajax({
            url: '/api/sesame/wishlist',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ item_id: btn.data('item-id') }),
            success: function(data) {
              if (data.success) alert('Added to your wishlist!');
              else alert(data.error || 'Failed');
            }
          });
        });
      });
    </script>` : ""}`;
}

module.exports = { homeView };
