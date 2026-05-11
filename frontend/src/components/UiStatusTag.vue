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
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
}

.tag[data-status="completed"] {
  border-color: #bbf7d0;
  background: #f0fdf4;
  color: #166534;
}

.tag[data-status="failed"] {
  border-color: #fecaca;
  background: #fef2f2;
  color: #991b1b;
}

.tag[data-status="canceled"] {
  border-color: #e5e7eb;
  background: #f9fafb;
  color: #4b5563;
}
</style>
