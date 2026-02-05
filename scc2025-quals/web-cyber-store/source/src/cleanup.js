const fs = require("fs");
const path = require("path");

try {
  fs.mkdirSync(path.join(__dirname, "../public/receipts"), { recursive: true });
} catch {}

function cleanUpReceipts() {
  const receiptsDir = path.join(__dirname, "../public/receipts");
  fs.readdir(receiptsDir, (err, files) => {
    if (err) {
      console.error("Error reading receipts directory:", err);
      return;
    }

    const now = Date.now();
    files.forEach((file) => {
      const filePath = path.join(receiptsDir, file);
      fs.stat(filePath, (err, stats) => {
        if (err) {
          console.error("Error getting file stats:", err);
          return;
        }

        const age = now - stats.mtimeMs;
        if (age > 1000 * 60 * 15) {
          fs.unlink(filePath, (err) => {
            if (err) {
              console.error("Error deleting file:", err);
            }
          });
        }
      });
    });
  });
}

setInterval(cleanUpReceipts, 1000 * 60 * 15);
