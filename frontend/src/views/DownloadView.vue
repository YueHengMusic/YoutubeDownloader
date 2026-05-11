<template>
  <section class="section">
    <h2>{{ t("download_title") }}</h2>
    <p class="desc">{{ t("download_desc") }}</p>

    <form @submit.prevent="submit">
      <label>{{ t("download_label_url") }}</label>
      <input v-model="url" required :placeholder="t('download_placeholder_url')" />

      <label>{{ t("download_label_output_dir") }}</label>
      <div class="row">
        <input v-model="outputDir" required />
        <button class="btn-secondary" type="button" @click="pickDir">{{ t("common_select") }}</button>
      </div>

      <label>{{ t("download_label_format_id") }}</label>
      <input v-model="formatId" :placeholder="t('download_placeholder_format_id')" />

      <label>{{ t("download_label_resolution") }}</label>
      <input v-model="resolution" :placeholder="t('download_placeholder_resolution')" />

      <label>{{ t("download_label_cookie_mode") }}</label>
      <UiSelect v-model="cookieMode" :options="cookie_mode_options" />

      <div v-if="cookieMode === 'file'" class="row">
        <input v-model="cookieValue" :placeholder="t('download_placeholder_cookie_path')" />
        <button class="btn-secondary" type="button" @click="pickCookie">{{ t("common_select_file") }}</button>
      </div>

      <div v-if="cookieMode === 'browser'" class="browser-source-group">
        <label>{{ t("download_label_cookie_browser") }}</label>
        <UiSelect v-model="cookieValue" :options="cookie_browser_options" />
      </div>

      <button class="btn-primary" type="submit" :disabled="store.isSubmittingTask">
        {{ store.isSubmittingTask ? t("download_submitting") : t("download_submit") }}
      </button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useTaskStore } from "@/stores/tasks";
import { t } from "@/i18n/strings";
import UiSelect, { type UiSelectOption } from "@/components/UiSelect.vue";

type CookieMode = "none" | "file" | "browser";

type DownloadFormDraft = {
  outputDir: string;
  formatId: string;
  resolution: string;
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
        outputDir: ".",
        formatId: "",
        resolution: "",
        cookieMode: "none",
        cookieValue: ""
      };
    }
    const parsed = JSON.parse(raw) as Partial<DownloadFormDraft>;
    const mode: CookieMode = parsed.cookieMode === "file" || parsed.cookieMode === "browser" ? parsed.cookieMode : "none";
    return {
      outputDir: parsed.outputDir || ".",
      formatId: parsed.formatId || "",
      resolution: parsed.resolution || "",
      cookieMode: mode,
      cookieValue: parsed.cookieValue || ""
    };
  } catch {
    return {
      outputDir: ".",
      formatId: "",
      resolution: "",
      cookieMode: "none",
      cookieValue: ""
    };
  }
}

function save_form_draft(draft: DownloadFormDraft) {
  localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(draft));
}

// 这个页面的表单状态（每个输入框都对应一个响应式变量）。
const store = useTaskStore();
const initialDraft = load_form_draft();
const url = ref("");
const outputDir = ref(initialDraft.outputDir);
const formatId = ref(initialDraft.formatId);
const resolution = ref(initialDraft.resolution);
const cookieMode = ref<CookieMode>(initialDraft.cookieMode);
const cookieValue = ref(initialDraft.cookieValue);
const cookie_mode_options = computed<UiSelectOption[]>(() => [
  { value: "none", label: t("download_cookie_mode_none") },
  { value: "file", label: t("download_cookie_mode_file") },
  { value: "browser", label: t("download_cookie_mode_browser") }
]);
const cookie_browser_options = computed<UiSelectOption[]>(() => [
  { value: "chrome", label: t("download_cookie_browser_chrome") },
  { value: "edge", label: t("download_cookie_browser_edge") }
]);

watch([outputDir, formatId, resolution, cookieMode, cookieValue], () => {
  save_form_draft({
    outputDir: outputDir.value,
    formatId: formatId.value,
    resolution: resolution.value,
    cookieMode: cookieMode.value,
    cookieValue: cookieValue.value
  });
});

watch(cookieMode, (mode) => {
  // 浏览器模式下仅允许固定枚举值，避免手输拼写导致后端参数无效。
  if (mode === "browser" && cookieValue.value !== "chrome" && cookieValue.value !== "edge") {
    cookieValue.value = "chrome";
  }
  if (mode === "none") {
    cookieValue.value = "";
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
.section {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
}

.row > input,
.row > select {
  flex: 1;
}

.row > .btn-secondary {
  flex: 0 0 auto;
}

.browser-source-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

input {
  width: 100%;
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  height: 40px;
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

.btn-primary:disabled,
.btn-secondary:disabled {
  background: var(--surface-soft);
  border-color: var(--hairline);
  color: var(--mute);
  cursor: not-allowed;
}
</style>
