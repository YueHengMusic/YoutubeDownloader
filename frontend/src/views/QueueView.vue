<template>
  <section class="section">
    <div class="head">
      <h2>{{ t("queue_title") }}</h2>
      <button class="btn-secondary" @click="refresh" :disabled="store.isRefreshingTasks">
        {{ store.isRefreshingTasks ? t("common_refreshing") : t("common_refresh") }}
      </button>
    </div>

    <UiLoadingRows v-if="store.isRefreshingTasks && store.tasks.length === 0" :rows="4" />
    <UiEmptyState
      v-else-if="store.tasks.length === 0"
      :title="t('queue_empty_title')"
      :description="t('queue_empty_desc')"
      :action-label="t('common_retry')"
      @action="refresh"
    />
    <table v-else>
      <thead>
        <tr>
          <th>{{ t("queue_table_url") }}</th>
          <th>{{ t("queue_table_status") }}</th>
          <th>{{ t("queue_table_progress") }}</th>
          <th>{{ t("queue_table_action") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in store.tasks" :key="task.id">
          <td class="url">{{ task.url }}</td>
          <td><UiStatusTag :status="task.status" /></td>
          <td>{{ task.progress.toFixed(1) }}%</td>
          <td>
            <button class="btn-secondary" @click="cancel(task.id)" :disabled="task.status !== 'running' && task.status !== 'pending'">
              {{ t("queue_action_cancel") }}
            </button>
            <button class="btn-secondary danger" @click="removeTask(task.id)" :disabled="task.status === 'running'">
              {{ t("queue_action_delete") }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "@/stores/tasks";
import UiStatusTag from "@/components/UiStatusTag.vue";
import UiEmptyState from "@/components/UiEmptyState.vue";
import UiLoadingRows from "@/components/UiLoadingRows.vue";
import { t } from "@/i18n/strings";

const store = useTaskStore();

// 页面初始化时读取一次任务快照，并自动接入实时推送。
onMounted(() => {
  store.init();
});

async function cancel(taskId: string) {
  await store.cancelTask(taskId);
}

async function removeTask(taskId: string) {
  await store.deleteTask(taskId);
}

async function refresh() {
  await store.init();
}
</script>

<style scoped>
.section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.33;
  font-weight: 600;
  font-family: "SF Pro Rounded", ui-rounded, ui-sans-serif, system-ui, sans-serif;
}

table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid var(--hairline);
  border-radius: 12px;
  overflow: hidden;
}

th,
td {
  border-bottom: 1px solid var(--hairline);
  padding: 12px;
  text-align: left;
  font-size: 14px;
}

thead th {
  background: var(--surface-soft);
}

.url {
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-secondary {
  border-radius: 9999px;
  height: 36px;
  padding: 8px 20px;
  border: 1px solid var(--hairline-strong);
  background: var(--canvas);
  color: var(--ink);
  cursor: pointer;
}

.danger {
  margin-left: 8px;
}

.btn-secondary:disabled {
  background: var(--surface-soft);
  border-color: var(--hairline);
  color: var(--mute);
  cursor: not-allowed;
}
</style>
