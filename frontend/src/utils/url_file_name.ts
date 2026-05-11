/**
 * 从 URL 中提取可读文件名：
 * - 取 pathname 最后一段作为候选名。
 * - 自动执行 URL 解码，便于展示中文和空格等字符。
 * - 无法提取时返回调用方提供的兜底文案（用于 i18n）。
 */
export function get_file_name_from_url(url: string, fallback_text: string): string {
  try {
    const parsed_url = new URL(url);
    const raw_name = parsed_url.pathname.split("/").filter(Boolean).pop();
    if (!raw_name) return fallback_text;
    return decodeURIComponent(raw_name);
  } catch {
    return fallback_text;
  }
}
