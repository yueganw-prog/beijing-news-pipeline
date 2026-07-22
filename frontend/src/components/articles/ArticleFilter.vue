<template>
  <div>
    <!-- Filter chips -->
    <div class="filter-bar">
      <button class="filter-chip" :class="{ active: !modelValue }" @click="$emit('update:modelValue', null)">
        全部
      </button>
      <button
        v-for="s in sources"
        :key="s"
        class="filter-chip"
        :class="{ active: modelValue === s }"
        @click="$emit('update:modelValue', modelValue === s ? null : s)"
      >
        {{ s }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{ "update:modelValue": [value: string | null] }>();
defineProps<{ sources: string[]; modelValue: string | null }>();
</script>
