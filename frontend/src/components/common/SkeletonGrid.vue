<template>
  <div class="skeleton-grid" :style="gridStyle" role="status" aria-label="加载中">
    <div v-for="i in count" :key="i" class="skeleton" :style="{ height: itemHeight }" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    count?: number;
    columns?: number;
    itemHeight?: string;
  }>(),
  { count: 4, columns: 4, itemHeight: "100px" },
);

const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(auto-fit, minmax(${Math.max(160, 800 / props.columns)}px, 1fr))`,
}));
</script>
