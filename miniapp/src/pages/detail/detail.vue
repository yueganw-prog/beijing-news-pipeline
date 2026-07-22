<template>
  <scroll-view scroll-y class="page" v-if="article">
    <view class="detail-container">
      <!-- Title -->
      <text class="detail-title">{{ article.title }}</text>

      <!-- Meta bar -->
      <view class="detail-meta">
        <span class="badge" :class="'badge-' + article.category">
          {{ catLabel(article.category) }}
        </span>
        <view class="detail-meta-item">
          <text>📰</text>
          <text>{{ article.source }}</text>
        </view>
        <view class="detail-meta-item" v-if="article.author && article.author !== '自动采集'">
          <text>✍️</text>
          <text>{{ article.author }}</text>
        </view>
        <view class="detail-meta-item">
          <text>🕐</text>
          <text>{{ formatDate(article.published_at) }}</text>
        </view>
      </view>

      <!-- Summary -->
      <view class="detail-summary" v-if="article.summary">
        <text>{{ article.summary }}</text>
      </view>

      <!-- Content -->
      <text class="detail-content">{{ article.content_clean || article.content_raw || '(暂无内容)' }}</text>

      <!-- Action buttons -->
      <view class="detail-actions">
        <view class="action-btn" @click="copyContent">
          <text>📋</text>
          <text>{{ copied ? '已复制' : '复制全文' }}</text>
        </view>
        <view class="action-btn" @click="openOriginal">
          <text>🔗</text>
          <text>复制原文链接</text>
        </view>
      </view>
    </view>
  </scroll-view>

  <!-- Loading State -->
  <view v-else-if="loading" class="empty-state">
    <text class="empty-text">加载中...</text>
  </view>

  <!-- Error State -->
  <view v-else class="empty-state">
    <view class="empty-icon" />
    <text class="empty-text">文章加载失败</text>
    <view class="action-btn" style="margin-top:24rpx;width:200rpx;" @click="fetchArticle">
      <text>重试</text>
    </view>
  </view>
</template>

<script>
import { getArticle } from '@/api/index.js'
import { CAT_LABELS, formatDate } from '@/utils/format.js'

export default {
  data() {
    return {
      article: null,
      loading: true,
      copied: false
    }
  },
  onLoad(options) {
    if (options.id) {
      this.fetchArticle(parseInt(options.id))
    }
  },
  methods: {
    async fetchArticle(id) {
      this.loading = true
      try {
        const idToFetch = id || parseInt(this.$route?.query?.id)
        this.article = await getArticle(idToFetch)
      } catch (e) {
        console.error('Failed to load article:', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    catLabel(cat) {
      return CAT_LABELS[cat] || cat
    },

    formatDate,

    async copyContent() {
      if (!this.article) return
      const text = this.article.content_clean || this.article.content_raw || ''
      try {
        await uni.setClipboardData({ data: text })
        this.copied = true
        uni.showToast({ title: '已复制', icon: 'success' })
        setTimeout(() => { this.copied = false }, 2000)
      } catch (e) {
        uni.showToast({ title: '复制失败', icon: 'none' })
      }
    },

    openOriginal() {
      if (!this.article || !this.article.url) return
      uni.setClipboardData({ data: this.article.url })
      uni.showModal({
        title: '链接已复制',
        content: '请在浏览器中粘贴打开原文',
        showCancel: false,
        confirmText: '知道了'
      })
    }
  }
}
</script>
