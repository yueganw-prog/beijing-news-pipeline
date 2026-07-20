import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { getArticles, getArticle } from "@/api/endpoints";
import type { Article, ArticleDetail } from "@/types";

export const useArticlesStore = defineStore("articles", () => {
  const items = ref<Article[]>([]);
  const currentDetail = ref<ArticleDetail | null>(null);
  const loading = ref(false);
  const detailLoading = ref(false);
  const error = ref<string | null>(null);

  // Filters
  const category = ref<string | null>(null);
  const source = ref<string | null>(null);
  const searchQuery = ref("");

  const sources = computed(() => [...new Set(items.value.map((a) => a.source))].sort());
  const hasFilters = computed(
    () => !!(category.value || source.value || searchQuery.value.trim()),
  );

  async function fetchArticles() {
    loading.value = true;
    error.value = null;
    try {
      const data = await getArticles({
        category: category.value ?? undefined,
        source: source.value ?? undefined,
        search: searchQuery.value.trim() || undefined,
        limit: 500,
      });
      items.value = data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "加载文章失败";
    } finally {
      loading.value = false;
    }
  }

  async function fetchArticleDetail(id: number) {
    detailLoading.value = true;
    try {
      currentDetail.value = await getArticle(id);
    } catch (e) {
      // Fallback: try to find in the already-loaded list
      currentDetail.value = (items.value.find((a) => a.id === id) as ArticleDetail) ?? null;
    } finally {
      detailLoading.value = false;
    }
  }

  function setCategory(cat: string | null) {
    category.value = cat;
    source.value = null;
    searchQuery.value = "";
  }

  function setSource(src: string | null) {
    source.value = src;
  }

  function setSearch(q: string) {
    searchQuery.value = q;
  }

  function clearDetail() {
    currentDetail.value = null;
  }

  return {
    items, currentDetail, loading, detailLoading, error,
    category, source, searchQuery, sources, hasFilters,
    fetchArticles, fetchArticleDetail,
    setCategory, setSource, setSearch, clearDetail,
  };
});
