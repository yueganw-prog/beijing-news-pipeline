<template>
  <div class="page">
    <AppTopbar
      title="文章详情"
      :show-refresh="false"
      @toggle-mobile="$emit('toggleMobile')"
    >
      <template #actions>
        <button class="btn-icon" @click="router.back()" aria-label="返回">
          <BaseIcon name="chevronLeft" />
        </button>
      </template>
    </AppTopbar>

    <div class="content">
      <div class="content-inner">
        <LoadingSpinner v-if="store.detailLoading" />
        <ErrorState
          v-else-if="!article"
          message="文章不存在或已删除"
          retry-label="返回列表"
          @retry="router.push({ name: 'articles' })"
        />
        <div v-else class="panel" style="animation:none;box-shadow:none">
          <div class="panel-header">
            <h2>{{ article.title }}</h2>
          </div>
          <div class="panel-body">
            <div class="meta">
              <StatusBadge :category="article.category" />
              <span><BaseIcon name="globe" /> {{ article.source }}</span>
              <span v-if="article.author"><BaseIcon name="user" /> {{ article.author }}</span>
              <span><BaseIcon name="calendar" /> {{ formatDate(article.published_at) }}</span>
            </div>
            <div v-if="article.summary" class="summary">{{ article.summary }}</div>
            <div class="article-content">
              {{ article.content_clean || "(无内容)" }}
            </div>
            <div class="detail-actions">
              <button class="action-btn" @click="searchOriginal">
                <BaseIcon name="link" /> 搜索原文
              </button>
              <button class="action-btn" @click="copyContent">
                <BaseIcon :name="copied ? 'check' : 'copy'" />
                {{ copied ? "已复制" : "复制内容" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useArticlesStore } from "@/stores/articles";
import { formatDate } from "@/utils/formatters";
import AppTopbar from "@/components/layout/AppTopbar.vue";
import BaseIcon from "@/components/common/BaseIcon.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import ErrorState from "@/components/common/ErrorState.vue";

defineEmits<{ toggleMobile: [] }>();

const props = defineProps<{ id: number }>();
const router = useRouter();
const store = useArticlesStore();
const copied = ref(false);

const article = computed(() => store.currentDetail);

onMounted(() => {
  store.fetchArticleDetail(props.id);
});

watch(
  () => props.id,
  (newId) => {
    store.fetchArticleDetail(newId);
  },
);

function searchOriginal() {
  if (article.value) {
    window.open(
      "https://www.google.com/search?q=" +
      encodeURIComponent(article.value.title),
      "_blank",
    );
  }
}

async function copyContent() {
  if (!article.value) return;
  const text = article.value.content_clean || "";
  try {
    await navigator.clipboard.writeText(text);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch {
    // clipboard unavailable
  }
}
</script>
