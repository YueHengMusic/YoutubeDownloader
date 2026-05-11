<template>
  <div class="loading-list">
    <div v-for="i in rows" :key="i" class="row" />
  </div>
</template>

<script setup lang="ts">
/**
 * 通用加载骨架组件：
 * - 在异步请求进行中展示，占位效果更自然。
 */
withDefaults(
  defineProps<{
    rows?: number;
  }>(),
  {
    rows: 4
  }
);
</script>

<style scoped>
.loading-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row {
  height: 48px;
  border-radius: 12px;
  border: 1px solid var(--hairline);
  background: linear-gradient(90deg, #fafafa 25%, #f3f4f6 37%, #fafafa 63%);
  background-size: 400% 100%;
  animation: shine 1.2s ease-in-out infinite;
}

@keyframes shine {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</style>
