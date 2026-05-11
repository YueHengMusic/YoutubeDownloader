import { defineStore } from "pinia";
import { useHistoryStore } from "@/stores/history";
import { useRealtimeTaskStore } from "@/stores/realtime";
import { useSettingsStore } from "@/stores/settings";
import { useSystemStore } from "@/stores/system";
import { useTaskRuntimeStore } from "@/stores/taskRuntime";
import { useUiStore } from "@/stores/ui";

export type { NoticeType, TerminalLogLine, TerminalStreamType, UiTask } from "@/stores/types";

/**
 * 兼容层：保留历史 API 形状，内部全部转发到拆分后的领域 store。
 * 新代码请优先直接使用 taskRuntime/history/realtime/system/settings/ui store。
 */
export const useTaskStore = defineStore("tasks", {
  getters: {
    tasks: () => useTaskRuntimeStore().tasks,
    history: () => useHistoryStore().history,
    notice: () => useUiStore().notice,
    terminalLogs: () => useRealtimeTaskStore().terminalLogs,
    ytDlpStatus: () => useSystemStore().ytDlpStatus,
    ffmpegStatus: () => useSystemStore().ffmpegStatus,
    dependencyStatus: () => useSystemStore().dependencyStatus,
    appSettings: () => useSettingsStore().appSettings,
    isSubmittingTask: () => useTaskRuntimeStore().isSubmittingTask,
    isRefreshingTasks: () => useTaskRuntimeStore().isRefreshingTasks,
    isRefreshingHistory: () => useHistoryStore().isRefreshingHistory,
    isCheckingYtDlp: () => useSystemStore().isCheckingYtDlp,
    isUpdatingYtDlp: () => useSystemStore().isUpdatingYtDlp,
    isCheckingFfmpeg: () => useSystemStore().isCheckingFfmpeg,
    isUpdatingFfmpeg: () => useSystemStore().isUpdatingFfmpeg,
    isCheckingDependencyStatus: () => useSystemStore().isCheckingDependencyStatus,
    isRefreshingAppSettings: () => useSettingsStore().isRefreshingAppSettings,
    isSavingAppSettings: () => useSettingsStore().isSavingAppSettings,
    downloadConcurrencyInput: () => useSettingsStore().downloadConcurrencyInput
  },
  actions: {
    init() {
      return Promise.all([useTaskRuntimeStore().refreshTasks(), useHistoryStore().refreshHistory()]).then(() => undefined);
    },
    connectWs() {
      useRealtimeTaskStore().connectWs();
    },
    ensureWsReady(timeoutMs?: number) {
      return useRealtimeTaskStore().ensureWsReady(timeoutMs);
    },
    clearTerminalLogs() {
      useRealtimeTaskStore().clearTerminalLogs();
    },
    showNotice(type: "success" | "error" | "info", message: string) {
      useUiStore().showNotice(type, message);
    },
    clearNotice() {
      useUiStore().clearNotice();
    },
    createTask: (payload: Parameters<ReturnType<typeof useTaskRuntimeStore>["createTask"]>[0]) =>
      useTaskRuntimeStore().createTask(payload),
    cancelTask: (taskId: string) => useTaskRuntimeStore().cancelTask(taskId),
    deleteTask: (taskId: string) => useTaskRuntimeStore().deleteTask(taskId),
    importCookie: (path: string) => useTaskRuntimeStore().importCookie(path),
    refreshHistory: () => useHistoryStore().refreshHistory(),
    deleteHistoryItem: (taskId: string) => useHistoryStore().deleteHistoryItem(taskId),
    clearHistory: () => useHistoryStore().clearHistory(),
    refreshYtDlpStatus: () => useSystemStore().refreshYtDlpStatus(),
    updateYtDlp: () => useSystemStore().updateYtDlp(),
    refreshFfmpegStatus: () => useSystemStore().refreshFfmpegStatus(),
    updateFfmpeg: () => useSystemStore().updateFfmpeg(),
    refreshDependencyStatus: () => useSystemStore().refreshDependencyStatus(),
    refreshAppSettings: () => useSettingsStore().refreshAppSettings(),
    saveAppSettings: () => useSettingsStore().saveAppSettings(),
    setDownloadConcurrencyInput(value: number) {
      useSettingsStore().downloadConcurrencyInput = value;
    }
  }
});
