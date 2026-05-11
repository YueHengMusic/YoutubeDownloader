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
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, watch } from "vue";
import { useTaskStore } from "@/stores/tasks";
import { locale_ref, setLocale, t } from "@/i18n/strings";

const store = useTaskStore();
let noticeTimer: ReturnType<typeof setTimeout> | null = null;

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

onBeforeUnmount(() => {
  if (noticeTimer) clearTimeout(noticeTimer);
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
  padding: 24px 20px 88px;
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
}
</style>
