import { defineStore } from "pinia";
import {
  apiClient,
  connectTaskWs,
  fetchFfmpegUpdateStatus,
  fetchYtDlpUpdateStatus,
  triggerFfmpegUpdate,
  triggerYtDlpUpdate,
  type CreateTaskPayload,
  type FfmpegUpdateStatus,
  type YtDlpUpdateStatus
} from "@/api/client";

export type UiTask = {
  id: string;
  url: string;
  status: "pending" | "running" | "completed" | "failed" | "canceled";
  progress: number;
  speed?: string;
  eta?: string;
  log: string;
  error?: string;
  output_dir: string;
  updated_at: string;
};

export const useTaskStore = defineStore("tasks", {
  state: () => ({
    tasks: [] as UiTask[],
    history: [] as UiTask[],
    ws: null as WebSocket | null,
    ytDlpStatus: null as YtDlpUpdateStatus | null,
    ffmpegStatus: null as FfmpegUpdateStatus | null
  }),
  actions: {
    async init() {
      // 页面首次加载时：同步读取当前任务 + 历史记录。
      const { data } = await apiClient.get<UiTask[]>("/api/tasks");
      this.tasks = data;
      const historyResp = await apiClient.get<UiTask[]>("/api/history");
      this.history = historyResp.data;
      this.connectWs();
    },
    connectWs() {
      if (this.ws) return;
      this.ws = connectTaskWs((event) => {
        if (event.type !== "task_update") return;
        const task = event.data as UiTask;
        // 就地更新数组项，保持 Vue 响应式和列表顺序稳定。
        const idx = this.tasks.findIndex((item) => item.id === task.id);
        if (idx >= 0) this.tasks[idx] = task;
        else this.tasks.unshift(task);
      });
    },
    async createTask(payload: CreateTaskPayload) {
      const { data } = await apiClient.post<UiTask>("/api/tasks", payload);
      this.tasks.unshift(data);
    },
    async cancelTask(taskId: string) {
      await apiClient.post(`/api/tasks/${taskId}/cancel`);
    },
    async importCookie(path: string) {
      await apiClient.post("/api/cookies/import", { path });
    },
    async refreshHistory() {
      const { data } = await apiClient.get<UiTask[]>("/api/history");
      this.history = data;
    },
    async refreshYtDlpStatus() {
      this.ytDlpStatus = await fetchYtDlpUpdateStatus();
    },
    async updateYtDlp() {
      await triggerYtDlpUpdate();
      await this.refreshYtDlpStatus();
    },
    async refreshFfmpegStatus() {
      this.ffmpegStatus = await fetchFfmpegUpdateStatus();
    },
    async updateFfmpeg() {
      await triggerFfmpegUpdate();
      await this.refreshFfmpegStatus();
    }
  }
});
