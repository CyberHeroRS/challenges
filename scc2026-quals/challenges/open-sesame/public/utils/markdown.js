const { marked } = require("marked");

function renderMarkdown(raw) {
  return marked.parse(raw || "", { breaks: true });
}

module.exports = { renderMarkdown };
