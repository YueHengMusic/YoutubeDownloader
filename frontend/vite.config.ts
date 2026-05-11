﻿import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "node:path";

// 这个配置文件同时服务于两种场景：
// 1) 开发模式：Electron 加载 http://127.0.0.1:5173
// 2) 生产/回退模式：Electron 通过 file:// 加载 frontend/dist/index.html
// base: "./" 是关键，它会让构建后的资源路径从绝对路径 /assets/... 变成相对路径 ./assets/...
// 这样在 file:// 场景就不会再出现 ERR_FILE_NOT_FOUND 导致白屏。
export default defineConfig({
  root: path.resolve(__dirname),
  base: "./",
  plugins: [vue()],
  server: {
    port: 5173,
    host: "127.0.0.1"
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src")
    }
  }
});
