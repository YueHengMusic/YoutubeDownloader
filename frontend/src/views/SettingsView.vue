<template>
  <section class="section">
    <h2>{{ t("settings_title") }}</h2>
    <p class="desc">{{ t("settings_desc") }}</p>

    <article class="card">
      <h3>{{ t("settings_ytdlp_title") }}</h3>
      <div class="info_list">
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_installed_version") }}</span>
          <span class="info_value">{{ store.ytDlpStatus?.installed_version || t("common_not_installed") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_latest_version") }}</span>
          <span class="info_value">{{ store.ytDlpStatus?.latest_version || t("common_dash") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_need_update") }}</span>
          <span class="info_value">{{ store.ytDlpStatus?.has_update ? t("common_yes") : t("common_no") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_binary_path") }}</span>
          <span class="info_value long">{{ store.ytDlpStatus?.binary_path || t("common_dash") }}</span>
        </div>
      </div>
      <div class="row">
        <button class="btn-secondary" @click="checkYtDlp" :disabled="store.isCheckingYtDlp || store.isUpdatingYtDlp">
          {{ store.isCheckingYtDlp ? t("settings_button_checking") : t("settings_button_check_update") }}
        </button>
        <button class="btn-primary" @click="updateYtDlp" :disabled="store.isUpdatingYtDlp || store.isCheckingYtDlp">
          {{ store.isUpdatingYtDlp ? t("settings_button_updating") : t("settings_button_update_ytdlp") }}
        </button>
      </div>
    </article>

    <article class="card">
      <h3>{{ t("settings_ffmpeg_title") }}</h3>
      <div class="info_list">
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_installed_version") }}</span>
          <span class="info_value">{{ store.ffmpegStatus?.installed_version || t("common_not_installed") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_latest_release_id") }}</span>
          <span class="info_value">{{ store.ffmpegStatus?.latest_release_id ?? t("common_dash") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_latest_published_at") }}</span>
          <span class="info_value">{{ store.ffmpegStatus?.latest_published_at || t("common_dash") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_local_release_id") }}</span>
          <span class="info_value">{{ store.ffmpegStatus?.local_release_id ?? t("common_unknown") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_need_update") }}</span>
          <span class="info_value">{{ store.ffmpegStatus?.has_update ? t("common_yes") : t("common_no") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_binary_path") }}</span>
          <span class="info_value long">{{ store.ffmpegStatus?.binary_path || t("common_dash") }}</span>
        </div>
      </div>
      <div class="row">
        <button class="btn-secondary" @click="checkFfmpeg" :disabled="store.isCheckingFfmpeg || store.isUpdatingFfmpeg">
          {{ store.isCheckingFfmpeg ? t("settings_button_checking") : t("settings_button_check_update") }}
        </button>
        <button class="btn-primary" @click="updateFfmpeg" :disabled="store.isUpdatingFfmpeg || store.isCheckingFfmpeg">
          {{ store.isUpdatingFfmpeg ? t("settings_button_updating") : t("settings_button_update_ffmpeg") }}
        </button>
      </div>
    </article>

    <p class="meta">{{ t("settings_meta", { backendUrl }) }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "@/stores/tasks";
import { t } from "@/i18n/strings";

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
.section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.33;
  font-weight: 600;
  font-family: "SF Pro Rounded", ui-rounded, ui-sans-serif, system-ui, sans-serif;
}

h3 {
  margin: 0;
  font-size: 19px;
  line-height: 1.36;
  font-weight: 600;
}

.desc {
  margin: 0;
  color: var(--body);
  font-size: 14px;
}

.card {
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info_list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info_row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 8px;
  align-items: baseline;
}

.info_key {
  color: var(--body);
  font-size: 13px;
}

.info_value {
  font-size: 14px;
  color: var(--ink);
}

.info_value.long {
  word-break: break-all;
}

.row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  border-radius: 9999px;
  height: 36px;
  padding: 8px 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-primary {
  border: 1px solid var(--primary);
  background: var(--primary);
  color: var(--on-primary);
}

.btn-secondary {
  border: 1px solid var(--hairline-strong);
  background: var(--canvas);
  color: var(--ink);
}

.btn-primary,
.btn-secondary {
  min-width: 132px;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  background: var(--surface-soft);
  border-color: var(--hairline);
  color: var(--mute);
  cursor: not-allowed;
}

.meta {
  margin: 0;
  font-size: 13px;
  color: var(--body);
}

@media (max-width: 760px) {
  .info_row {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
</style>
