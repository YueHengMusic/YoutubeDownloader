<template>
  <div class="app-shell">
    <aside class="side-nav">
      <div class="side-brand">
        <div class="brand-dot">{{ t("app_brand_short") }}</div>
        <span class="brand-title">{{ t("app_brand_title") }}</span>
      </div>
      <nav class="side-links">
        <RouterLink class="nav-link" to="/download">{{ t("nav_download") }}</RouterLink>
        <RouterLink class="nav-link" to="/queue">{{ t("nav_queue") }}</RouterLink>
        <RouterLink class="nav-link" to="/history">{{ t("nav_history") }}</RouterLink>
        <RouterLink class="nav-link" to="/logs">{{ t("nav_logs") }}</RouterLink>
        <RouterLink class="nav-link" to="/settings">{{ t("nav_settings") }}</RouterLink>
        <RouterLink class="nav-link" to="/about">{{ t("nav_about") }}</RouterLink>
      </nav>
      <div class="side-actions">
        <div class="theme-switch">
          <span class="lang-label">{{ t("nav_theme_label") }}</span>
          <div class="lang-pill-group">
            <button class="lang-pill" :class="{ active: theme_mode === 'light' }" type="button" @click="setThemeMode('light')">
              {{ t("nav_theme_light") }}
            </button>
            <button class="lang-pill" :class="{ active: theme_mode === 'dark' }" type="button" @click="setThemeMode('dark')">
              {{ t("nav_theme_dark") }}
            </button>
          </div>
        </div>
        <div class="lang-switch">
          <span class="lang-label">{{ t("nav_language_label") }}</span>
          <div class="lang-pill-group">
            <button class="lang-pill" :class="{ active: locale_ref === 'zh-CN' }" type="button" @click="setLocale('zh-CN')">
              {{ t("nav_language_zh_cn") }}
            </button>
            <button class="lang-pill" :class="{ active: locale_ref === 'en' }" type="button" @click="setLocale('en')">
              {{ t("nav_language_en") }}
            </button>
          </div>
        </div>
      </div>
    </aside>

    <div class="workspace">
      <section v-if="uiStore.notice.visible" class="notice" :data-type="uiStore.notice.type">
        <span>{{ uiStore.notice.message }}</span>
      </section>
      <main class="page">
        <section class="page-content">
          <RouterView />
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRealtimeTaskStore } from "@/stores/realtime";
import { useUiStore } from "@/stores/ui";
import { locale_ref, setLocale, t } from "@/i18n/strings";

type ThemeMode = "light" | "dark";
const THEME_MODE_STORAGE_KEY = "yt_dlp_gui_theme_mode";

const uiStore = useUiStore();
const realtimeStore = useRealtimeTaskStore();
let noticeTimer: ReturnType<typeof setTimeout> | null = null;

function detectThemeMode(): ThemeMode {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function loadInitialThemeMode(): ThemeMode {
  if (typeof localStorage !== "undefined") {
    const savedThemeMode = localStorage.getItem(THEME_MODE_STORAGE_KEY);
    if (savedThemeMode === "light" || savedThemeMode === "dark") {
      return savedThemeMode;
    }
  }
  return detectThemeMode();
}

const theme_mode = ref<ThemeMode>(loadInitialThemeMode());

function setThemeMode(mode: ThemeMode) {
  theme_mode.value = mode;
}

watch(
  theme_mode,
  (mode) => {
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", mode);
    }
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(THEME_MODE_STORAGE_KEY, mode);
    }
  },
  { immediate: true }
);

watch(
  () => `${uiStore.notice.visible}:${uiStore.notice.nonce}`,
  () => {
    if (noticeTimer) {
      clearTimeout(noticeTimer);
      noticeTimer = null;
    }
    if (!uiStore.notice.visible) return;
    // 提示自动消失，不需要手动关闭；新提示到来会重置计时。
    noticeTimer = setTimeout(() => {
      uiStore.clearNotice();
    }, 3200);
  }
);

onBeforeUnmount(() => {
  if (noticeTimer) clearTimeout(noticeTimer);
});

onMounted(() => {
  // 全局壳组件启动时就连接 WS，确保在任意页面都能收到实时终端输出。
  realtimeStore.connectWs();
});
</script>

<style>
:root {
  color-scheme: light;
  --primary: #000000;
  --on-primary: #ffffff;
  --ink: #000000;
  --ink-deep: #090909;
  --charcoal: #525252;
  --body: #737373;
  --mute: #a3a3a3;
  --canvas: #ffffff;
  --surface-soft: #fafafa;
  --hairline: #e5e5e5;
  --hairline-strong: #d4d4d4;
  --focus-ring: rgba(59, 130, 246, 0.5);
  /* 统一尺寸节奏：按钮高度、输入高度、卡片内边距在各页面复用。 */
  --control_height: 36px;
  --control_height_compact: 32px;
  --field_height: 40px;
  --field_height_compact: 36px;
  --card_padding: 20px;
  --card_padding_compact: 16px;
  /* 页面主内容最大宽度：窗口足够时自动变宽，不再固定窄列。 */
  --layout_max_width: 1160px;
  --notice-bg: #ffffff;
  --notice-success-bg: #f0fdf4;
  --notice-success-border: #bbf7d0;
  --notice-error-bg: #fef2f2;
  --notice-error-border: #fecaca;
  --select-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  --select-option-selected-bg: #f3f4f6;
  --status-running-border: #bfdbfe;
  --status-running-bg: #eff6ff;
  --status-running-text: #1d4ed8;
  --status-completed-border: #bbf7d0;
  --status-completed-bg: #f0fdf4;
  --status-completed-text: #166534;
  --status-failed-border: #fecaca;
  --status-failed-bg: #fef2f2;
  --status-failed-text: #991b1b;
  --status-canceled-border: #e5e7eb;
  --status-canceled-bg: #f9fafb;
  --status-canceled-text: #4b5563;
  --skeleton-base: #fafafa;
  --skeleton-highlight: #f3f4f6;
}

:root[data-theme="dark"] {
  color-scheme: dark;
  --primary: #e5e7eb;
  --on-primary: #111827;
  --ink: #f3f4f6;
  --ink-deep: #ffffff;
  --charcoal: #d1d5db;
  --body: #9ca3af;
  --mute: #6b7280;
  --canvas: #0f1115;
  --surface-soft: #171a21;
  --hairline: #2b313d;
  --hairline-strong: #3a4150;
  --focus-ring: rgba(96, 165, 250, 0.4);
  --notice-bg: #171a21;
  --notice-success-bg: #0f2a1d;
  --notice-success-border: #1e5d3a;
  --notice-error-bg: #331a1d;
  --notice-error-border: #7f1d1d;
  --select-shadow: 0 10px 24px rgba(0, 0, 0, 0.4);
  --select-option-selected-bg: #202634;
  --status-running-border: #1e3a8a;
  --status-running-bg: #172554;
  --status-running-text: #bfdbfe;
  --status-completed-border: #166534;
  --status-completed-bg: #052e16;
  --status-completed-text: #86efac;
  --status-failed-border: #7f1d1d;
  --status-failed-bg: #450a0a;
  --status-failed-text: #fecaca;
  --status-canceled-border: #374151;
  --status-canceled-bg: #1f2937;
  --status-canceled-text: #d1d5db;
  --skeleton-base: #171a21;
  --skeleton-highlight: #202634;
}

* {
  box-sizing: border-box;
}

html,
body,
#app {
  margin: 0;
  min-height: 100%;
  background: var(--canvas);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
}

button,
input,
select {
  font: inherit;
}

a {
  color: var(--ink);
}
</style>

<style scoped>
.app-shell {
  height: 100vh;
  display: flex;
  background: var(--canvas);
  overflow: hidden;
}

.brand-dot {
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  border: 1px solid var(--hairline-strong);
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 600;
}

.side-nav {
  flex: 0 0 236px;
  width: 236px;
  height: 100vh;
  border-right: 1px solid var(--hairline);
  background: var(--surface-soft);
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  /**
   * 侧边栏固定在视口内：
   * - 不跟随右侧页面内容滚动；
   * - 右侧内容很长时，语言切换与终端开关仍停留在侧边栏底部可见位置。
   */
  position: sticky;
  top: 0;
  overflow-y: auto;
}

.side-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 40px;
  padding: 0 8px;
}

.brand-title {
  font-size: 14px;
  font-weight: 600;
}

.side-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-link {
  font-size: 14px;
  text-decoration: none;
  color: var(--ink);
  height: var(--control_height);
  border-radius: 10px;
  padding: 0 10px;
  display: flex;
  align-items: center;
}

.nav-link.router-link-active {
  border: 1px solid var(--hairline-strong);
  background: var(--canvas);
}

.lang-switch {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.theme-switch {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.side-actions {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lang-label {
  color: var(--body);
  font-size: 12px;
  padding-left: 4px;
}

.lang-pill-group {
  display: flex;
  align-items: center;
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  padding: 2px;
  background: var(--surface-soft);
}

.lang-pill {
  flex: 1;
  min-width: 64px;
  height: var(--control_height);
  border: 0;
  border-radius: 9999px;
  padding: 0 10px;
  background: transparent;
  color: var(--body);
  cursor: pointer;
}

.lang-pill.active {
  background: var(--canvas);
  border: 1px solid var(--hairline);
  color: var(--ink);
}

.workspace {
  flex: 1;
  min-width: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  /**
   * 仅右侧工作区滚动，避免整个应用一起滚动导致“侧边栏跟着跑”。
   */
  overflow-y: auto;
  overflow-x: hidden;
}

.notice {
  position: fixed;
  bottom: 14px;
  right: 14px;
  z-index: 50;
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: 12px 14px;
  min-width: 260px;
  max-width: 420px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  font-size: 14px;
  background: var(--notice-bg);
}

.page {
  flex: 1;
  max-width: var(--layout_max_width);
  width: 100%;
  margin: 0 auto;
  padding: 24px 20px 32px;
}

.notice[data-type="success"] {
  border-color: var(--notice-success-border);
  background: var(--notice-success-bg);
}

.notice[data-type="error"] {
  border-color: var(--notice-error-border);
  background: var(--notice-error-bg);
}

.page-content {
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: var(--card_padding);
}


@media (max-width: 1080px) {
  .side-nav {
    flex-basis: 212px;
    width: 212px;
  }
}

@media (max-width: 840px) {
  .notice {
    bottom: 12px;
    left: 12px;
    right: 12px;
    min-width: 0;
    max-width: none;
  }
}

@media (max-width: 560px) {
  .app-shell {
    flex-direction: column;
  }
  .side-nav {
    width: 100%;
    border-right: 0;
    border-bottom: 1px solid var(--hairline);
    padding: 12px;
    gap: 10px;
  }
  .side-links {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 6px;
  }
  .nav-link {
    width: calc(50% - 3px);
  }
  .side-actions {
    margin-top: 0;
  }
  .page {
    padding-left: 12px;
    padding-right: 12px;
  }
  .page-content {
    padding: var(--card_padding_compact);
  }
}
</style>
