const { resolve } = require("node:path");
const { defineConfig } = require("vite");

module.exports = defineConfig(({ mode }) => ({
  build: {
    outDir: resolve(__dirname, "../static/dist"),
    emptyOutDir: true,
    sourcemap: mode !== "production",
    rollupOptions: {
      input: {
        app: resolve(__dirname, "src/styles/app.css"),
        core: resolve(__dirname, "src/js/core.js"),
        portal: resolve(__dirname, "src/js/portal.js"),
        admin_list: resolve(__dirname, "src/js/admin_list.js"),
        admin_edit: resolve(__dirname, "src/js/admin_edit.js"),
        print: resolve(__dirname, "src/js/print.js"),
      },
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith(".css")) return "[name][extname]";
          return "assets/[name]-[hash][extname]";
        },
      },
    },
  },
}));

