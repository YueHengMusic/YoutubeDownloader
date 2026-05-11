<template>
  <div class="app-shell">
    <header class="primary-nav">
      <div class="nav-inner">
        <div class="brand-group">
          <div class="brand-dot">{{ t("app_brand_short") }}</div>
          <span class="brand-title">{{ t("app_brand_title") }}</span>
          <RouterLink class="nav-link" to="/download">{{ t("nav_download") }}</RouterLink>
          <RouterLink class="nav-link" to="/queue">{{ t("nav_queue") }}</RouterLink>
          <RouterLink class="nav-link" to="/history">{{ t("nav_history") }}</RouterLink>
          <RouterLink class="nav-link" to="/settings">{{ t("nav_settings") }}</RouterLink>
        </div>
        <div class="nav-actions">
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
          <button class="terminal-toggle" type="button" :class="{ active: store.terminalPanelVisible }" @click="store.toggleTerminalPanel()">
            {{ store.terminalPanelVisible ? t("nav_terminal_hide") : t("nav_terminal_show") }}
          </button>
        </div>
      </div>
    </header>

    <main class="page">
      <section v-if="store.notice.visible" class="notice" :data-type="store.notice.type">
        <span>{{ store.notice.message }}</span>
      </section>

      <section class="hero">
        <h1>{{ t("hero_title") }}</h1>
        <p>{{ t("hero_subtitle") }}</p>
      </section>

      <section class="page-content">
        <RouterView />
      </section>
    </main>

    <footer class="app-footer">
      <div v-if="store.terminalPanelVisible" class="terminal-card">
        <div class="terminal-header">
          <strong>{{ t("terminal_title") }}</strong>
          <button type="button" class="terminal-clear" @click="store.clearTerminalLogs()">
            {{ t("terminal_clear") }}
          </button>
        </div>
        <div ref="terminalBodyRef" class="terminal-body">
          <p v-if="store.terminalLogs.length === 0" class="terminal-empty">{{ t("terminal_empty") }}</p>
          <p v-for="line in store.terminalLogs" :key="line.id" class="terminal-line">
            <span class="terminal-meta">[{{ formatTime(line.created_at) }}] [{{ line.task_id.slice(0, 8) }}] [{{ terminalStreamLabel(line.stream) }}]</span>
            <span class="terminal-text">{{ line.text }}</span>
          </p>
        </div>
      </div>
      <div class="copyright-card">
        <p class="copyright-line">{{ t("footer_copyright", { year: currentYear }) }}</p>
        <p class="copyright-line">{{ t("footer_contact") }}</p>
        <p class="copyright-line">
          <span>{{ t("footer_based_on_prefix") }}</span>
          <a href="#" @click.prevent="openYtDlpRepo">{{ t("footer_based_on_link_text") }}</a>
          <span>{{ t("footer_based_on_suffix") }}</span>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useTaskStore } from "@/stores/tasks";
import { locale_ref, setLocale, t } from "@/i18n/strings";
import type { TerminalStreamType } from "@/stores/tasks";

const store = useTaskStore();
let noticeTimer: ReturnType<typeof setTimeout> | null = null;
const terminalBodyRef = ref<HTMLElement | null>(null);
const yt_dlp_repo_url = "https://github.com/yt-dlp/yt-dlp";
const currentYear = new Date().getFullYear();

watch(
  () => `${store.notice.visible}:${store.notice.nonce}`,
  () => {
    if (noticeTimer) {
      clearTimeout(noticeTimer);
      noticeTimer = null;
    }
    if (!store.notice.visible) return;
    // 提示自动消失，不需要手动关闭；新提示到来会重置计时。
    noticeTimer = setTimeout(() => {
      store.clearNotice();
    }, 3200);
  }
);

watch(
  () => store.terminalLogs.length,
  async () => {
    if (!store.terminalPanelVisible) return;
    // 新日志到达时自动滚动到底部，避免用户手动追踪最新输出。
    await nextTick();
    if (terminalBodyRef.value) {
      terminalBodyRef.value.scrollTop = terminalBodyRef.value.scrollHeight;
    }
  }
);

function terminalStreamLabel(stream: TerminalStreamType): string {
  if (stream === "command") return t("terminal_stream_command");
  if (stream === "status") return t("terminal_stream_status");
  return t("terminal_stream_stdout");
}

function formatTime(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString();
}

async function openYtDlpRepo() {
  try {
    const ok = await window.desktopAPI?.openExternalUrl?.(yt_dlp_repo_url);
    if (ok) return;
  } catch {
    // ignore
  }
  const popupWindow = window.open(yt_dlp_repo_url, "_blank", "noopener,noreferrer");
  if (!popupWindow) window.location.href = yt_dlp_repo_url;
}

onBeforeUnmount(() => {
  if (noticeTimer) clearTimeout(noticeTimer);
});

onMounted(() => {
  // 全局壳组件启动时就连接 WS，确保在任意页面都能收到实时终端输出。
  store.connectWs();
});
</script>

<style>
:root {
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
  min-height: 100vh;
  background: var(--canvas);
}

.primary-nav {
  height: 56px;
  border-bottom: 1px solid var(--hairline);
  background: var(--canvas);
}

.nav-inner {
  height: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 12px;
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

.brand-title {
  font-size: 14px;
  font-weight: 600;
  margin-right: 8px;
}

.nav-link {
  font-size: 14px;
  text-decoration: none;
}

.lang-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.nav-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.terminal-toggle {
  height: 32px;
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  background: var(--canvas);
  color: var(--body);
  padding: 0 12px;
  cursor: pointer;
}

.terminal-toggle.active {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
}

.lang-label {
  color: var(--body);
  font-size: 12px;
}

.lang-pill-group {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  padding: 2px;
  background: var(--surface-soft);
}

.lang-pill {
  height: 28px;
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

.page {
  max-width: 760px;
  margin: 0 auto;
  padding: 24px 20px 32px;
}

.notice {
  position: fixed;
  top: 14px;
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
  background: #ffffff;
}

.notice[data-type="success"] {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.notice[data-type="error"] {
  border-color: #fecaca;
  background: #fef2f2;
}

.hero {
  text-align: center;
  margin-bottom: 32px;
}

.hero h1 {
  margin: 0 0 8px;
  font-size: 36px;
  line-height: 1.11;
  font-weight: 500;
  font-family: "SF Pro Rounded", ui-rounded, ui-sans-serif, system-ui, sans-serif;
}

.hero p {
  margin: 0;
  color: var(--body);
  font-size: 16px;
}

.page-content {
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: 24px;
}

.app-footer {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 20px 24px;
}

.terminal-card {
  background: var(--canvas);
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: 16px;
}

.terminal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--hairline);
  font-size: 14px;
}

.terminal-clear {
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  background: var(--canvas);
  color: var(--ink);
  height: 32px;
  padding: 0 10px;
  cursor: pointer;
}

.terminal-body {
  margin-top: 12px;
  max-height: 220px;
  overflow: auto;
  padding: 0;
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  font-size: 14px;
  line-height: 1.45;
}

.terminal-empty {
  margin: 0;
  color: var(--mute);
}

.terminal-line {
  margin: 0 0 6px;
}

.terminal-meta {
  color: var(--body);
  margin-right: 8px;
}

.terminal-text {
  color: var(--ink);
}

.copyright-card {
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: 12px 16px;
  background: var(--canvas);
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  text-align: center;
}

.copyright-line {
  margin: 0;
  font-size: 13px;
  color: var(--body);
}

.copyright-line a {
  color: var(--ink);
  text-decoration: underline;
}

@media (max-width: 840px) {
  .hero h1 {
    font-size: 28px;
  }
  .brand-title {
    display: none;
  }
  .lang-label {
    display: none;
  }
  .notice {
    left: 12px;
    right: 12px;
    min-width: 0;
    max-width: none;
  }
  .app-footer {
    padding-bottom: 16px;
  }
}
</style>
