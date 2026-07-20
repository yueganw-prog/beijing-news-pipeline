<template>
  <div class="theme-toggle" role="radiogroup" aria-label="主题切换">
    <button
      v-for="opt in options"
      :key="opt.key"
      :class="{ active: theme.mode === opt.key }"
      :aria-label="opt.label"
      :aria-checked="theme.mode === opt.key"
      role="radio"
      @click="theme.setTheme(opt.key)"
    >
      <BaseIcon :name="opt.icon" :size="14" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore, type ThemeMode } from "@/stores/theme";
import BaseIcon from "./BaseIcon.vue";

const theme = useThemeStore();

const options: { key: ThemeMode; label: string; icon: string }[] = [
  { key: "dark", label: "深色模式", icon: "moon" },
  { key: "light", label: "浅色模式", icon: "sun" },
  { key: "system", label: "跟随系统", icon: "monitor" },
];
</script>
