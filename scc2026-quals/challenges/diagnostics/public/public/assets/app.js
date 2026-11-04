(function () {
  const STORAGE_KEY = "FLAG_PART_F_B64";
  const STORAGE_VAL = "cHQ2e0JSMFc1M1I1X30=";
  const BOOT_TAG = "hun7_";

  function setSeed() {
    try {
      if (!window.localStorage.getItem(STORAGE_KEY)) {
        window.localStorage.setItem(STORAGE_KEY, STORAGE_VAL);
      }
      if (!window.localStorage.getItem("FLAG_PART_F_HINT")) {
        window.localStorage.setItem("FLAG_PART_F_HINT", "decode FLAG_PART_F_B64");
      }
    } catch {
      // ignore storage failures
    }
  }

  async function runSweep() {
    const out = document.getElementById("out");
    if (!out) return;
    out.textContent = "sweeping node channels...\n";

    try {
      const response = await fetch("/api/pulse", { credentials: "same-origin" });
      if (!response.ok) {
        out.textContent += "relay pulse failed.\n";
        return;
      }
      await response.json();
      out.textContent += "sweep complete.\n";
    } catch {
      out.textContent += "network exception during sweep.\n";
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    setSeed();
    // eslint-disable-next-line no-console
    console.log(`FLAG_PART_C=pt3{${BOOT_TAG}}`);

    const btn = document.getElementById("sync-btn");
    if (btn) {
      btn.addEventListener("click", runSweep);
    }

    // Hit /api/pulse on initial page load too.
    void runSweep();
  });
})();
