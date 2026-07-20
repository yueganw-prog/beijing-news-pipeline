<template>
  <div class="view-wrapper">
    <!-- Demo banner -->
    <div v-if="isDemo" class="demo-banner">
      <BaseIcon name="database" :size="12" />
      演示模式 — 显示模拟数据 · 后端 API 不可用时自动启用
    </div>

    <!-- Error -->
    <ErrorState
      v-if="store.error"
      :message="store.error"
      @retry="store.fetchArticles()"
    />

    <!-- Content -->
    <div class="content" v-else>
      <div class="content-inner">
        <ArticleFilter
          v-model="store.source"
          :sources="store.sources"
        />
        <SearchInput
          v-model="store.searchQuery"
          @search="store.fetchArticles()"
        />

        <LoadingSpinner v-if="store.loading" />

        <ArticleTable
          v-else-if="store.items.length"
          :articles="store.items"
          @select="openDetail"
        />

        <EmptyState
          v-else
          :message="store.hasFilters ? '没有匹配的文章' : '暂无文章'"
        />
      </div>
    </div>

    <!-- Detail modal -->
    <ArticleDetail
      :article="store.currentDetail"
      @close="store.clearDetail()"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useArticlesStore } from "@/stores/articles";
import SearchInput from "@/components/common/SearchInput.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import ErrorState from "@/components/common/ErrorState.vue";
import BaseIcon from "@/components/common/BaseIcon.vue";
import ArticleFilter from "./ArticleFilter.vue";
import ArticleTable from "./ArticleTable.vue";
import ArticleDetail from "./ArticleDetail.vue";

const route = useRoute();
const router = useRouter();
const store = useArticlesStore();

const isDemo = computed(
  () => import.meta.env.VITE_MOCK_MODE === "true" || !window.location.hostname.includes("localhost"),
);

function openDetail(id: number) {
  router.push({ name: "article-detail", params: { id } });
}

// Sync route query → store on mount
onMounted(() => {
  if (route.query.category) {
    store.setCategory(route.query.category as string);
  }
  store.fetchArticles();
});

// Re-fetch when route query changes
watch(
  () => route.query,
  (q) => {
    if (q.category) store.setCategory(q.category as string);
    else if (!q.category && store.category) store.setCategory(null);
    store.fetchArticles();
  },
);
</script>
