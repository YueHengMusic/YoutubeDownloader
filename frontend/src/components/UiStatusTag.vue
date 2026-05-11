<template>
  <span class="tag" :data-status="status">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { taskStatusText } from "@/i18n/strings";

/**
 * 统一任务状态标签组件：
 * - 统一“状态文案 + 状态颜色”，页面无需重复写判断逻辑。
 */
const props = defineProps<{
  status: "pending" | "running" | "completed" | "failed" | "canceled";
}>();

const label = computed(() => taskStatusText(props.status));
</script>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  min-width: 74px;
  padding: 0 12px;
  border-radius: 9999px;
  border: 1px solid var(--hairline);
  background: var(--surface-soft);
  font-size: 12px;
}

.tag[data-status="running"] {
  border-color: var(--status-running-border);
  background: var(--status-running-bg);
  color: var(--status-running-text);
}

.tag[data-status="completed"] {
  border-color: var(--status-completed-border);
  background: var(--status-completed-bg);
  color: var(--status-completed-text);
}

.tag[data-status="failed"] {
  border-color: var(--status-failed-border);
  background: var(--status-failed-bg);
  color: var(--status-failed-text);
}

.tag[data-status="canceled"] {
  border-color: var(--status-canceled-border);
  background: var(--status-canceled-bg);
  color: var(--status-canceled-text);
}
</style>
