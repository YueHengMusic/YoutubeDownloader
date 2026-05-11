<template>
  <div class="layout">
    <aside class="sidebar">
      <h2>yt-dlp GUI</h2>
      <!-- 左侧导航：把最常用操作固定在一个位置，降低新手学习成本 -->
      <nav>
        <RouterLink to="/download">下载</RouterLink>
        <RouterLink to="/queue">队列</RouterLink>
        <RouterLink to="/history">历史</RouterLink>
        <RouterLink to="/settings">设置</RouterLink>
      </nav>
    </aside>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.layout { display: grid; grid-template-columns: 220px 1fr; min-height: 100vh; font-family: Arial, sans-serif; }
.sidebar { padding: 16px; background: #171717; color: #fff; }
.sidebar nav { display: flex; flex-direction: column; gap: 8px; }
.sidebar a { color: #d2d2d2; text-decoration: none; }
.content { padding: 20px; background: #f5f5f5; }
</style>
