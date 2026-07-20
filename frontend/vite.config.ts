import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
  },
  // Base path: repo name for production GH Pages, root for dev.
  // Change to '/' if using a custom domain.
  base: command === "build" ? "/beijing-news-pipeline/" : "/",
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/airflow": {
        target: "http://localhost:8080",
        rewrite: (path) => path.replace(/^\/airflow/, ""),
      },
    },
  },
}));
