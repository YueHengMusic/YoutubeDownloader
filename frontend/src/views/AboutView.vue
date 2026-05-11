<template>
  <section class="section">
    <h2>{{ t("about_title") }}</h2>
    <p class="desc">{{ t("about_desc") }}</p>

    <article class="card">
      <h3>{{ t("about_section_project") }}</h3>
      <div class="info_list">
        <div class="info_row">
          <span class="info_key">{{ t("about_project_name") }}</span>
          <span class="info_value">{{ t("about_project_name_value") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_project_version") }}</span>
          <span class="info_value">{{ app_version }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_project_repository") }}</span>
          <span class="info_value">
            <a href="#" @click.prevent="open_project_repo">{{ project_repo_url }}</a>
          </span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_project_goal") }}</span>
          <span class="info_value">{{ t("about_project_goal_value") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_project_upstream") }}</span>
          <span class="info_value">
            <a href="#" @click.prevent="open_ytdlp_repo">{{ t("about_project_repo_link") }}</a>
          </span>
        </div>
      </div>
    </article>

    <article class="card">
      <h3>{{ t("about_section_author") }}</h3>
      <div class="info_list">
        <div class="info_row">
          <span class="info_key">{{ t("about_author_name") }}</span>
          <span class="info_value">{{ t("about_author_name_value") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_author_contact") }}</span>
          <span class="info_value">{{ t("about_author_contact_value") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_author_copyright") }}</span>
          <span class="info_value">{{ t("about_author_copyright_value", { year: current_year }) }}</span>
        </div>
      </div>
    </article>

    <article class="card">
      <h3>{{ t("about_section_stack") }}</h3>
      <div class="info_list">
        <div class="info_row">
          <span class="info_key">{{ t("about_stack_frontend") }}</span>
          <span class="info_value">{{ t("about_stack_frontend_value") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_stack_backend") }}</span>
          <span class="info_value">{{ t("about_stack_backend_value") }}</span>
        </div>
        <div class="info_row">
          <span class="info_key">{{ t("about_stack_desktop") }}</span>
          <span class="info_value">{{ t("about_stack_desktop_value") }}</span>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { t } from "@/i18n/strings";

const yt_dlp_repo_url = "https://github.com/yt-dlp/yt-dlp";
const project_repo_url = "https://github.com/YueHengMusic/YoutubeDownloader";
const app_version = ref<string>("-");
const current_year = new Date().getFullYear();

onMounted(async () => {
  // 版本号优先由 Electron 主进程提供；浏览器调试场景显示占位符。
  try {
    const version = await window.desktopAPI?.getAppVersion?.();
    if (version && version.trim()) {
      app_version.value = version.trim();
    }
  } catch {
    // ignore
  }
});

async function open_external_url(url: string) {
  /**
   * 优先通过 Electron 主进程打开系统默认浏览器；
   * 浏览器调试场景下回退到 window.open，保证链接可用。
   */
  try {
    const ok = await window.desktopAPI?.openExternalUrl?.(url);
    if (ok) return;
  } catch {
    // ignore
  }
  const popup_window = window.open(url, "_blank", "noopener,noreferrer");
  if (!popup_window) window.location.href = url;
}

async function open_project_repo() {
  await open_external_url(project_repo_url);
}

async function open_ytdlp_repo() {
  await open_external_url(yt_dlp_repo_url);
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
  overflow-wrap: anywhere;
}

.info_value a {
  color: var(--ink);
  text-decoration: underline;
}

@media (max-width: 760px) {
  .card {
    padding: var(--card_padding_compact);
  }
  .info_row {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
</style>
