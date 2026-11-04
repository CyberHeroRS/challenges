## Matrix Underground Forum Challenge

This is a small, self-contained web challenge themed around an underground Matrix-style forum.

### Structure

- **index.html**: Main page with the forum layout and challenge description hints.
- **assets/style.css**: Matrix-style visuals and layout (dark theme, green glow, glitchy accents).
- **assets/app.js**: Frontend logic for:
  - Fake "authentication" state (no visible registration).
  - Rendering thread list and locked post content for non-logged-in users.
  - Fake ads with close buttons (for your generated images later).

### Running Locally

You can serve the files with any static HTTP server. For convenience:

```bash
npm install
npm run dev
```

This uses `npx serve .` to host the current directory on a local port.

### Next Steps

- Add your generated images for:
  - Forum logo/banner.
  - User avatars.
  - Ad slots (`ad-1`, `ad-2`, etc.).
- Implement the actual "bypass" to get a logged-in state (e.g., subtle JS bug, hidden input, URL trick, etc.).
- Add more threads, replies, and in-universe flavor text.

