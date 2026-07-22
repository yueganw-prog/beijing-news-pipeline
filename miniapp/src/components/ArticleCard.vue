<template>
  <view class="article-card" @click="$emit('click', article.id)">
    <view class="card-title">{{ article.title || '(无标题)' }}</view>
    <view class="card-meta">
      <span class="badge" :class="'badge-' + article.category">
        {{ catLabel(article.category) }}
      </span>
      <text class="card-source">{{ article.source }}</text>
      <text class="card-date">{{ formatRelative(article.published_at) }}</text>
    </view>
    <view class="card-summary" v-if="article.summary">
      {{ article.summary }}
    </view>
  </view>
</template>

<script>
import { CAT_LABELS, formatRelative } from '@/utils/format.js'

export default {
  name: 'ArticleCard',
  props: {
    article: { type: Object, required: true }
  },
  emits: ['click'],
  methods: {
    formatRelative,
    catLabel(cat) {
      return CAT_LABELS[cat] || cat
    }
  }
}
</script>
