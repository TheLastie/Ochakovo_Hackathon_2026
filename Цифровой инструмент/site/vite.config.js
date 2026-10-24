import { defineConfig } from "vite";
export default defineConfig({
  base: "/static/app/",
  build: {
    outDir: "web/dist",
    emptyOutDir: true,
    rollupOptions: {
      input: "web/src/main.ts",
      output: { entryFileNames: "app.js", assetFileNames: "[name][extname]" },
    },
  },
});
