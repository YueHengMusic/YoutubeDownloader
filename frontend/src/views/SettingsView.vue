<template>
  <section>
    <h1>设置</h1>
    <p>后端地址：{{ backendUrl }}</p>
    <p>并发下载：2-3（当前由后端配置）</p>

    <hr />
    <h2>yt-dlp 自动更新</h2>
    <p>已安装版本：{{ store.ytDlpStatus?.installed_version || "未安装" }}</p>
    <p>最新版本：{{ store.ytDlpStatus?.latest_version || "-" }}</p>
    <p>需要更新：{{ store.ytDlpStatus?.has_update ? "是" : "否" }}</p>
    <p>本地路径：{{ store.ytDlpStatus?.binary_path || "-" }}</p>
    <div class="row">
      <button @click="checkYtDlp">检查更新</button>
      <button @click="updateYtDlp">下载/更新 yt-dlp</button>
    </div>

    <hr />
    <h2>ffmpeg 自动更新</h2>
    <p>已安装版本：{{ store.ffmpegStatus?.installed_version || "未安装" }}</p>
    <p>最新发布ID：{{ store.ffmpegStatus?.latest_release_id ?? "-" }}</p>
    <p>最新发布时间：{{ store.ffmpegStatus?.latest_published_at || "-" }}</p>
    <p>本地发布ID：{{ store.ffmpegStatus?.local_release_id ?? "未知" }}</p>
    <p>需要更新：{{ store.ffmpegStatus?.has_update ? "是" : "否" }}</p>
    <p>本地路径：{{ store.ffmpegStatus?.binary_path || "-" }}</p>
    <div class="row">
      <button @click="checkFfmpeg">检查更新</button>
      <button @click="updateFfmpeg">下载/更新 ffmpeg</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "@/stores/tasks";

// 设置页用于展示“依赖组件可用性”和“一键更新”能力。
const backendUrl = "http://127.0.0.1:8000";
const store = useTaskStore();

onMounted(async () => {
  // 页面加载时同步拉取两个依赖的状态，用户打开就能看见结果。
  await store.refreshYtDlpStatus();
  await store.refreshFfmpegStatus();
});

async function checkYtDlp() {
  await store.refreshYtDlpStatus();
}

async function updateYtDlp() {
  await store.updateYtDlp();
}

async function checkFfmpeg() {
  await store.refreshFfmpegStatus();
}

async function updateFfmpeg() {
  await store.updateFfmpeg();
}
</script>

<style scoped>
.row { display: flex; gap: 8px; }
button { padding: 8px 12px; }
</style>
