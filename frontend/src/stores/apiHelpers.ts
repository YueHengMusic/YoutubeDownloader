import { t } from "@/i18n/strings";

export function isTimeoutError(error: unknown): boolean {
  if (typeof error !== "object" || error === null) return false;
  const maybe = error as { code?: string; message?: string };
  if (maybe.code === "ECONNABORTED") return true;
  return typeof maybe.message === "string" && maybe.message.toLowerCase().includes("timeout");
}

export async function runWithRetryOnceOnTimeout<T>(requestFn: () => Promise<T>): Promise<T> {
  try {
    return await requestFn();
  } catch (error) {
    if (!isTimeoutError(error)) throw error;
  }
  return await requestFn();
}

export function extractErrorMessage(error: unknown): string {
  if (typeof error === "object" && error !== null) {
    const maybe = error as { response?: { data?: { detail?: string } }; message?: string };
    if (maybe.response?.data?.detail) return maybe.response.data.detail;
    if (maybe.message) return maybe.message;
  }
  return t("notice_unknown_error");
}
