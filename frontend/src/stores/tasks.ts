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
import { t } from "@/i18n/strings";

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

export type NoticeType = "success" | "error" | "info";

export const useTaskStore = defineStore("tasks", {
  state: () => ({
    tasks: [] as UiTask[],
    history: [] as UiTask[],
    ws: null as WebSocket | null,
    ytDlpStatus: null as YtDlpUpdateStatus | null,
    ffmpegStatus: null as FfmpegUpdateStatus | null,
    notice: {
      visible: false,
      type: "info" as NoticeType,
      message: "",
      nonce: 0
    },
    isSubmittingTask: false,
    isRefreshingTasks: false,
    isRefreshingHistory: false,
    isCheckingYtDlp: false,
    isUpdatingYtDlp: false,
    isCheckingFfmpeg: false,
    isUpdatingFfmpeg: false
  }),
  actions: {
    showNotice(type: NoticeType, message: string) {
      // 每次提示都递增 nonce，确保“相同 visible 状态下的新提示”也能触发 UI 刷新与计时重置。
      this.notice = { visible: true, type, message, nonce: this.notice.nonce + 1 };
    },
    clearNotice() {
      this.notice.visible = false;
      this.notice.message = "";
    },
    extractErrorMessage(error: unknown): string {
      if (typeof error === "object" && error !== null) {
        const maybe = error as { response?: { data?: { detail?: string } }; message?: string };
        if (maybe.response?.data?.detail) return maybe.response.data.detail;
        if (maybe.message) return maybe.message;
      }
      return t("notice_unknown_error");
    },
    async init() {
      this.isRefreshingTasks = true;
      try {
        // 页面首次加载时：同步读取当前任务 + 历史记录。
        const { data } = await apiClient.get<UiTask[]>("/api/tasks");
        this.tasks = data;
        const historyResp = await apiClient.get<UiTask[]>("/api/history");
        this.history = historyResp.data;
        this.connectWs();
      } catch (error) {
        this.showNotice("error", t("notice_init_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isRefreshingTasks = false;
      }
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
      this.isSubmittingTask = true;
      try {
        const { data } = await apiClient.post<UiTask>("/api/tasks", payload);
        this.tasks.unshift(data);
        this.showNotice("success", t("notice_create_task_success"));
      } catch (error) {
        this.showNotice("error", t("notice_create_task_failed", { error: this.extractErrorMessage(error) }));
        throw error;
      } finally {
        this.isSubmittingTask = false;
      }
    },
    async cancelTask(taskId: string) {
      try {
        await apiClient.post(`/api/tasks/${taskId}/cancel`);
        this.showNotice("info", t("notice_cancel_task_success"));
      } catch (error) {
        this.showNotice("error", t("notice_cancel_task_failed", { error: this.extractErrorMessage(error) }));
      }
    },
    async importCookie(path: string) {
      try {
        await apiClient.post("/api/cookies/import", { path });
        this.showNotice("success", t("notice_cookie_import_success"));
      } catch (error) {
        this.showNotice("error", t("notice_cookie_import_failed", { error: this.extractErrorMessage(error) }));
        throw error;
      }
    },
    async refreshHistory() {
      this.isRefreshingHistory = true;
      try {
        const { data } = await apiClient.get<UiTask[]>("/api/history");
        this.history = data;
      } catch (error) {
        this.showNotice("error", t("notice_history_refresh_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isRefreshingHistory = false;
      }
    },
    async refreshYtDlpStatus() {
      this.isCheckingYtDlp = true;
      try {
        this.ytDlpStatus = await fetchYtDlpUpdateStatus();
        this.showNotice("info", t("notice_ytdlp_check_success"));
      } catch (error) {
        this.showNotice("error", t("notice_ytdlp_check_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isCheckingYtDlp = false;
      }
    },
    async updateYtDlp() {
      this.isUpdatingYtDlp = true;
      try {
        await triggerYtDlpUpdate();
        await this.refreshYtDlpStatus();
        this.showNotice("success", t("notice_ytdlp_update_success"));
      } catch (error) {
        this.showNotice("error", t("notice_ytdlp_update_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isUpdatingYtDlp = false;
      }
    },
    async refreshFfmpegStatus() {
      this.isCheckingFfmpeg = true;
      try {
        this.ffmpegStatus = await fetchFfmpegUpdateStatus();
        this.showNotice("info", t("notice_ffmpeg_check_success"));
      } catch (error) {
        this.showNotice("error", t("notice_ffmpeg_check_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isCheckingFfmpeg = false;
      }
    },
    async updateFfmpeg() {
      this.isUpdatingFfmpeg = true;
      try {
        await triggerFfmpegUpdate();
        await this.refreshFfmpegStatus();
        this.showNotice("success", t("notice_ffmpeg_update_success"));
      } catch (error) {
        this.showNotice("error", t("notice_ffmpeg_update_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isUpdatingFfmpeg = false;
      }
    }
  }
});
