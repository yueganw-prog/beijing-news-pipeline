<template>
  <table class="article-table">
    <thead>
      <tr>
        <th>标题</th>
        <th>来源</th>
        <th class="cell-category">分类</th>
        <th>日期</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(article, idx) in articles"
        :key="article.id"
        :style="{ animation: 'slideUp .3s ease ' + idx * 0.02 + 's both' }"
        tabindex="0"
        @click="$emit('select', article.id)"
        @keydown.enter="$emit('select', article.id)"
      >
        <td class="cell-title" :title="article.title">{{ article.title || "(无标题)" }}</td>
        <td class="cell-source">{{ article.source }}</td>
        <td class="cell-category"><StatusBadge :category="article.category" /></td>
        <td class="cell-date">{{ formatDate(article.published_at) }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import type { Article } from "@/types";
import { formatDate } from "@/utils/formatters";
import StatusBadge from "@/components/common/StatusBadge.vue";

defineEmits<{ select: [id: number] }>();
defineProps<{ articles: Article[] }>();
</script>
