<template>
  <section class="section">
    <div class="head">
      <h2>{{ t("history_title") }}</h2>
      <div class="actions">
        <button class="btn-secondary" @click="store.refreshHistory" :disabled="store.isRefreshingHistory">
          {{ store.isRefreshingHistory ? t("common_refreshing") : t("common_refresh") }}
        </button>
        <button class="btn-secondary" @click="store.clearHistory" :disabled="store.history.length === 0">
          {{ t("history_action_clear_all") }}
        </button>
      </div>
    </div>

    <UiLoadingRows v-if="store.isRefreshingHistory && store.history.length === 0" :rows="4" />
    <UiEmptyState
      v-else-if="store.history.length === 0"
      :title="t('history_empty_title')"
      :description="t('history_empty_desc')"
      :action-label="t('common_retry')"
      @action="store.refreshHistory"
    />
    <div v-else class="list">
      <article class="item" v-for="item in store.history" :key="item.id">
        <div class="row">
          <UiStatusTag :status="item.status" />
          <div class="meta">
            <span class="time">{{ item.updated_at }}</span>
            <button class="btn-secondary btn-sm" @click="store.deleteHistoryItem(item.id)">
              {{ t("history_action_delete") }}
            </button>
          </div>
        </div>
        <p class="url">{{ item.url }}</p>
      </article>
    </div>
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
onMounted(() => {
  // 历史记录来自后端 SQLite 持久化，不会因前端刷新而丢失。
  store.refreshHistory();
});
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

.actions {
  display: flex;
  align-items: center;
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

.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item {
  border: 1px solid var(--hairline);
  border-radius: 12px;
  padding: var(--card_padding_compact);
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.meta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.time {
  color: var(--body);
  font-size: 12px;
}

.url {
  margin: 8px 0 0;
  font-size: 14px;
  word-break: break-all;
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

.btn-secondary:disabled {
  background: var(--surface-soft);
  border-color: var(--hairline);
  color: var(--mute);
  cursor: not-allowed;
}

.btn-sm {
  height: var(--control_height_compact);
  padding: 0 12px;
}

@media (max-width: 560px) {
  .actions {
    width: 100%;
  }
  .btn-secondary {
    height: var(--control_height_compact);
    padding: 6px 14px;
  }
  .actions .btn-secondary {
    flex: 1 1 160px;
  }
  .meta {
    width: 100%;
    justify-content: space-between;
  }
  .btn-sm {
    margin-left: auto;
  }
}
</style>
