function reportFormView() {
  return `
    <div class="auth-form">
      <h2>Report to the Captain</h2>
      <p>Found something interesting? Send a page for the captain to review.</p>
      <form method="POST" action="/api/report">
        <input type="url" name="url" placeholder="URL for the captain to visit" required>
        <button type="submit" class="btn">Send Report</button>
      </form>
    </div>`;
}

function reportSentView() {
  return `
    <div class="auth-form">
      <h2>Report Sent</h2>
      <p>The captain will review your report shortly.</p>
      <a href="/" class="btn">Back to Cave</a>
    </div>`;
}

module.exports = { reportFormView, reportSentView };
