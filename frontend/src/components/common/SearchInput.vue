<template>
  <div class="search-bar">
    <input
      :value="modelValue"
      type="text"
      :placeholder="placeholder"
      @input="onInput"
      @keydown.enter="$emit('search')"
      aria-label="搜索"
    />
    <button class="btn-icon" @click="$emit('search')" aria-label="搜索">
      <BaseIcon name="search" />
    </button>
  </div>
</template>

<script setup lang="ts">
import BaseIcon from "./BaseIcon.vue";

const emit = defineEmits<{
  search: [];
  "update:modelValue": [value: string];
}>();

withDefaults(
  defineProps<{
    modelValue?: string;
    placeholder?: string;
  }>(),
  { modelValue: "", placeholder: "搜索标题、摘要或正文..." },
);

function onInput(e: Event) {
  const target = e.target as HTMLInputElement;
  emit("update:modelValue", target.value);
}
</script>
