import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "dist",
    assetsDir: "assets",
  },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/airflow": "http://localhost:8080",
    },
  },
});
