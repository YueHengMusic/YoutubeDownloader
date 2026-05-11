<template>
  <section class="section">
    <h2>{{ t("settings_title") }}</h2>
    <p class="desc">{{ t("settings_desc") }}</p>

    <article class="card">
      <h3>{{ t("settings_download_title") }}</h3>
      <div class="info_list">
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_download_concurrency") }}</span>
          <span class="info_value">
            <input
              v-model.number="store.downloadConcurrencyInput"
              class="input_number"
              type="number"
              :min="store.appSettings?.min_download_concurrency ?? 1"
              :max="store.appSettings?.max_download_concurrency ?? 20"
            />
          </span>
        </div>
      </div>
      <p class="card_hint">
        {{
          t("settings_download_concurrency_hint", {
            min: store.appSettings?.min_download_concurrency ?? 1,
            max: store.appSettings?.max_download_concurrency ?? 20,
            defaultValue: store.appSettings?.default_download_concurrency ?? 2
          })
        }}
      </p>
      <div class="row">
        <button class="btn-primary" @click="saveSettings" :disabled="store.isSavingAppSettings || store.isRefreshingAppSettings">
          {{ store.isSavingAppSettings ? t("settings_button_saving") : t("settings_button_save") }}
        </button>
      </div>
    </article>

    <article class="card">
      <h3>{{ t("settings_ytdlp_title") }}</h3>
      <div class="info_list">
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_installed_version") }}</span>
          <span class="info_value">
            {{
              store.ytDlpStatus?.installed_version
                || (store.dependencyStatus?.yt_dlp.exists ? t("settings_installed_unchecked") : t("common_not_installed"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_latest_version") }}</span>
          <span class="info_value">{{ store.ytDlpStatus?.latest_version || t("common_dash") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_need_update") }}</span>
          <span class="info_value">
            {{
              store.ytDlpStatus == null
                ? t("common_dash")
                : (store.ytDlpStatus.has_update ? t("common_yes") : t("common_no"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_binary_path") }}</span>
          <span class="info_value long">{{ store.ytDlpStatus?.binary_path || store.dependencyStatus?.yt_dlp.path || t("common_dash") }}</span>
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
          <span class="info_value">
            {{
              store.ffmpegStatus?.installed_version
                || (store.dependencyStatus?.ffmpeg.exists ? t("settings_installed_unchecked") : t("common_not_installed"))
            }}
          </span>
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
          <span class="info_value">
            {{
              store.ffmpegStatus == null
                ? t("common_dash")
                : (store.ffmpegStatus.has_update ? t("common_yes") : t("common_no"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_binary_path") }}</span>
          <span class="info_value long">{{ store.ffmpegStatus?.binary_path || store.dependencyStatus?.ffmpeg.path || t("common_dash") }}</span>
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
  // 进入设置页时：读取本地依赖状态 + 读取应用设置（并发下载等）。
  await Promise.all([store.refreshDependencyStatus(), store.refreshAppSettings()]);
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

async function saveSettings() {
  await store.saveAppSettings();
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
  padding: var(--card_padding);
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

.input_number {
  width: 120px;
  height: var(--control_height);
  border-radius: 9999px;
  border: 1px solid var(--hairline-strong);
  background: var(--canvas);
  color: var(--ink);
  padding: 0 14px;
  font-size: 14px;
}

.card_hint {
  margin: 0;
  font-size: 13px;
  color: var(--body);
}

.row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  border-radius: 9999px;
  height: var(--control_height);
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
  overflow-wrap: anywhere;
}

@media (max-width: 760px) {
  .card {
    padding: var(--card_padding_compact);
  }
  .info_row {
    grid-template-columns: 1fr;
    gap: 2px;
  }
  .btn-primary,
  .btn-secondary {
    flex: 1 1 220px;
  }
  .input_number {
    width: 100%;
    max-width: 220px;
  }
}

@media (max-width: 560px) {
  /* 小屏时按钮改为整行，避免英文文案下出现拥挤换行。 */
  .btn-primary,
  .btn-secondary {
    height: var(--control_height_compact);
    width: 100%;
    min-width: 0;
  }
  .input_number {
    max-width: none;
  }
}
</style>
