import axios from "axios";

// =======================
// API 客户端统一入口
// =======================
// 这里集中管理后端地址和超时，避免每个页面写一份重复配置。
export const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000
});

export type CreateTaskPayload = {
  url: string;
  output_dir: string;
  download_target?: "video" | "audio" | "thumbnail";
  format_id?: string;
  resolution?: string;
  resolution_mode?: "prefer" | "limit";
  audio_format?: "mp3" | "m4a" | "opus" | "wav" | "flac";
  subtitle_mode?: "none" | "manual" | "auto" | "all";
  subtitle_langs?: string;
  write_info_json?: boolean;
  write_description?: boolean;
  write_thumbnail?: boolean;
  embed_thumbnail?: boolean;
  cookie_mode: "none" | "file" | "browser";
  cookie_value?: string;
};

export type YtDlpUpdateStatus = {
  installed_version: string | null;
  latest_version: string;
  has_update: boolean;
  binary_path: string;
};

export type FfmpegUpdateStatus = {
  installed_version: string | null;
  latest_release_id: number;
  latest_tag_name: string;
  latest_published_at: string;
  local_release_id: number | null;
  has_update: boolean;
  binary_path: string;
};

export type DependencyStatus = {
  yt_dlp: {
    path: string;
    exists: boolean;
    installing: boolean;
  };
  ffmpeg: {
    path: string;
    exists: boolean;
    installing: boolean;
  };
};

export type AppSettings = {
  download_concurrency: number;
  min_download_concurrency: number;
  max_download_concurrency: number;
  default_download_concurrency: number;
};

// 下载任务实时进度 websocket 连接入口。
export function connectTaskWs(onMessage: (data: any) => void): WebSocket {
  const ws = new WebSocket("ws://127.0.0.1:8000/ws/tasks");
  ws.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      // 后端偶发脏数据时忽略，避免前端直接崩溃。
    }
  };
  return ws;
}

export async function fetchYtDlpUpdateStatus(): Promise<YtDlpUpdateStatus> {
  const { data } = await apiClient.get<YtDlpUpdateStatus>("/api/system/yt-dlp/update-status");
  return data;
}

export async function triggerYtDlpUpdate(): Promise<Record<string, unknown>> {
  const { data } = await apiClient.post<Record<string, unknown>>("/api/system/yt-dlp/update");
  return data;
}

export async function fetchFfmpegUpdateStatus(): Promise<FfmpegUpdateStatus> {
  const { data } = await apiClient.get<FfmpegUpdateStatus>("/api/system/ffmpeg/update-status");
  return data;
}

export async function triggerFfmpegUpdate(): Promise<Record<string, unknown>> {
  const { data } = await apiClient.post<Record<string, unknown>>("/api/system/ffmpeg/update");
  return data;
}

export async function fetchDependencyStatus(): Promise<DependencyStatus> {
  const { data } = await apiClient.get<DependencyStatus>("/api/system/dependencies");
  return data;
}

export async function fetchAppSettings(): Promise<AppSettings> {
  const { data } = await apiClient.get<AppSettings>("/api/system/settings");
  return data;
}

export async function updateAppSettings(downloadConcurrency: number): Promise<AppSettings> {
  const { data } = await apiClient.put<AppSettings>("/api/system/settings", {
    download_concurrency: downloadConcurrency
  });
  return data;
}
