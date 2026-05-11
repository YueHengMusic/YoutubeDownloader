<template>
  <section class="section">
    <div class="head">
      <h2>{{ t("logs_title") }}</h2>
      <button type="button" class="btn-secondary" @click="realtimeStore.clearTerminalLogs()">
        {{ t("terminal_clear") }}
      </button>
    </div>
    <p class="desc">{{ t("logs_desc") }}</p>

    <article class="terminal_card">
      <div ref="terminal_body_ref" class="terminal_body">
        <p v-if="realtimeStore.terminalLogs.length === 0" class="terminal_empty">{{ t("terminal_empty") }}</p>
        <p v-for="line in realtimeStore.terminalLogs" :key="line.id" class="terminal_line">
          <span class="terminal_meta">[{{ format_time(line.created_at) }}] [{{ line.task_id.slice(0, 8) }}] [{{ terminal_stream_label(line.stream) }}]</span>
          <span class="terminal_text">{{ line.text }}</span>
        </p>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import { useRealtimeTaskStore } from "@/stores/realtime";
import { t } from "@/i18n/strings";
import type { TerminalStreamType } from "@/stores/types";

const realtimeStore = useRealtimeTaskStore();
const terminal_body_ref = ref<HTMLElement | null>(null);

watch(
  () => realtimeStore.terminalLogs.length,
  async () => {
    // 新日志到达时自动滚到底部，便于观察最新输出。
    await nextTick();
    if (terminal_body_ref.value) {
      terminal_body_ref.value.scrollTop = terminal_body_ref.value.scrollHeight;
    }
  }
);

function terminal_stream_label(stream: TerminalStreamType): string {
  if (stream === "command") return t("terminal_stream_command");
  if (stream === "status") return t("terminal_stream_status");
  return t("terminal_stream_stdout");
}

function format_time(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString();
}
</script>

<style scoped>
.section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}

h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.33;
  font-weight: 600;
  font-family: "SF Pro Rounded", ui-rounded, ui-sans-serif, system-ui, sans-serif;
}

.desc {
  margin: 0;
  color: var(--body);
  font-size: 14px;
}

.terminal_card {
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: var(--card_padding_compact);
  background: var(--canvas);
}

.terminal_body {
  max-height: calc(100vh - 280px);
  min-height: 240px;
  overflow: auto;
  padding: 0;
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  font-size: 14px;
  line-height: 1.45;
}

.terminal_empty {
  margin: 0;
  color: var(--mute);
}

.terminal_line {
  margin: 0 0 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 2px 8px;
}

.terminal_meta {
  color: var(--body);
  flex: 0 0 auto;
}

.terminal_text {
  color: var(--ink);
  flex: 1 1 260px;
  word-break: break-word;
}

.btn-secondary {
  border-radius: 9999px;
  height: var(--control_height);
  padding: 8px 20px;
  border: 1px solid var(--hairline-strong);
  background: var(--canvas);
  color: var(--ink);
  cursor: pointer;
}

@media (max-width: 560px) {
  .btn-secondary {
    height: var(--control_height_compact);
    padding: 6px 14px;
  }
  .terminal_body {
    max-height: calc(100vh - 300px);
    min-height: 200px;
  }
}
</style>
