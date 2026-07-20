<template>
  <div>
    <AppTopbar
      :title="`文章列表 · ${categoryLabel}（共 ${store.items.length} 篇）`"
      :refreshing="store.loading"
      @refresh="store.fetchArticles()"
      @toggle-mobile="$emit('toggleMobile')"
    />
    <ArticlesView />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useArticlesStore } from "@/stores/articles";
import { CATEGORY_LABELS } from "@/utils/constants";
import AppTopbar from "@/components/layout/AppTopbar.vue";
import ArticlesView from "@/components/articles/ArticlesView.vue";

defineEmits<{ toggleMobile: [] }>();
const store = useArticlesStore();

const categoryLabel = computed(() =>
  store.category ? CATEGORY_LABELS[store.category] || "全部" : "全部",
);
</script>
