import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import inlineSource from "vite-plugin-inline-source";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), inlineSource()],
  server: {
    hmr: false, // Disabled, because we're routing through nginx, so HMR doesn't work anyways

    // For testing outside of docker
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
    allowedHosts: true,
    cors: true,
  },
});
