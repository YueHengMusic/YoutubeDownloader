import { defineStore } from "pinia";
import {
  apiClient,
  connectTaskWs,
  fetchDependencyStatus,
  fetchFfmpegUpdateStatus,
  fetchYtDlpUpdateStatus,
  triggerFfmpegUpdate,
  triggerYtDlpUpdate,
  type CreateTaskPayload,
  type DependencyStatus,
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
export type TerminalStreamType = "command" | "stdout" | "status";

export type TerminalLogLine = {
  id: number;
  task_id: string;
  stream: TerminalStreamType;
  text: string;
  created_at: number;
};

type TaskWsEvent =
  | { type: "task_update"; data: UiTask }
  | { type: "terminal_output"; data: { task_id: string; stream: TerminalStreamType; text: string } };

export const useTaskStore = defineStore("tasks", {
  state: () => ({
    tasks: [] as UiTask[],
    history: [] as UiTask[],
    ws: null as WebSocket | null,
    ytDlpStatus: null as YtDlpUpdateStatus | null,
    ffmpegStatus: null as FfmpegUpdateStatus | null,
    dependencyStatus: null as DependencyStatus | null,
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
    isUpdatingFfmpeg: false,
    isCheckingDependencyStatus: false,
    // 终端面板默认开启，用户进入应用时可立即看到后台执行输出。
    terminalPanelVisible: true,
    terminalLogs: [] as TerminalLogLine[],
    terminalLogIdSeed: 0,
    wsReconnectTimer: null as ReturnType<typeof setTimeout> | null
  }),
  actions: {
    isTimeoutError(error: unknown): boolean {
      if (typeof error !== "object" || error === null) return false;
      const maybe = error as { code?: string; message?: string };
      if (maybe.code === "ECONNABORTED") return true;
      return typeof maybe.message === "string" && maybe.message.toLowerCase().includes("timeout");
    },
    async runWithRetryOnceOnTimeout<T>(requestFn: () => Promise<T>): Promise<T> {
      /**
       * 统一“超时重试一次”兜底：
       * - 仅在超时场景重试一次，避免把业务错误（如 400/404）误重试；
       * - 重试失败后抛出原异常，让上层按原有提示逻辑处理。
       */
      try {
        return await requestFn();
      } catch (error) {
        if (!this.isTimeoutError(error)) throw error;
      }
      return await requestFn();
    },
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
        const { data } = await this.runWithRetryOnceOnTimeout(() => apiClient.get<UiTask[]>("/api/tasks"));
        this.tasks = data;
        const historyResp = await this.runWithRetryOnceOnTimeout(() => apiClient.get<UiTask[]>("/api/history"));
        this.history = historyResp.data;
      } catch (error) {
        this.showNotice("error", t("notice_init_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        // 即便初始化接口失败，也要尝试连 WS，避免后端稍后恢复后仍然没有实时事件。
        this.connectWs();
        this.isRefreshingTasks = false;
      }
    },
    connectWs() {
      // 连接中/已连接则不重复创建；已关闭/已断开时允许重连。
      if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) return;
      const ws = connectTaskWs((event: TaskWsEvent) => {
        if (event.type === "task_update") {
          const task = event.data as UiTask;
          // 就地更新数组项，保持 Vue 响应式和列表顺序稳定。
          const idx = this.tasks.findIndex((item) => item.id === task.id);
          if (idx >= 0) this.tasks[idx] = task;
          else this.tasks.unshift(task);
          return;
        }
        if (event.type === "terminal_output") {
          const payload = event.data;
          // 兜底字段，避免后端某些系统事件缺字段导致前端完全不显示日志。
          const taskId = payload.task_id || "system";
          const stream = payload.stream || "stdout";
          const text = payload.text || "";
          this.pushTerminalLog(taskId, stream, text);
        }
      });
      this.ws = ws;

      ws.onopen = () => {
        if (this.wsReconnectTimer) {
          clearTimeout(this.wsReconnectTimer);
          this.wsReconnectTimer = null;
        }
      };
      ws.onclose = () => {
        this.ws = null;
        this.scheduleWsReconnect();
      };
      ws.onerror = () => {
        // 某些环境下 onerror 不一定触发 onclose，这里主动关闭确保进入统一重连逻辑。
        try {
          ws.close();
        } catch {
          // ignore
        }
      };
    },
    scheduleWsReconnect() {
      if (this.wsReconnectTimer) return;
      this.wsReconnectTimer = setTimeout(() => {
        this.wsReconnectTimer = null;
        this.connectWs();
      }, 1500);
    },
    async ensureWsReady(timeoutMs = 1200) {
      // 对“短时操作日志”（如版本检查）做兜底：先尽力确保 WS 连上，避免事件瞬间发完被错过。
      this.connectWs();
      if (this.ws?.readyState === WebSocket.OPEN) return;
      await new Promise<void>((resolve) => {
        const ws = this.ws;
        if (!ws) {
          resolve();
          return;
        }
        let done = false;
        const finish = () => {
          if (done) return;
          done = true;
          resolve();
        };
        const timer = setTimeout(() => {
          ws.removeEventListener("open", onOpen);
          finish();
        }, timeoutMs);
        const onOpen = () => {
          clearTimeout(timer);
          ws.removeEventListener("open", onOpen);
          finish();
        };
        ws.addEventListener("open", onOpen);
      });
    },
    toggleTerminalPanel() {
      this.terminalPanelVisible = !this.terminalPanelVisible;
    },
    clearTerminalLogs() {
      this.terminalLogs = [];
    },
    pushTerminalLog(taskId: string, stream: TerminalStreamType, text: string) {
      // 终端日志是高频数据，限制最大条数避免长时间运行后内存持续增长。
      this.terminalLogIdSeed += 1;
      this.terminalLogs.push({
        id: this.terminalLogIdSeed,
        task_id: taskId,
        stream,
        text,
        created_at: Date.now()
      });
      const maxLogCount = 300;
      if (this.terminalLogs.length > maxLogCount) {
        this.terminalLogs.splice(0, this.terminalLogs.length - maxLogCount);
      }
    },
    async createTask(payload: CreateTaskPayload) {
      this.isSubmittingTask = true;
      try {
        // 下载任务会在后端 worker 中立即产生命令与终端输出，先确保 WS 就绪，避免首批日志丢失。
        await this.ensureWsReady();
        const { data } = await this.runWithRetryOnceOnTimeout(() => apiClient.post<UiTask>("/api/tasks", payload));
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
        await this.runWithRetryOnceOnTimeout(() => apiClient.post(`/api/tasks/${taskId}/cancel`));
        this.showNotice("info", t("notice_cancel_task_success"));
      } catch (error) {
        this.showNotice("error", t("notice_cancel_task_failed", { error: this.extractErrorMessage(error) }));
      }
    },
    async deleteTask(taskId: string) {
      try {
        await this.runWithRetryOnceOnTimeout(() => apiClient.delete(`/api/tasks/${taskId}`));
        // 删除成功后本地同步移除，避免必须手动刷新才能看到结果。
        this.tasks = this.tasks.filter((item) => item.id !== taskId);
        this.showNotice("success", t("notice_delete_task_success"));
      } catch (error) {
        this.showNotice("error", t("notice_delete_task_failed", { error: this.extractErrorMessage(error) }));
      }
    },
    async importCookie(path: string) {
      try {
        await this.runWithRetryOnceOnTimeout(() => apiClient.post("/api/cookies/import", { path }));
        this.showNotice("success", t("notice_cookie_import_success"));
      } catch (error) {
        this.showNotice("error", t("notice_cookie_import_failed", { error: this.extractErrorMessage(error) }));
        throw error;
      }
    },
    async refreshHistory() {
      this.isRefreshingHistory = true;
      try {
        const { data } = await this.runWithRetryOnceOnTimeout(() => apiClient.get<UiTask[]>("/api/history"));
        this.history = data;
      } catch (error) {
        this.showNotice("error", t("notice_history_refresh_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isRefreshingHistory = false;
      }
    },
    async deleteHistoryItem(taskId: string) {
      try {
        await this.runWithRetryOnceOnTimeout(() => apiClient.delete(`/api/history/${taskId}`));
        this.history = this.history.filter((item) => item.id !== taskId);
        this.showNotice("success", t("notice_history_delete_success"));
      } catch (error) {
        this.showNotice("error", t("notice_history_delete_failed", { error: this.extractErrorMessage(error) }));
      }
    },
    async clearHistory() {
      try {
        await this.runWithRetryOnceOnTimeout(() => apiClient.delete("/api/history"));
        this.history = [];
        this.showNotice("success", t("notice_history_clear_success"));
      } catch (error) {
        this.showNotice("error", t("notice_history_clear_failed", { error: this.extractErrorMessage(error) }));
      }
    },
    async refreshYtDlpStatus() {
      this.isCheckingYtDlp = true;
      try {
        await this.ensureWsReady();
        this.ytDlpStatus = await this.runWithRetryOnceOnTimeout(() => fetchYtDlpUpdateStatus());
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
        await this.ensureWsReady();
        await this.runWithRetryOnceOnTimeout(() => triggerYtDlpUpdate());
        await this.refreshYtDlpStatus();
        await this.refreshDependencyStatus();
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
        await this.ensureWsReady();
        this.ffmpegStatus = await this.runWithRetryOnceOnTimeout(() => fetchFfmpegUpdateStatus());
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
        await this.ensureWsReady();
        await this.runWithRetryOnceOnTimeout(() => triggerFfmpegUpdate());
        await this.refreshFfmpegStatus();
        await this.refreshDependencyStatus();
        this.showNotice("success", t("notice_ffmpeg_update_success"));
      } catch (error) {
        this.showNotice("error", t("notice_ffmpeg_update_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isUpdatingFfmpeg = false;
      }
    },
    async refreshDependencyStatus() {
      this.isCheckingDependencyStatus = true;
      try {
        // 这里只检查本地二进制文件是否存在，不会触发 GitHub 远程版本请求。
        this.dependencyStatus = await this.runWithRetryOnceOnTimeout(() => fetchDependencyStatus());
      } catch (error) {
        this.showNotice("error", t("notice_dependency_check_failed", { error: this.extractErrorMessage(error) }));
      } finally {
        this.isCheckingDependencyStatus = false;
      }
    }
  }
});
