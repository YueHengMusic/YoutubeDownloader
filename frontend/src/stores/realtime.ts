import { defineStore } from "pinia";
import { connectTaskWs } from "@/api/client";
import { useTaskRuntimeStore } from "@/stores/taskRuntime";
import type { TaskWsEvent, TerminalLogLine, TerminalStreamType } from "@/stores/types";

export const useRealtimeTaskStore = defineStore("realtimeTask", {
  state: () => ({
    ws: null as WebSocket | null,
    wsReconnectTimer: null as ReturnType<typeof setTimeout> | null,
    terminalLogs: [] as TerminalLogLine[],
    terminalLogIdSeed: 0
  }),
  actions: {
    connectWs() {
      if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) return;
      const ws = connectTaskWs((event: TaskWsEvent) => {
        if (event.type === "task_update") {
          useTaskRuntimeStore().upsertTask(event.data);
          return;
        }
        if (event.type === "terminal_output") {
          const payload = event.data;
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
    clearTerminalLogs() {
      this.terminalLogs = [];
    },
    pushTerminalLog(taskId: string, stream: TerminalStreamType, text: string) {
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
    }
  }
});
