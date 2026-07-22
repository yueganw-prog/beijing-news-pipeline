<template>
  <div class="topbar">
    <div style="display:flex;align-items:center;gap:12px">
      <button class="mobile-toggle" @click="$emit('toggleMobile')" aria-label="菜单">
        <BaseIcon name="menu" />
      </button>
      <h2>{{ title }}</h2>
    </div>
    <div class="topbar-actions">
      <slot name="actions" />
      <button v-if="showRefresh" class="btn-icon" :class="{ refreshing }" @click="$emit('refresh')" aria-label="刷新">
        <BaseIcon name="refresh" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseIcon from "@/components/common/BaseIcon.vue";

defineEmits<{ toggleMobile: []; refresh: [] }>();
withDefaults(
  defineProps<{
    title?: string;
    refreshing?: boolean;
    showRefresh?: boolean;
  }>(),
  { title: "", refreshing: false, showRefresh: true },
);
</script>
