import { defineStore } from "pinia";
import { apiClient } from "@/api/client";
import { t } from "@/i18n/strings";
import { extractErrorMessage, runWithRetryOnceOnTimeout } from "@/stores/apiHelpers";
import { useUiStore } from "@/stores/ui";
import type { UiTask } from "@/stores/types";

export const useHistoryStore = defineStore("history", {
  state: () => ({
    history: [] as UiTask[],
    isRefreshingHistory: false
  }),
  actions: {
    async refreshHistory() {
      const ui = useUiStore();
      this.isRefreshingHistory = true;
      try {
        const { data } = await runWithRetryOnceOnTimeout(() => apiClient.get<UiTask[]>("/api/history"));
        this.history = data;
      } catch (error) {
        ui.showNotice("error", t("notice_history_refresh_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isRefreshingHistory = false;
      }
    },
    async deleteHistoryItem(taskId: string) {
      const ui = useUiStore();
      try {
        await runWithRetryOnceOnTimeout(() => apiClient.delete(`/api/history/${taskId}`));
        this.history = this.history.filter((item) => item.id !== taskId);
        ui.showNotice("success", t("notice_history_delete_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_history_delete_failed", { error: extractErrorMessage(error) }));
      }
    },
    async clearHistory() {
      const ui = useUiStore();
      try {
        await runWithRetryOnceOnTimeout(() => apiClient.delete("/api/history"));
        this.history = [];
        ui.showNotice("success", t("notice_history_clear_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_history_clear_failed", { error: extractErrorMessage(error) }));
      }
    }
  }
});
