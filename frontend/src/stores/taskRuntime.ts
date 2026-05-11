import { defineStore } from "pinia";
import { apiClient, type CreateTaskPayload } from "@/api/client";
import { t } from "@/i18n/strings";
import { extractErrorMessage, runWithRetryOnceOnTimeout } from "@/stores/apiHelpers";
import { useRealtimeTaskStore } from "@/stores/realtime";
import { useUiStore } from "@/stores/ui";
import type { UiTask } from "@/stores/types";

export const useTaskRuntimeStore = defineStore("taskRuntime", {
  state: () => ({
    tasks: [] as UiTask[],
    isSubmittingTask: false,
    isRefreshingTasks: false
  }),
  actions: {
    upsertTask(task: UiTask) {
      const idx = this.tasks.findIndex((item) => item.id === task.id);
      if (idx >= 0) this.tasks[idx] = task;
      else this.tasks.unshift(task);
    },
    async refreshTasks() {
      const ui = useUiStore();
      this.isRefreshingTasks = true;
      try {
        const { data } = await runWithRetryOnceOnTimeout(() => apiClient.get<UiTask[]>("/api/tasks"));
        this.tasks = data;
      } catch (error) {
        ui.showNotice("error", t("notice_init_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isRefreshingTasks = false;
      }
    },
    async createTask(payload: CreateTaskPayload) {
      const ui = useUiStore();
      const realtime = useRealtimeTaskStore();
      this.isSubmittingTask = true;
      try {
        await realtime.ensureWsReady();
        const { data } = await runWithRetryOnceOnTimeout(() => apiClient.post<UiTask>("/api/tasks", payload));
        this.upsertTask(data);
        ui.showNotice("success", t("notice_create_task_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_create_task_failed", { error: extractErrorMessage(error) }));
        throw error;
      } finally {
        this.isSubmittingTask = false;
      }
    },
    async cancelTask(taskId: string) {
      const ui = useUiStore();
      try {
        await runWithRetryOnceOnTimeout(() => apiClient.post(`/api/tasks/${taskId}/cancel`));
        ui.showNotice("info", t("notice_cancel_task_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_cancel_task_failed", { error: extractErrorMessage(error) }));
      }
    },
    async deleteTask(taskId: string) {
      const ui = useUiStore();
      try {
        await runWithRetryOnceOnTimeout(() => apiClient.delete(`/api/tasks/${taskId}`));
        this.tasks = this.tasks.filter((item) => item.id !== taskId);
        ui.showNotice("success", t("notice_delete_task_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_delete_task_failed", { error: extractErrorMessage(error) }));
      }
    },
    async importCookie(path: string) {
      const ui = useUiStore();
      try {
        await runWithRetryOnceOnTimeout(() => apiClient.post("/api/cookies/import", { path }));
        ui.showNotice("success", t("notice_cookie_import_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_cookie_import_failed", { error: extractErrorMessage(error) }));
        throw error;
      }
    }
  }
});
