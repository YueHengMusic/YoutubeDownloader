import { defineStore } from "pinia";
import type { NoticeType } from "@/stores/types";

export const useUiStore = defineStore("ui", {
  state: () => ({
    notice: {
      visible: false,
      type: "info" as NoticeType,
      message: "",
      nonce: 0
    }
  }),
  actions: {
    showNotice(type: NoticeType, message: string) {
      this.notice = { visible: true, type, message, nonce: this.notice.nonce + 1 };
    },
    clearNotice() {
      this.notice.visible = false;
      this.notice.message = "";
    }
  }
});
