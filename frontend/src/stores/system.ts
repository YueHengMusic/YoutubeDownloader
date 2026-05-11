import { defineStore } from "pinia";
import {
  fetchDependencyStatus,
  fetchFfmpegUpdateStatus,
  fetchYtDlpUpdateStatus,
  triggerFfmpegUpdate,
  triggerYtDlpUpdate,
  type DependencyStatus,
  type FfmpegUpdateStatus,
  type YtDlpUpdateStatus
} from "@/api/client";
import { t } from "@/i18n/strings";
import { extractErrorMessage, runWithRetryOnceOnTimeout } from "@/stores/apiHelpers";
import { useRealtimeTaskStore } from "@/stores/realtime";
import { useUiStore } from "@/stores/ui";

export const useSystemStore = defineStore("system", {
  state: () => ({
    ytDlpStatus: null as YtDlpUpdateStatus | null,
    ffmpegStatus: null as FfmpegUpdateStatus | null,
    dependencyStatus: null as DependencyStatus | null,
    isCheckingYtDlp: false,
    isUpdatingYtDlp: false,
    isCheckingFfmpeg: false,
    isUpdatingFfmpeg: false,
    isCheckingDependencyStatus: false
  }),
  actions: {
    async refreshYtDlpStatus() {
      const ui = useUiStore();
      const realtime = useRealtimeTaskStore();
      this.isCheckingYtDlp = true;
      try {
        await realtime.ensureWsReady();
        this.ytDlpStatus = await runWithRetryOnceOnTimeout(() => fetchYtDlpUpdateStatus());
        ui.showNotice("info", t("notice_ytdlp_check_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_ytdlp_check_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isCheckingYtDlp = false;
      }
    },
    async updateYtDlp() {
      const ui = useUiStore();
      this.isUpdatingYtDlp = true;
      try {
        await useRealtimeTaskStore().ensureWsReady();
        await runWithRetryOnceOnTimeout(() => triggerYtDlpUpdate());
        await this.refreshYtDlpStatus();
        await this.refreshDependencyStatus();
        ui.showNotice("success", t("notice_ytdlp_update_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_ytdlp_update_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isUpdatingYtDlp = false;
      }
    },
    async refreshFfmpegStatus() {
      const ui = useUiStore();
      const realtime = useRealtimeTaskStore();
      this.isCheckingFfmpeg = true;
      try {
        await realtime.ensureWsReady();
        this.ffmpegStatus = await runWithRetryOnceOnTimeout(() => fetchFfmpegUpdateStatus());
        ui.showNotice("info", t("notice_ffmpeg_check_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_ffmpeg_check_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isCheckingFfmpeg = false;
      }
    },
    async updateFfmpeg() {
      const ui = useUiStore();
      this.isUpdatingFfmpeg = true;
      try {
        await useRealtimeTaskStore().ensureWsReady();
        await runWithRetryOnceOnTimeout(() => triggerFfmpegUpdate());
        await this.refreshFfmpegStatus();
        await this.refreshDependencyStatus();
        ui.showNotice("success", t("notice_ffmpeg_update_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_ffmpeg_update_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isUpdatingFfmpeg = false;
      }
    },
    async refreshDependencyStatus() {
      const ui = useUiStore();
      this.isCheckingDependencyStatus = true;
      try {
        this.dependencyStatus = await runWithRetryOnceOnTimeout(() => fetchDependencyStatus());
      } catch (error) {
        ui.showNotice("error", t("notice_dependency_check_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isCheckingDependencyStatus = false;
      }
    }
  }
});
