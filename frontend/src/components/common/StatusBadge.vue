<template>
  <span class="badge" :class="`badge-${category}`" :aria-label="label">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { CATEGORY_LABELS } from "@/utils/constants";

const props = defineProps<{ category: string }>();
const label = computed(() => CATEGORY_LABELS[props.category] || props.category);
</script>
