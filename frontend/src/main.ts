import { createApp } from "vue";
import { createPinia } from "pinia";
import { router } from "@/router";
import App from "@/App.vue";

// 前端入口：
// 1) 注册 Pinia（全局状态）
// 2) 注册 Router（页面路由）
// 3) 把根组件挂载到 #app
const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");
