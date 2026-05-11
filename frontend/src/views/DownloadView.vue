<template>
  <section class="section">
    <div class="head">
      <h2>{{ t("download_title") }}</h2>
      <div class="mode-switch">
        <span class="mode-label">{{ t("download_mode_label") }}</span>
        <div class="mode-pill-group">
          <button class="mode-pill" :class="{ active: formMode === 'simple' }" type="button" @click="formMode = 'simple'">
            {{ t("download_mode_simple") }}
          </button>
          <button class="mode-pill" :class="{ active: formMode === 'advanced' }" type="button" @click="formMode = 'advanced'">
            {{ t("download_mode_advanced") }}
          </button>
        </div>
      </div>
    </div>
    <p class="desc">{{ t("download_desc") }}</p>

    <form @submit.prevent="submit">
      <label>{{ t("download_label_url") }}</label>
      <input v-model="url" required :placeholder="t('download_placeholder_url')" />

      <label>{{ t("download_label_output_dir") }}</label>
      <div class="row">
        <input v-model="outputDir" required />
        <button class="btn-secondary" type="button" @click="pickDir">{{ t("common_select") }}</button>
      </div>

      <label>{{ t("download_label_target") }}</label>
      <UiSelect v-model="downloadTarget" :options="download_target_options" />

      <label>{{ t("download_label_subtitle_mode") }}</label>
      <UiSelect v-model="subtitleMode" :options="subtitle_mode_options" :disabled="downloadTarget === 'thumbnail'" />
      <UiHint v-if="downloadTarget === 'thumbnail'">
        {{ t("download_hint_subtitle_disabled_thumbnail") }}
      </UiHint>

      <template v-if="formMode === 'advanced'">
        <template v-if="downloadTarget === 'audio'">
          <label>{{ t("download_label_audio_format") }}</label>
          <UiSelect v-model="audioFormat" :options="audio_format_options" />
        </template>

        <template v-if="downloadTarget === 'video'">
        <label>{{ t("download_label_format_id") }}</label>
        <input v-model="formatId" :placeholder="t('download_placeholder_format_id')" />

        <label>{{ t("download_label_resolution") }}</label>
        <input v-model="resolution" :placeholder="t('download_placeholder_resolution')" />
          <label>{{ t("download_label_resolution_mode") }}</label>
          <UiSelect v-model="resolutionMode" :options="resolution_mode_options" />
        </template>
        <template v-if="subtitleMode !== 'none'">
          <label>{{ t("download_label_subtitle_langs") }}</label>
          <input v-model="subtitleLangs" :placeholder="t('download_placeholder_subtitle_langs')" :disabled="downloadTarget === 'thumbnail'" />
        </template>

        <div class="check_list">
          <label class="check_item">
            <input v-model="writeInfoJson" type="checkbox" />
            <span>{{ t("download_option_write_info_json") }}</span>
          </label>
          <label class="check_item">
            <input v-model="writeDescription" type="checkbox" />
            <span>{{ t("download_option_write_description") }}</span>
          </label>
          <label class="check_item">
            <input v-model="writeThumbnail" type="checkbox" :disabled="downloadTarget === 'thumbnail'" />
            <span>{{ t("download_option_write_thumbnail") }}</span>
          </label>
          <label class="check_item">
            <input v-model="embedThumbnail" type="checkbox" :disabled="downloadTarget === 'thumbnail'" />
            <span>{{ t("download_option_embed_thumbnail") }}</span>
          </label>
        </div>
        <UiHint v-if="downloadTarget === 'thumbnail'">
          {{ t("download_hint_embed_thumbnail_disabled_thumbnail") }}
        </UiHint>
      </template>

      <div class="label_with_tip">
        <label>{{ t("download_label_cookie_mode") }}</label>
        <button class="tip_toggle" type="button" @click="showCookieTip = !showCookieTip">
          {{ t("download_cookie_tip_toggle") }}
        </button>
      </div>
      <div v-if="showCookieTip" class="tip_card">
        <span>{{ t("download_cookie_tip_text_prefix") }}</span>
        <a href="#" @click.prevent="openCookieHelperLink">
          {{ t("download_cookie_tip_link_text") }}
        </a>
        <span>{{ t("download_cookie_tip_text_suffix") }}</span>
      </div>
      <UiSelect v-model="cookieMode" :options="cookie_mode_options" />

      <div v-if="cookieMode === 'file'" class="row">
        <input v-model="cookieValue" :placeholder="t('download_placeholder_cookie_path')" />
        <button class="btn-secondary" type="button" @click="pickCookie">{{ t("common_select_file") }}</button>
      </div>

      <div v-if="cookieMode === 'browser'" class="browser-source-group">
        <label>{{ t("download_label_cookie_browser") }}</label>
        <UiSelect v-model="cookieValue" :options="cookie_browser_options" />
      </div>

      <button class="btn-primary" type="submit" :disabled="isSubmitDisabled">
        {{ store.isSubmittingTask ? t("download_submitting") : t("download_submit") }}
      </button>
      <UiHint v-if="isDependencyInstalling">
        {{ t("download_dependency_installing_hint") }}
      </UiHint>
      <UiHint v-else-if="!isDependencyReady">
        {{ t("download_dependency_missing_hint") }}
        <RouterLink class="hint_link" to="/settings">{{ t("download_dependency_go_settings") }}</RouterLink>
        {{ t("download_dependency_go_settings_suffix") }}
      </UiHint>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useTaskRuntimeStore } from "@/stores/taskRuntime";
import { useSystemStore } from "@/stores/system";
import { t } from "@/i18n/strings";
import UiSelect, { type UiSelectOption } from "@/components/UiSelect.vue";
import UiHint from "@/components/UiHint.vue";

type CookieMode = "none" | "file" | "browser";
type DownloadFormMode = "simple" | "advanced";
type DownloadTarget = "video" | "audio" | "thumbnail";
type ResolutionMode = "prefer" | "limit";
type AudioFormat = "mp3" | "m4a" | "opus" | "wav" | "flac";
type SubtitleMode = "none" | "manual" | "auto" | "all";

type DownloadFormDraft = {
  formMode: DownloadFormMode;
  outputDir: string;
  downloadTarget: DownloadTarget;
  formatId: string;
  resolution: string;
  resolutionMode: ResolutionMode;
  audioFormat: AudioFormat;
  subtitleMode: SubtitleMode;
  subtitleLangs: string;
  writeInfoJson: boolean;
  writeDescription: boolean;
  writeThumbnail: boolean;
  embedThumbnail: boolean;
  cookieMode: CookieMode;
  cookieValue: string;
};

const FORM_STORAGE_KEY = "yt_dlp_gui_download_form_draft";

function load_form_draft(): DownloadFormDraft {
  /**
   * 读取本地草稿：
   * - 仅保存“可复用参数”（输出目录/格式/分辨率/Cookie设置）；
   * - 不保存 URL，避免下次打开时误提交旧链接。
   */
  try {
    const raw = localStorage.getItem(FORM_STORAGE_KEY);
    if (!raw) {
      return {
        formMode: "simple",
        outputDir: ".",
        downloadTarget: "video",
        formatId: "",
        resolution: "",
        resolutionMode: "prefer",
        audioFormat: "mp3",
        subtitleMode: "none",
        subtitleLangs: "",
        writeInfoJson: false,
        writeDescription: false,
        writeThumbnail: false,
        embedThumbnail: false,
        cookieMode: "browser",
        cookieValue: "edge"
      };
    }
    const parsed = JSON.parse(raw) as Partial<DownloadFormDraft>;
    const formMode: DownloadFormMode = parsed.formMode === "advanced" ? "advanced" : "simple";
    const cookieMode: CookieMode = parsed.cookieMode === "file" || parsed.cookieMode === "browser" ? parsed.cookieMode : "none";
    return {
      formMode,
      outputDir: parsed.outputDir || ".",
      downloadTarget: parsed.downloadTarget === "audio" || parsed.downloadTarget === "thumbnail" ? parsed.downloadTarget : "video",
      formatId: parsed.formatId || "",
      resolution: parsed.resolution || "",
      resolutionMode: parsed.resolutionMode === "limit" ? "limit" : "prefer",
      audioFormat:
        parsed.audioFormat === "m4a" || parsed.audioFormat === "opus" || parsed.audioFormat === "wav" || parsed.audioFormat === "flac"
          ? parsed.audioFormat
          : "mp3",
      subtitleMode:
        parsed.subtitleMode === "manual" || parsed.subtitleMode === "auto" || parsed.subtitleMode === "all" ? parsed.subtitleMode : "none",
      subtitleLangs: parsed.subtitleLangs || "",
      writeInfoJson: Boolean(parsed.writeInfoJson),
      writeDescription: Boolean(parsed.writeDescription),
      writeThumbnail: Boolean(parsed.writeThumbnail),
      embedThumbnail: Boolean(parsed.embedThumbnail),
      cookieMode,
      cookieValue: parsed.cookieValue || ""
    };
  } catch {
    return {
      formMode: "simple",
      outputDir: ".",
      downloadTarget: "video",
      formatId: "",
      resolution: "",
      resolutionMode: "prefer",
      audioFormat: "mp3",
      subtitleMode: "none",
      subtitleLangs: "",
      writeInfoJson: false,
      writeDescription: false,
      writeThumbnail: false,
      embedThumbnail: false,
      cookieMode: "browser",
      cookieValue: "edge"
    };
  }
}

function save_form_draft(draft: DownloadFormDraft) {
  localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(draft));
}

// 这个页面的表单状态（每个输入框都对应一个响应式变量）。
const store = useTaskRuntimeStore();
const systemStore = useSystemStore();
const initialDraft = load_form_draft();
const url = ref("");
const formMode = ref<DownloadFormMode>(initialDraft.formMode);
const outputDir = ref(initialDraft.outputDir);
const downloadTarget = ref<DownloadTarget>(initialDraft.downloadTarget);
const formatId = ref(initialDraft.formatId);
const resolution = ref(initialDraft.resolution);
const resolutionMode = ref<ResolutionMode>(initialDraft.resolutionMode);
const audioFormat = ref<AudioFormat>(initialDraft.audioFormat);
const subtitleMode = ref<SubtitleMode>(initialDraft.subtitleMode);
const subtitleLangs = ref(initialDraft.subtitleLangs);
const writeInfoJson = ref(initialDraft.writeInfoJson);
const writeDescription = ref(initialDraft.writeDescription);
const writeThumbnail = ref(initialDraft.writeThumbnail);
const embedThumbnail = ref(initialDraft.embedThumbnail);
const cookieMode = ref<CookieMode>(initialDraft.cookieMode);
const cookieValue = ref(initialDraft.cookieValue);
const showCookieTip = ref(false);
const cookie_helper_url = "https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc";
const cookie_mode_options = computed<UiSelectOption[]>(() => [
  { value: "none", label: t("download_cookie_mode_none") },
  { value: "file", label: t("download_cookie_mode_file") },
  { value: "browser", label: t("download_cookie_mode_browser") }
]);
const cookie_browser_options = computed<UiSelectOption[]>(() => [
  { value: "chrome", label: t("download_cookie_browser_chrome") },
  { value: "edge", label: t("download_cookie_browser_edge") }
]);
const download_target_options = computed<UiSelectOption[]>(() => [
  { value: "video", label: t("download_target_video") },
  { value: "audio", label: t("download_target_audio") },
  { value: "thumbnail", label: t("download_target_thumbnail") }
]);
const resolution_mode_options = computed<UiSelectOption[]>(() => [
  { value: "prefer", label: t("download_resolution_mode_prefer") },
  { value: "limit", label: t("download_resolution_mode_limit") }
]);
const audio_format_options = computed<UiSelectOption[]>(() => [
  { value: "mp3", label: "mp3" },
  { value: "m4a", label: "m4a" },
  { value: "opus", label: "opus" },
  { value: "wav", label: "wav" },
  { value: "flac", label: "flac" }
]);
const subtitle_mode_options = computed<UiSelectOption[]>(() => [
  { value: "none", label: t("download_subtitle_mode_none") },
  { value: "manual", label: t("download_subtitle_mode_manual") },
  { value: "auto", label: t("download_subtitle_mode_auto") },
  { value: "all", label: t("download_subtitle_mode_all") }
]);
const isDependencyInstalling = computed(() => {
  const dependencyStatus = systemStore.dependencyStatus;
  if (!dependencyStatus) return false;
  return dependencyStatus.yt_dlp.installing || dependencyStatus.ffmpeg.installing;
});
const isDependencyReady = computed(() => {
  const dependencyStatus = systemStore.dependencyStatus;
  if (!dependencyStatus) return false;
  return dependencyStatus.yt_dlp.exists && dependencyStatus.ffmpeg.exists && !isDependencyInstalling.value;
});
const isSubmitDisabled = computed(() => {
  return store.isSubmittingTask || !isDependencyReady.value || isDependencyInstalling.value;
});
let dependencyPollTimer: ReturnType<typeof setInterval> | null = null;

watch(
  [
    formMode,
    outputDir,
    downloadTarget,
    formatId,
    resolution,
    resolutionMode,
    audioFormat,
    subtitleMode,
    subtitleLangs,
    writeInfoJson,
    writeDescription,
    writeThumbnail,
    embedThumbnail,
    cookieMode,
    cookieValue
  ],
  () => {
  save_form_draft({
    formMode: formMode.value,
    outputDir: outputDir.value,
    downloadTarget: downloadTarget.value,
    formatId: formatId.value,
    resolution: resolution.value,
    resolutionMode: resolutionMode.value,
    audioFormat: audioFormat.value,
    subtitleMode: subtitleMode.value,
    subtitleLangs: subtitleLangs.value,
    writeInfoJson: writeInfoJson.value,
    writeDescription: writeDescription.value,
    writeThumbnail: writeThumbnail.value,
    embedThumbnail: embedThumbnail.value,
    cookieMode: cookieMode.value,
    cookieValue: cookieValue.value
  });
  }
);

watch(downloadTarget, (target) => {
  // 非视频模式下避免遗留的视频参数造成混淆。
  if (target !== "video") {
    formatId.value = "";
  }
  if (target === "thumbnail") {
    // 仅封面模式下，清理无意义选项，避免用户误解这些开关会生效。
    writeThumbnail.value = true;
    embedThumbnail.value = false;
    subtitleMode.value = "none";
    subtitleLangs.value = "";
  }
});

watch(cookieMode, (mode) => {
  // 浏览器模式下仅允许固定枚举值，避免手输拼写导致后端参数无效。
  if (mode === "browser" && cookieValue.value !== "chrome" && cookieValue.value !== "edge") {
    cookieValue.value = "edge";
  }
  // 切到文件模式时，清理浏览器名称残留，避免输入框出现 edge/chrome 误导用户。
  if (mode === "file" && (cookieValue.value === "chrome" || cookieValue.value === "edge")) {
    cookieValue.value = "";
  }
  if (mode === "none") {
    cookieValue.value = "";
  }
});

onMounted(async () => {
  await systemStore.refreshDependencyStatus();
  dependencyPollTimer = setInterval(() => {
    void systemStore.refreshDependencyStatus();
  }, 3000);
});

onBeforeUnmount(() => {
  if (dependencyPollTimer) {
    clearInterval(dependencyPollTimer);
    dependencyPollTimer = null;
  }
});

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

async function openCookieHelperLink() {
  /**
   * 优先走 Electron 主进程调用 shell.openExternal，以便使用系统默认浏览器。
   * 如果当前不是桌面环境（例如纯浏览器调试），则降级使用 window.open。
   */
  try {
    const ok = await window.desktopAPI?.openExternalUrl?.(cookie_helper_url);
    if (ok) return;
  } catch {
    // ignore: 可能是旧版 Electron 主进程未注册 IPC，走下方降级方案。
  }
  const popupWindow = window.open(cookie_helper_url, "_blank", "noopener,noreferrer");
  if (!popupWindow) {
    // 再兜底：至少保证链接可访问（即便不是默认浏览器路径）。
    window.location.href = cookie_helper_url;
  }
}

async function submit() {
  // 组装创建任务请求：可选字段为空时用 undefined，后端会按“未填写”处理。
  await store.createTask({
    url: url.value,
    output_dir: outputDir.value,
    download_target: downloadTarget.value,
    format_id: downloadTarget.value === "video" ? formatId.value || undefined : undefined,
    resolution: downloadTarget.value === "video" ? resolution.value || undefined : undefined,
    resolution_mode: downloadTarget.value === "video" ? resolutionMode.value : undefined,
    audio_format: downloadTarget.value === "audio" ? audioFormat.value : undefined,
    subtitle_mode: subtitleMode.value,
    subtitle_langs: subtitleMode.value !== "none" ? subtitleLangs.value || undefined : undefined,
    write_info_json: writeInfoJson.value,
    write_description: writeDescription.value,
    write_thumbnail: downloadTarget.value === "thumbnail" ? true : writeThumbnail.value,
    embed_thumbnail: downloadTarget.value === "thumbnail" ? false : embedThumbnail.value,
    cookie_mode: cookieMode.value,
    cookie_value: cookieValue.value || undefined
  });
  url.value = "";
}
</script>

<style scoped>
.section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.33;
  font-weight: 600;
  font-family: "SF Pro Rounded", ui-rounded, ui-sans-serif, system-ui, sans-serif;
}

.desc {
  margin: 0;
  font-size: 14px;
  color: var(--body);
}

.mode-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.mode-label {
  color: var(--body);
  font-size: 12px;
}

.mode-pill-group {
  display: flex;
  align-items: center;
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  padding: 2px;
  background: var(--surface-soft);
}

.mode-pill {
  min-width: 64px;
  height: var(--control_height);
  border: 0;
  border-radius: 9999px;
  padding: 0 12px;
  background: transparent;
  color: var(--body);
  cursor: pointer;
}

.mode-pill.active {
  background: var(--canvas);
  border: 1px solid var(--hairline);
  color: var(--ink);
}

form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

label {
  font-size: 14px;
  font-weight: 500;
}

.row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.row > input,
.row > select {
  flex: 1;
  min-width: 220px;
}

.row > .btn-secondary {
  flex: 0 0 auto;
}

.browser-source-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.check_list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 8px 12px;
}

.check_item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--body);
}

.check_item input[type="checkbox"] {
  width: 16px;
  height: 16px;
}


.label_with_tip {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tip_toggle {
  width: 20px;
  height: 20px;
  border: 1px solid var(--hairline-strong);
  border-radius: 9999px;
  background: var(--canvas);
  color: var(--body);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tip_card {
  border: 1px solid var(--hairline);
  border-radius: 12px;
  background: var(--surface-soft);
  padding: var(--card_padding_compact);
  font-size: 13px;
  color: var(--body);
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.tip_card a {
  color: var(--ink);
  text-decoration: underline;
}

.hint_link {
  margin-left: 4px;
  color: var(--ink);
  text-decoration: underline;
}

input {
  width: 100%;
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  height: var(--field_height);
  padding: 8px 16px;
  outline: none;
}

input:focus,
input:focus {
  border-color: var(--ink);
  box-shadow: 0 0 0 3px var(--focus-ring);
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

.btn-primary:disabled,
.btn-secondary:disabled {
  background: var(--surface-soft);
  border-color: var(--hairline);
  color: var(--mute);
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .head {
    align-items: stretch;
  }
  .mode-switch {
    justify-content: space-between;
    width: 100%;
  }
  .mode-pill {
    height: var(--control_height_compact);
  }
  /* 小屏下保持标签和提示按钮同行，避免提示按钮被挤到下一行影响可发现性。 */
  .label_with_tip {
    justify-content: space-between;
  }
  .row > input,
  .row > select {
    min-width: 0;
    width: 100%;
  }
  .row > .btn-secondary {
    width: 100%;
  }
  input {
    height: var(--field_height_compact);
  }
  .btn-primary,
  .btn-secondary {
    height: var(--control_height_compact);
  }
}
</style>
