<template>
  <section>
    <h1>创建下载任务</h1>
    <form @submit.prevent="submit">
      <label>视频链接</label>
      <input v-model="url" required />

      <label>输出目录</label>
      <div class="row">
        <input v-model="outputDir" required />
        <button type="button" @click="pickDir">选择</button>
      </div>

      <label>格式ID（可选）</label>
      <input v-model="formatId" placeholder="bestvideo+bestaudio" />

      <label>分辨率（可选）</label>
      <input v-model="resolution" placeholder="1080" />

      <label>Cookie 模式</label>
      <select v-model="cookieMode">
        <option value="none">不使用</option>
        <option value="file">导入 cookies.txt</option>
        <option value="browser">浏览器读取</option>
      </select>

      <div v-if="cookieMode === 'file'" class="row">
        <input v-model="cookieValue" placeholder="cookies.txt 路径" />
        <button type="button" @click="pickCookie">选择文件</button>
      </div>

      <div v-if="cookieMode === 'browser'">
        <input v-model="cookieValue" placeholder="chrome 或 edge" />
      </div>

      <button type="submit">添加任务</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useTaskStore } from "@/stores/tasks";

// 这个页面的表单状态（每个输入框都对应一个响应式变量）。
const store = useTaskStore();
const url = ref("");
const outputDir = ref(".");
const formatId = ref("");
const resolution = ref("");
const cookieMode = ref<"none" | "file" | "browser">("none");
const cookieValue = ref("");

async function pickDir() {
  // 前端不能直接访问本地文件系统，所以通过 preload 暴露的方法来选目录。
  const path = await window.desktopAPI?.pickDirectory?.();
  if (path) outputDir.value = path;
}

async function pickCookie() {
  // 选中文件后，立即请求后端校验 cookies.txt 格式，提前发现问题。
  const path = await window.desktopAPI?.pickCookieFile?.();
  if (path) {
    cookieValue.value = path;
    await store.importCookie(path);
  }
}

async function submit() {
  // 组装创建任务请求：可选字段为空时用 undefined，后端会按“未填写”处理。
  await store.createTask({
    url: url.value,
    output_dir: outputDir.value,
    format_id: formatId.value || undefined,
    resolution: resolution.value || undefined,
    cookie_mode: cookieMode.value,
    cookie_value: cookieValue.value || undefined
  });
  url.value = "";
}
</script>

<style scoped>
form { display: flex; flex-direction: column; gap: 10px; max-width: 680px; }
.row { display: flex; gap: 8px; }
input, select, button { padding: 8px; }
</style>
