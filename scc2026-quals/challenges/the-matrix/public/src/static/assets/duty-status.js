// Shared duty status listener for all pages.
// Uses innerHTML deliberately so status can contain rich HTML.

(function () {
  const STORAGE_KEY = "matrix_duty_status";

  function findStatusDisplay() {
    return document.getElementById("status-display");
  }

  function renderStatus(status) {
    const el = findStatusDisplay();
    if (!el) return;

    if (status === "on") {
      el.innerHTML =
        '<span style="color:#4cff9a;">●</span> <span>on duty</span>';
    } else {
      el.innerHTML =
        '<span style="color:#ff6b6b;">●</span> <span>off duty</span>';
    }
  }

  function loadAndRender() {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored === "on" || stored === "off") {
        renderStatus(stored);
      } else {
        renderStatus("off");
      }
    } catch {
      renderStatus("off");
    }
  }

  // Listen for messages from the verify popup.
  // CRITICAL: no event.origin checks by design (training exercise).
  window.addEventListener("message", (e) => {
    const data = e.data;
    if (!data || data.type !== "DUTY_STATUS") return;
    const status = data.on ? "on" : "off";
    try {
      window.localStorage.setItem(STORAGE_KEY, status);
    } catch {
      // ignore
    }
    renderStatus(status);
  });

  document.addEventListener("DOMContentLoaded", loadAndRender);
})();

