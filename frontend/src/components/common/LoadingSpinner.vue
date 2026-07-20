<template>
  <div class="loading-overlay" role="status" aria-label="加载中">
    <span class="spinner" :class="{ 'spinner-sm': small }" />
    <slot>加载中...</slot>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ small?: boolean }>(), { small: false });
</script>
