window.ThreadBoardPreview = {
  renderDisplayNamePreview(targetId, displayName) {
    const target = document.getElementById(targetId);
    if (!target) {
      return;
    }

    target.innerHTML =
      '<div class="name-preview-card"><span class="label">Profile badge</span><div class="sink">Signed in as ' +
      displayName +
      "</div></div>";
  }
};

