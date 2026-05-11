import { defineStore } from "pinia";
import { fetchAppSettings, updateAppSettings, type AppSettings } from "@/api/client";
import { t } from "@/i18n/strings";
import { extractErrorMessage, runWithRetryOnceOnTimeout } from "@/stores/apiHelpers";
import { useUiStore } from "@/stores/ui";

export const useSettingsStore = defineStore("settings", {
  state: () => ({
    appSettings: null as AppSettings | null,
    isRefreshingAppSettings: false,
    isSavingAppSettings: false,
    downloadConcurrencyInput: 2
  }),
  actions: {
    async refreshAppSettings() {
      const ui = useUiStore();
      this.isRefreshingAppSettings = true;
      try {
        this.appSettings = await runWithRetryOnceOnTimeout(() => fetchAppSettings());
        this.downloadConcurrencyInput = this.appSettings.download_concurrency;
      } catch (error) {
        ui.showNotice("error", t("notice_settings_load_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isRefreshingAppSettings = false;
      }
    },
    async saveAppSettings() {
      const ui = useUiStore();
      this.isSavingAppSettings = true;
      try {
        const minValue = this.appSettings?.min_download_concurrency ?? 1;
        const maxValue = this.appSettings?.max_download_concurrency ?? 20;
        const defaultValue = this.appSettings?.default_download_concurrency ?? 2;
        const parsedValue = Number(this.downloadConcurrencyInput);
        const safeValue = Number.isFinite(parsedValue) ? parsedValue : defaultValue;
        const nextValue = Math.min(maxValue, Math.max(minValue, Math.trunc(safeValue)));
        this.appSettings = await runWithRetryOnceOnTimeout(() => updateAppSettings(nextValue));
        this.downloadConcurrencyInput = this.appSettings.download_concurrency;
        ui.showNotice("success", t("notice_settings_save_success"));
      } catch (error) {
        ui.showNotice("error", t("notice_settings_save_failed", { error: extractErrorMessage(error) }));
      } finally {
        this.isSavingAppSettings = false;
      }
    }
  }
});
