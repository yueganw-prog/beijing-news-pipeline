<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="article" class="overlay" @click.self="close" @keydown.escape="close">
        <div class="panel" role="dialog" aria-modal="true" aria-label="文章详情">
          <div class="panel-header">
            <h2>{{ article.title }}</h2>
            <button class="close-btn" @click="close" aria-label="关闭">
              <BaseIcon name="close" />
            </button>
          </div>
          <div class="panel-body">
            <!-- Meta -->
            <div class="meta">
              <StatusBadge :category="article.category" />
              <span><BaseIcon name="globe" /> {{ article.source }}</span>
              <span v-if="article.author"><BaseIcon name="user" /> {{ article.author }}</span>
              <span><BaseIcon name="calendar" /> {{ formatDate(article.published_at) }}</span>
            </div>

            <!-- Summary -->
            <div v-if="article.summary" class="summary">{{ article.summary }}</div>

            <!-- Content -->
            <div class="article-content">
              {{ article.content_clean || article.content_raw || "(无内容)" }}
            </div>

            <!-- Actions -->
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
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { ArticleDetail as ArticleDetailType } from "@/types";
import { formatDate } from "@/utils/formatters";
import BaseIcon from "@/components/common/BaseIcon.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{ article: ArticleDetailType | null }>();
const emit = defineEmits<{ close: [] }>();

const copied = ref(false);

function close() {
  emit("close");
}

function searchOriginal() {
  if (props.article) {
    window.open(
      "https://www.google.com/search?q=" +
      encodeURIComponent(props.article.title),
      "_blank",
    );
  }
}

async function copyContent() {
  if (!props.article) return;
  const text = props.article.content_clean || props.article.content_raw || "";
  try {
    await navigator.clipboard.writeText(text);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch {
    // clipboard API may be unavailable in insecure contexts
  }
}
</script>
