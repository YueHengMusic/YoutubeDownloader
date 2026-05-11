<template>
  <section>
    <h1>历史记录</h1>
    <button @click="store.refreshHistory">刷新</button>
    <ul>
      <li v-for="item in store.history" :key="item.id">
        {{ item.status }} - {{ item.url }}
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "@/stores/tasks";

const store = useTaskStore();
onMounted(() => {
  // 历史记录来自后端 SQLite 持久化，不会因前端刷新而丢失。
  store.refreshHistory();
});
</script>
