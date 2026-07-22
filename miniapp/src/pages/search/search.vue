<template>
  <view class="page">
    <!-- Search Header -->
    <view class="search-header">
      <view class="search-input-wrap" :class="{ focused }">
        <text style="font-size:28rpx;margin-right:8rpx;">🔍</text>
        <input
          class="search-input"
          v-model="query"
          placeholder="搜索标题、摘要或正文..."
          placeholder-style="color:#5c6380"
          confirm-type="search"
          :focus="true"
          @confirm="doSearch"
          @focus="focused = true"
          @blur="focused = false"
        />
        <text
          v-if="query"
          @click="clearSearch"
          style="font-size:28rpx;color:var(--text-muted);padding:8rpx;"
        >✕</text>
      </view>
      <text class="search-cancel" @click="goBack">取消</text>
    </view>

    <!-- Loading -->
    <LoadingSkeleton v-if="loading" :count="3" />

    <!-- Results -->
    <view v-else-if="searched">
      <ArticleCard
        v-for="article in results"
        :key="article.id"
        :article="article"
        @click="goDetail"
      />

      <!-- Load more -->
      <view v-if="loadingMore" class="load-more">
        <text>加载中...</text>
      </view>
      <view v-else-if="hasMore && results.length > 0" class="load-more" @click="loadMore">
        <text style="color:var(--accent)">加载更多</text>
      </view>

      <!-- Empty -->
      <EmptyState
        v-if="results.length === 0"
        text="未找到相关文章"
      />
    </view>

    <!-- Initial state (before first search) -->
    <view v-else class="empty-state">
      <text class="empty-text">输入关键词搜索文章</text>
    </view>
  </view>
</template>

<script>
import { searchArticles } from '@/api/index.js'
import ArticleCard from '@/components/ArticleCard.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  components: { ArticleCard, LoadingSkeleton, EmptyState },
  data() {
    return {
      query: '',
      results: [],
      searched: false,
      loading: false,
      loadingMore: false,
      hasMore: false,
      focused: false,
      limit: 50,
      offset: 0
    }
  },
  onLoad(options) {
    // If a query was passed, pre-fill and search
    if (options && options.q) {
      this.query = options.q
      this.doSearch()
    }
  },
  methods: {
    async doSearch() {
      const q = this.query.trim()
      if (!q) return

      this.offset = 0
      this.loading = true
      this.searched = true

      try {
        const data = await searchArticles(q, this.limit, 0)
        this.results = data
        this.hasMore = data.length >= this.limit
        this.offset = data.length
      } catch (e) {
        console.error('Search failed:', e)
        uni.showToast({ title: '搜索失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    async loadMore() {
      if (this.loadingMore) return
      this.loadingMore = true

      try {
        const data = await searchArticles(this.query.trim(), this.limit, this.offset)
        this.results = [...this.results, ...data]
        this.hasMore = data.length >= this.limit
        this.offset += data.length
      } catch (e) {
        console.error('Load more failed:', e)
      } finally {
        this.loadingMore = false
      }
    },

    clearSearch() {
      this.query = ''
      this.results = []
      this.searched = false
      this.offset = 0
    },

    goDetail(id) {
      uni.navigateTo({ url: `/pages/detail/detail?id=${id}` })
    },

    goBack() {
      uni.navigateBack()
    }
  }
}
</script>
