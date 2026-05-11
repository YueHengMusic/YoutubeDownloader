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
    <div v-else class="table_wrap">
      <table>
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
            <td class="url" :title="task.status === 'completed' ? (task.output_dir || task.url) : ''">{{ task.url }}</td>
            <td><UiStatusTag :status="task.status" /></td>
            <td class="progress_cell">
              <span class="progress_anchor">
                <span class="progress_value">{{ task.progress.toFixed(1) }}%</span>
                <span v-if="task.status === 'running' && task.eta" class="eta_tip">
                  {{ t("queue_eta_prefix") }} {{ task.eta }}
                </span>
              </span>
            </td>
            <td class="actions_cell">
              <button
                class="btn-secondary"
                @click="handlePrimaryAction(task)"
                :disabled="isPrimaryActionDisabled(task)"
              >
                {{ getPrimaryActionText(task) }}
              </button>
              <button class="btn-secondary danger" @click="removeTask(task.id)" :disabled="task.status === 'running'">
                {{ t("queue_action_delete") }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskRuntimeStore } from "@/stores/taskRuntime";
import { useUiStore } from "@/stores/ui";
import { extractErrorMessage } from "@/stores/apiHelpers";
import type { UiTask } from "@/stores/types";
import UiStatusTag from "@/components/UiStatusTag.vue";
import UiEmptyState from "@/components/UiEmptyState.vue";
import UiLoadingRows from "@/components/UiLoadingRows.vue";
import { t } from "@/i18n/strings";

const store = useTaskRuntimeStore();
const uiStore = useUiStore();

// 页面初始化时读取一次任务快照，并自动接入实时推送。
onMounted(() => {
  store.refreshTasks();
});

async function cancel(taskId: string) {
  await store.cancelTask(taskId);
}

async function retry(taskId: string) {
  await store.retryTask(taskId);
}

async function removeTask(taskId: string) {
  await store.deleteTask(taskId);
}

async function refresh() {
  await store.refreshTasks();
}

function getPrimaryActionText(task: UiTask): string {
  if (task.status === "completed") return t("queue_action_open");
  if (task.status === "failed") return t("queue_action_retry");
  return t("queue_action_cancel");
}

function isPrimaryActionDisabled(task: UiTask): boolean {
  if (task.status === "completed") return !task.output_dir;
  return task.status !== "running" && task.status !== "pending" && task.status !== "failed";
}

async function handlePrimaryAction(task: UiTask) {
  if (task.status === "completed") {
    await openResult(task);
    return;
  }
  if (task.status === "failed") {
    await retry(task.id);
    return;
  }
  await cancel(task.id);
}

async function openResult(task: UiTask) {
  if (!task.output_dir) {
    uiStore.showNotice("error", t("notice_open_task_result_failed", { error: t("common_unknown") }));
    return;
  }
  try {
    const ok = await window.desktopAPI?.revealPath?.(task.output_dir);
    if (ok) return;
    uiStore.showNotice("error", t("notice_open_task_result_failed", { error: t("common_unknown") }));
  } catch (error) {
    uiStore.showNotice("error", t("notice_open_task_result_failed", { error: extractErrorMessage(error) }));
  }
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

.table_wrap {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 640px;
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
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions_cell {
  white-space: nowrap;
}

.progress_cell {
  white-space: nowrap;
}

.progress_anchor {
  position: relative;
  display: inline-block;
  overflow: visible;
}

.eta_tip {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 1px);
  transform: translateX(-50%);
  border: 1px solid var(--hairline);
  border-radius: 8px;
  background: var(--canvas);
  color: var(--ink);
  font-size: 12px;
  line-height: 1.2;
  padding: 4px 8px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.12s ease;
  z-index: 6;
}

.progress_cell:hover .eta_tip {
  opacity: 1;
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

.danger {
  margin-left: 8px;
}

.btn-secondary:disabled {
  background: var(--surface-soft);
  border-color: var(--hairline);
  color: var(--mute);
  cursor: not-allowed;
}

@media (max-width: 560px) {
  table {
    min-width: 560px;
  }
  .btn-secondary {
    height: var(--control_height_compact);
    padding: 6px 14px;
  }
}
</style>
