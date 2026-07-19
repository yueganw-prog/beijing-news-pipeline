import { defineConfig } from "vite";

export default defineConfig({
  resolve: {
    alias: {
      // Use the full build that includes the template compiler
      // (required because components use inline `template:` strings)
      vue: "vue/dist/vue.esm-bundler.js",
    },
  },
  define: {
    // Vue feature flags for better tree-shaking
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
  },
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
});
