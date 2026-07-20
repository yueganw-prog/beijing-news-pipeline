<template>
  <div class="source-grid">
    <div
      v-for="s in stats"
      :key="s.source"
      class="source-card"
      :class="s.category"
    >
      <div class="src-name">{{ s.source }}</div>
      <div class="src-count">{{ s.cnt.toLocaleString() }}</div>
      <div class="src-last">
        <BaseIcon name="clock" :size="12" />
        最近: {{ formatDateTime(s.last_fetched) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { StatsBySource } from "@/types";
import { formatDateTime } from "@/utils/formatters";
import BaseIcon from "@/components/common/BaseIcon.vue";

defineProps<{ stats: StatsBySource[] }>();
</script>
