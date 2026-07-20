<template>
  <Teleport to="body">
    <TransitionGroup name="fade" tag="div" class="toast-container" aria-live="polite">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="`toast-${t.type}`"
        role="alert"
      >
        {{ t.message }}
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from "@/composables/useToast";
const { toasts } = useToast();
</script>
