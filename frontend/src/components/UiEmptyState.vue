<template>
  <section class="empty-state">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <button v-if="actionLabel" class="btn-secondary" type="button" @click="$emit('action')">
      {{ actionLabel }}
    </button>
  </section>
</template>

<script setup lang="ts">
/**
 * 通用空态组件：
 * - 页面无数据时，使用统一结构和样式。
 * - 可选 action 按钮用于“刷新/重试”等动作。
 */
defineProps<{
  title: string;
  description: string;
  actionLabel?: string;
}>();

defineEmits<{
  (event: "action"): void;
}>();
</script>

<style scoped>
.empty-state {
  border: 1px dashed var(--hairline-strong);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  background: var(--surface-soft);
}

h3 {
  margin: 0;
  font-size: 18px;
}

p {
  margin: 8px 0 0;
  color: var(--body);
  font-size: 14px;
}

.btn-secondary {
  margin-top: 12px;
  border-radius: 9999px;
  height: 36px;
  padding: 8px 20px;
  border: 1px solid var(--hairline-strong);
  background: var(--canvas);
  color: var(--ink);
  cursor: pointer;
}
</style>
