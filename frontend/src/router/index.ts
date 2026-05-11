import { createRouter, createWebHashHistory } from "vue-router";
import DownloadView from "@/views/DownloadView.vue";
import QueueView from "@/views/QueueView.vue";
import HistoryView from "@/views/HistoryView.vue";
import LogsView from "@/views/LogsView.vue";
import SettingsView from "@/views/SettingsView.vue";
import AboutView from "@/views/AboutView.vue";

// 使用 Hash 路由是为了兼容 Electron 的 file:// 加载模式，
// 避免刷新页面时向后端发起不存在的路径请求。
export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", redirect: "/download" },
    { path: "/download", component: DownloadView },
    { path: "/queue", component: QueueView },
    { path: "/history", component: HistoryView },
    { path: "/logs", component: LogsView },
    { path: "/settings", component: SettingsView },
    { path: "/about", component: AboutView }
  ]
});
