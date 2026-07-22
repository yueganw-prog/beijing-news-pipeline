<template>
  <span class="base-icon" :style="style" v-html="svg" aria-hidden="true" />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { icons } from "@/utils/icons";

const props = withDefaults(
  defineProps<{
    name: string;
    size?: number;
  }>(),
  { size: 16 },
);

const svg = computed(() => icons[props.name] || "");
const style = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  flexShrink: 0,
}));
</script>
