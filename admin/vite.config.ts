import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import tailwindcss from "@tailwindcss/vite";
import { exec } from "child_process";

let p = path.join(__dirname, "./public/static-server.cjs");

if (process.env.npm_lifecycle_event == "dev") {
  exec(`node ${p}`);
}
// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    chunkSizeWarningLimit: 20000,
  },
  base: "./",
  server: {
    port: 8001,
  },
  // preview: {
  //   port: 8001, // 指定预览模式的端口号
  // },
});
