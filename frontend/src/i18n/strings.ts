import { ref } from "vue";

/**
 * 统一文案资源：
 * - 所有用户可见文本都从这里取值，避免散落硬编码。
 * - 当前先提供简体中文和英文两套，后续可继续扩展。
 */
export type Locale = "zh-CN" | "en";

type MessageDict = Record<string, string>;

const ZH_CN: MessageDict = {
  app_brand_short: "yt",
  app_brand_title: "yt-dlp GUI",
  nav_download: "下载",
  nav_queue: "队列",
  nav_history: "历史",
  nav_settings: "设置",
  nav_language_label: "语言",
  nav_language_zh_cn: "中文",
  nav_language_en: "English",
  nav_terminal_show: "打开终端",
  nav_terminal_hide: "关闭终端",
  hero_title: "最简单的本地 yt-dlp 图形界面",
  hero_subtitle: "用更直观的界面管理下载任务、队列和依赖更新。",
  common_close: "关闭",
  common_refresh: "刷新",
  common_refreshing: "刷新中...",
  common_select: "选择",
  common_select_file: "选择文件",
  common_not_installed: "未安装",
  common_unknown: "未知",
  common_yes: "是",
  common_no: "否",
  common_dash: "-",
  common_retry: "重试",

  notice_unknown_error: "发生未知错误，请稍后重试",
  notice_init_failed: "初始化任务数据失败：{error}",
  notice_create_task_success: "任务已创建并加入下载队列",
  notice_create_task_failed: "创建任务失败：{error}",
  notice_cancel_task_success: "任务已取消",
  notice_cancel_task_failed: "取消任务失败：{error}",
  notice_delete_task_success: "任务已从队列删除",
  notice_delete_task_failed: "删除队列任务失败：{error}",
  notice_cookie_import_success: "cookies.txt 校验通过",
  notice_cookie_import_failed: "Cookie 文件校验失败：{error}",
  notice_history_refresh_failed: "刷新历史失败：{error}",
  notice_history_delete_success: "历史记录已删除",
  notice_history_delete_failed: "删除历史记录失败：{error}",
  notice_history_clear_success: "历史记录已清空",
  notice_history_clear_failed: "清空历史记录失败：{error}",
  notice_ytdlp_check_success: "yt-dlp 更新状态已刷新",
  notice_ytdlp_check_failed: "检查 yt-dlp 失败：{error}",
  notice_ytdlp_update_success: "yt-dlp 已完成下载/更新",
  notice_ytdlp_update_failed: "更新 yt-dlp 失败：{error}",
  notice_ffmpeg_check_success: "ffmpeg 更新状态已刷新",
  notice_ffmpeg_check_failed: "检查 ffmpeg 失败：{error}",
  notice_ffmpeg_update_success: "ffmpeg 已完成下载/更新",
  notice_ffmpeg_update_failed: "更新 ffmpeg 失败：{error}",
  notice_dependency_check_failed: "读取本地依赖状态失败：{error}",
  notice_settings_load_failed: "读取应用设置失败：{error}",
  notice_settings_save_success: "并发下载设置已保存",
  notice_settings_save_failed: "保存应用设置失败：{error}",

  download_title: "创建下载任务",
  download_desc: "粘贴链接，选择输出目录与格式，然后加入队列。",
  download_label_url: "视频链接",
  download_placeholder_url: "https://www.youtube.com/watch?v=...",
  download_label_output_dir: "输出目录",
  download_label_format_id: "格式 ID（可选）",
  download_placeholder_format_id: "bestvideo+bestaudio",
  download_label_resolution: "分辨率（可选）",
  download_placeholder_resolution: "1080",
  download_label_cookie_mode: "Cookie 模式",
  download_cookie_tip_toggle: "i",
  download_cookie_tip_text_prefix: "当从浏览器读取的 cookie 不可用时，可通过“",
  download_cookie_tip_text_suffix: "”浏览器插件手动获取 cookies.txt 文件并导入使用。",
  download_cookie_tip_link_text: "Get cookies.txt LOCALLY",
  download_cookie_mode_none: "不使用",
  download_cookie_mode_file: "导入 cookies.txt",
  download_cookie_mode_browser: "浏览器读取",
  download_label_cookie_browser: "浏览器来源",
  download_cookie_browser_chrome: "Chrome",
  download_cookie_browser_edge: "Edge",
  download_placeholder_cookie_path: "cookies.txt 路径",
  download_submit: "添加任务",
  download_submitting: "正在创建任务...",

  queue_title: "下载队列",
  queue_empty_title: "当前没有下载任务",
  queue_empty_desc: "请到“下载”页面创建任务，任务会自动进入这里并实时更新。",
  queue_table_url: "链接",
  queue_table_status: "状态",
  queue_table_progress: "进度",
  queue_table_action: "操作",
  queue_action_cancel: "取消",
  queue_action_delete: "删除",

  history_title: "历史记录",
  history_empty_title: "暂无历史记录",
  history_empty_desc: "当任务结束后，记录会保存到这里，方便你回看结果。",
  history_action_delete: "删除",
  history_action_clear_all: "清空历史",

  settings_title: "设置与依赖管理",
  settings_desc: "这里可以检查并更新 yt-dlp 与 ffmpeg，每次操作都会有状态反馈。",
  settings_ytdlp_title: "yt-dlp 版本信息",
  settings_ffmpeg_title: "ffmpeg 版本信息",
  settings_label_installed_version: "已安装版本",
  settings_label_latest_version: "最新版本",
  settings_label_need_update: "需要更新",
  settings_label_binary_path: "本地路径",
  settings_label_latest_release_id: "最新发布 ID",
  settings_label_latest_published_at: "最新发布时间",
  settings_label_local_release_id: "本地发布 ID",
  settings_button_check_update: "检查更新",
  settings_button_checking: "检查中...",
  settings_button_update_ytdlp: "下载/更新 yt-dlp",
  settings_button_update_ffmpeg: "下载/更新 ffmpeg",
  settings_button_updating: "下载中，请稍候...",
  settings_button_saving: "保存中...",
  settings_download_title: "下载并发设置",
  settings_label_download_concurrency: "并发下载数量",
  settings_download_concurrency_hint: "范围 {min}-{max}，默认 {defaultValue}。该设置会持久化保存并立即应用。",
  settings_button_save: "保存设置",
  settings_meta: "后端地址：{backendUrl}",
  settings_installed_unchecked: "已安装（未检查版本）",

  task_status_pending: "排队中",
  task_status_running: "下载中",
  task_status_completed: "已完成",
  task_status_failed: "失败",
  task_status_canceled: "已取消",
  terminal_title: "实时终端输出",
  terminal_clear: "清空输出",
  terminal_empty: "终端已开启，等待新的命令和输出...",
  terminal_stream_command: "命令",
  terminal_stream_stdout: "输出",
  terminal_stream_status: "状态",
  footer_copyright: "版权所有 © {year} YueHeng。保留所有权利。",
  footer_contact: "联系方式 QQ:368950794",
  footer_based_on_prefix: "本项目使用 ",
  footer_based_on_link_text: "yt-dlp",
  footer_based_on_suffix: "，仓库地址如链接所示。"
};

const EN: MessageDict = {
  app_brand_short: "yt",
  app_brand_title: "yt-dlp GUI",
  nav_download: "Download",
  nav_queue: "Queue",
  nav_history: "History",
  nav_settings: "Settings",
  nav_language_label: "Language",
  nav_language_zh_cn: "中文",
  nav_language_en: "English",
  nav_terminal_show: "Show Terminal",
  nav_terminal_hide: "Hide Terminal",
  hero_title: "The easiest local yt-dlp GUI",
  hero_subtitle: "Docs-style UI with traceable download and update feedback.",
  common_close: "Close",
  common_refresh: "Refresh",
  common_refreshing: "Refreshing...",
  common_select: "Select",
  common_select_file: "Select file",
  common_not_installed: "Not installed",
  common_unknown: "Unknown",
  common_yes: "Yes",
  common_no: "No",
  common_dash: "-",
  common_retry: "Retry",

  notice_unknown_error: "Unknown error occurred, please try again later",
  notice_init_failed: "Failed to initialize tasks: {error}",
  notice_create_task_success: "Task created and added to queue",
  notice_create_task_failed: "Failed to create task: {error}",
  notice_cancel_task_success: "Task canceled",
  notice_cancel_task_failed: "Failed to cancel task: {error}",
  notice_delete_task_success: "Task removed from queue",
  notice_delete_task_failed: "Failed to remove queue task: {error}",
  notice_cookie_import_success: "cookies.txt validated",
  notice_cookie_import_failed: "Cookie file validation failed: {error}",
  notice_history_refresh_failed: "Failed to refresh history: {error}",
  notice_history_delete_success: "History item deleted",
  notice_history_delete_failed: "Failed to delete history item: {error}",
  notice_history_clear_success: "History cleared",
  notice_history_clear_failed: "Failed to clear history: {error}",
  notice_ytdlp_check_success: "yt-dlp update status refreshed",
  notice_ytdlp_check_failed: "Failed to check yt-dlp: {error}",
  notice_ytdlp_update_success: "yt-dlp downloaded/updated",
  notice_ytdlp_update_failed: "Failed to update yt-dlp: {error}",
  notice_ffmpeg_check_success: "ffmpeg update status refreshed",
  notice_ffmpeg_check_failed: "Failed to check ffmpeg: {error}",
  notice_ffmpeg_update_success: "ffmpeg downloaded/updated",
  notice_ffmpeg_update_failed: "Failed to update ffmpeg: {error}",
  notice_dependency_check_failed: "Failed to read local dependency state: {error}",
  notice_settings_load_failed: "Failed to load app settings: {error}",
  notice_settings_save_success: "Concurrent download setting saved",
  notice_settings_save_failed: "Failed to save app settings: {error}",

  download_title: "Create Download Task",
  download_desc: "Paste a URL, choose output and format, then enqueue it.",
  download_label_url: "Video URL",
  download_placeholder_url: "https://www.youtube.com/watch?v=...",
  download_label_output_dir: "Output Directory",
  download_label_format_id: "Format ID (optional)",
  download_placeholder_format_id: "bestvideo+bestaudio",
  download_label_resolution: "Resolution (optional)",
  download_placeholder_resolution: "1080",
  download_label_cookie_mode: "Cookie Mode",
  download_cookie_tip_toggle: "i",
  download_cookie_tip_text_prefix: "When browser cookies are unavailable, you can use the “",
  download_cookie_tip_text_suffix: "” browser extension to manually export cookies.txt and import it here.",
  download_cookie_tip_link_text: "Get cookies.txt LOCALLY",
  download_cookie_mode_none: "Do not use",
  download_cookie_mode_file: "Import cookies.txt",
  download_cookie_mode_browser: "Read from browser",
  download_label_cookie_browser: "Browser Source",
  download_cookie_browser_chrome: "Chrome",
  download_cookie_browser_edge: "Edge",
  download_placeholder_cookie_path: "cookies.txt path",
  download_submit: "Add Task",
  download_submitting: "Creating...",

  queue_title: "Download Queue",
  queue_empty_title: "No tasks in queue",
  queue_empty_desc: "Create tasks in Download page and watch live updates here.",
  queue_table_url: "URL",
  queue_table_status: "Status",
  queue_table_progress: "Progress",
  queue_table_action: "Action",
  queue_action_cancel: "Cancel",
  queue_action_delete: "Delete",

  history_title: "History",
  history_empty_title: "No history yet",
  history_empty_desc: "Finished tasks will be listed here for quick review.",
  history_action_delete: "Delete",
  history_action_clear_all: "Clear History",

  settings_title: "Settings & Dependencies",
  settings_desc: "Check and update yt-dlp and ffmpeg with clear feedback.",
  settings_ytdlp_title: "yt-dlp Version Info",
  settings_ffmpeg_title: "ffmpeg Version Info",
  settings_label_installed_version: "Installed Version",
  settings_label_latest_version: "Latest Version",
  settings_label_need_update: "Needs Update",
  settings_label_binary_path: "Binary Path",
  settings_label_latest_release_id: "Latest Release ID",
  settings_label_latest_published_at: "Latest Published At",
  settings_label_local_release_id: "Local Release ID",
  settings_button_check_update: "Check Update",
  settings_button_checking: "Checking...",
  settings_button_update_ytdlp: "Download/Update yt-dlp",
  settings_button_update_ffmpeg: "Download/Update ffmpeg",
  settings_button_updating: "Downloading...",
  settings_button_saving: "Saving...",
  settings_download_title: "Download Concurrency",
  settings_label_download_concurrency: "Concurrent Downloads",
  settings_download_concurrency_hint: "Range {min}-{max}, default {defaultValue}. This setting is persisted and applied immediately.",
  settings_button_save: "Save Settings",
  settings_meta: "Backend: {backendUrl}",
  settings_installed_unchecked: "Installed (version not checked)",

  task_status_pending: "Pending",
  task_status_running: "Running",
  task_status_completed: "Completed",
  task_status_failed: "Failed",
  task_status_canceled: "Canceled",
  terminal_title: "Live Terminal Output",
  terminal_clear: "Clear",
  terminal_empty: "Terminal is enabled. Waiting for new commands and logs...",
  terminal_stream_command: "CMD",
  terminal_stream_stdout: "OUT",
  terminal_stream_status: "STATUS",
  footer_copyright: "Copyright © {year} YueHeng. All rights reserved.",
  footer_contact: "Contact QQ: 368950794",
  footer_based_on_prefix: "This project uses ",
  footer_based_on_link_text: "yt-dlp",
  footer_based_on_suffix: " (repository linked)."
};

const DICTS: Record<Locale, MessageDict> = {
  "zh-CN": ZH_CN,
  en: EN
};

const LOCALE_STORAGE_KEY = "yt_dlp_gui_locale";

function isSupportedLocale(locale: string): locale is Locale {
  return locale === "zh-CN" || locale === "en";
}

function detectLocale(): Locale {
  if (typeof navigator === "undefined") return "zh-CN";
  const lang = navigator.language.toLowerCase();
  return lang.startsWith("zh") ? "zh-CN" : "en";
}

function loadInitialLocale(): Locale {
  if (typeof localStorage !== "undefined") {
    const savedLocale = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (savedLocale && isSupportedLocale(savedLocale)) return savedLocale;
  }
  return detectLocale();
}

/**
 * 当前语言是响应式状态：
 * - 切换语言后，依赖 t() 的页面会自动重渲染，不需要刷新应用。
 */
export const locale_ref = ref<Locale>(loadInitialLocale());

export function setLocale(locale: Locale) {
  locale_ref.value = locale;
  if (typeof localStorage !== "undefined") {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  }
}

export function t(key: string, vars?: Record<string, string | number>): string {
  const template = DICTS[locale_ref.value][key] ?? DICTS["zh-CN"][key] ?? key;
  if (!vars) return template;
  return Object.entries(vars).reduce((text, [varKey, value]) => {
    return text.replaceAll(`{${varKey}}`, String(value));
  }, template);
}

export function taskStatusText(status: string): string {
  return t(`task_status_${status}`);
}
