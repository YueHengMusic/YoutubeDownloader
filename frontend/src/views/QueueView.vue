<template>
  <section>
    <h1>下载队列</h1>
    <button @click="refresh">刷新</button>
    <table>
      <thead>
        <tr>
          <th>链接</th>
          <th>状态</th>
          <th>进度</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in store.tasks" :key="task.id">
          <td>{{ task.url }}</td>
          <td>{{ task.status }}</td>
          <td>{{ task.progress.toFixed(1) }}%</td>
          <td>
            <button @click="cancel(task.id)" :disabled="task.status !== 'running' && task.status !== 'pending'">取消</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "@/stores/tasks";

const store = useTaskStore();

// 页面初始化时读取一次任务快照，并自动接入实时推送。
onMounted(() => {
  store.init();
});

async function cancel(taskId: string) {
  await store.cancelTask(taskId);
}

async function refresh() {
  await store.init();
}
</script>

<style scoped>
table { width: 100%; background: white; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 8px; }
</style>
