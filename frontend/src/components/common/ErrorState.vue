<template>
  <div class="error-state" role="alert">
    <p>{{ message }}</p>
    <button v-if="retryLabel" @click="$emit('retry')">{{ retryLabel }}</button>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineEmits<{ retry: [] }>();
withDefaults(
  defineProps<{
    message?: string;
    retryLabel?: string;
  }>(),
  { message: "加载失败，请稍后重试", retryLabel: "重新加载" },
);
</script>
