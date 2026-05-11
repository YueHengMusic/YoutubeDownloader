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
              v-model.number="settingsStore.downloadConcurrencyInput"
              class="input_number"
              type="number"
              :min="settingsStore.appSettings?.min_download_concurrency ?? 1"
              :max="settingsStore.appSettings?.max_download_concurrency ?? 20"
            />
          </span>
        </div>
      </div>
      <p class="card_hint">
        {{
          t("settings_download_concurrency_hint", {
            min: settingsStore.appSettings?.min_download_concurrency ?? 1,
            max: settingsStore.appSettings?.max_download_concurrency ?? 20,
            defaultValue: settingsStore.appSettings?.default_download_concurrency ?? 2
          })
        }}
      </p>
      <div class="row">
        <button
          class="btn-primary"
          @click="saveSettings"
          :disabled="settingsStore.isSavingAppSettings || settingsStore.isRefreshingAppSettings"
        >
          {{ settingsStore.isSavingAppSettings ? t("settings_button_saving") : t("settings_button_save") }}
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
              systemStore.ytDlpStatus?.installed_version
                || (systemStore.dependencyStatus?.yt_dlp.exists ? t("settings_installed_unchecked") : t("common_not_installed"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_latest_version") }}</span>
          <span class="info_value">{{ systemStore.ytDlpStatus?.latest_version || t("common_dash") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_need_update") }}</span>
          <span class="info_value">
            {{
              systemStore.ytDlpStatus == null
                ? t("common_dash")
                : (systemStore.ytDlpStatus.has_update ? t("common_yes") : t("common_no"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_binary_path") }}</span>
          <span class="info_value long">{{
            systemStore.ytDlpStatus?.binary_path || systemStore.dependencyStatus?.yt_dlp.path || t("common_dash")
          }}</span>
        </div>
      </div>
      <div class="row">
        <button
          class="btn-secondary"
          @click="checkYtDlp"
          :disabled="systemStore.isCheckingYtDlp || systemStore.isUpdatingYtDlp"
        >
          {{ systemStore.isCheckingYtDlp ? t("settings_button_checking") : t("settings_button_check_update") }}
        </button>
        <button
          class="btn-primary"
          @click="updateYtDlp"
          :disabled="systemStore.isUpdatingYtDlp || systemStore.isCheckingYtDlp"
        >
          {{ systemStore.isUpdatingYtDlp ? t("settings_button_updating") : t("settings_button_update_ytdlp") }}
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
              systemStore.ffmpegStatus?.installed_version
                || (systemStore.dependencyStatus?.ffmpeg.exists ? t("settings_installed_unchecked") : t("common_not_installed"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_latest_release_id") }}</span>
          <span class="info_value">{{ systemStore.ffmpegStatus?.latest_release_id ?? t("common_dash") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_latest_published_at") }}</span>
          <span class="info_value">{{ systemStore.ffmpegStatus?.latest_published_at || t("common_dash") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_local_release_id") }}</span>
          <span class="info_value">{{ systemStore.ffmpegStatus?.local_release_id ?? t("common_unknown") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_need_update") }}</span>
          <span class="info_value">
            {{
              systemStore.ffmpegStatus == null
                ? t("common_dash")
                : (systemStore.ffmpegStatus.has_update ? t("common_yes") : t("common_no"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_ffmpeg_exists") }}</span>
          <span class="info_value">
            {{
              systemStore.dependencyStatus?.ffmpeg.ffmpeg_exists == null
                ? t("common_dash")
                : (systemStore.dependencyStatus.ffmpeg.ffmpeg_exists ? t("common_yes") : t("common_no"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_ffprobe_exists") }}</span>
          <span class="info_value">
            {{
              systemStore.dependencyStatus?.ffmpeg.ffprobe_exists == null
                ? t("common_dash")
                : (systemStore.dependencyStatus.ffmpeg.ffprobe_exists ? t("common_yes") : t("common_no"))
            }}
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_ffmpeg_path") }}</span>
          <span class="info_value long">{{
            systemStore.ffmpegStatus?.binary_path || systemStore.dependencyStatus?.ffmpeg.path || t("common_dash")
          }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("settings_label_ffprobe_path") }}</span>
          <span class="info_value long">{{
            systemStore.ffmpegStatus?.ffprobe_path || systemStore.dependencyStatus?.ffmpeg.ffprobe_path || t("common_dash")
          }}</span>
        </div>
      </div>
      <div class="row">
        <button
          class="btn-secondary"
          @click="checkFfmpeg"
          :disabled="systemStore.isCheckingFfmpeg || systemStore.isUpdatingFfmpeg"
        >
          {{ systemStore.isCheckingFfmpeg ? t("settings_button_checking") : t("settings_button_check_update") }}
        </button>
        <button
          class="btn-primary"
          @click="updateFfmpeg"
          :disabled="systemStore.isUpdatingFfmpeg || systemStore.isCheckingFfmpeg"
        >
          {{ systemStore.isUpdatingFfmpeg ? t("settings_button_updating") : t("settings_button_update_ffmpeg") }}
        </button>
      </div>
    </article>

    <p class="meta">{{ t("settings_meta", { backendUrl }) }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useSettingsStore } from "@/stores/settings";
import { useSystemStore } from "@/stores/system";
import { t } from "@/i18n/strings";

// 设置页用于展示“依赖组件可用性”和“一键更新”能力。
const backendUrl = "http://127.0.0.1:8000";
const settingsStore = useSettingsStore();
const systemStore = useSystemStore();

onMounted(async () => {
  // 进入设置页时：读取本地依赖状态 + 读取应用设置（并发下载等）。
  await Promise.all([systemStore.refreshDependencyStatus(), settingsStore.refreshAppSettings()]);
});

async function checkYtDlp() {
  await systemStore.refreshYtDlpStatus();
}

async function updateYtDlp() {
  await systemStore.updateYtDlp();
}

async function checkFfmpeg() {
  await systemStore.refreshFfmpegStatus();
}

async function updateFfmpeg() {
  await systemStore.updateFfmpeg();
}

async function saveSettings() {
  await settingsStore.saveAppSettings();
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
