<template>
  <div class="empty-state" role="status">
    <p>{{ message }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ message?: string }>(), { message: "暂无数据" });
</script>
