<template>
  <view class="page">
    <!-- Header -->
    <view class="list-header">
      <text class="list-header-title">北京新闻</text>
      <view class="search-icon-btn" @click="goSearch">
        <text style="font-size:32rpx;">🔍</text>
      </view>
    </view>

    <!-- Category Tabs -->
    <CategoryTabs
      :active="activeCategory"
      :counts="categoryCounts"
      @change="onCategoryChange"
    />

    <!-- Loading Skeleton -->
    <LoadingSkeleton v-if="loading && articles.length === 0" :count="4" />

    <!-- Article List -->
    <view v-else>
      <ArticleCard
        v-for="article in articles"
        :key="article.id"
        :article="article"
        @click="goDetail"
      />

      <!-- Load more indicator -->
      <view v-if="loadingMore" class="load-more">
        <text>加载中...</text>
      </view>
      <view v-else-if="!hasMore && articles.length > 0" class="load-more">
        <text>— 已加载全部文章 —</text>
      </view>

      <!-- Empty State -->
      <EmptyState v-if="!loading && articles.length === 0" text="暂无文章" />
    </view>
  </view>
</template>

<script>
import { getArticles, getStatsBySource } from '@/api/index.js'
import CategoryTabs from '@/components/CategoryTabs.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  components: { CategoryTabs, ArticleCard, LoadingSkeleton, EmptyState },
  data() {
    return {
      articles: [],
      activeCategory: '',
      categoryCounts: { tech: 0, finance: 0, local: 0 },
      loading: true,
      loadingMore: false,
      hasMore: true,
      limit: 50,
      offset: 0
    }
  },
  onLoad() {
    this.loadCategoryCounts()
    this.loadArticles(true)
  },
  onShow() {
    // Refresh counts when returning from detail/search page
    this.loadCategoryCounts()
  },
  onPullDownRefresh() {
    this.loadArticles(true).then(() => {
      uni.stopPullDownRefresh()
    })
  },
  onReachBottom() {
    if (!this.hasMore || this.loadingMore) return
    this.loadArticles(false)
  },
  methods: {
    async loadCategoryCounts() {
      try {
        const stats = await getStatsBySource()
        const counts = { tech: 0, finance: 0, local: 0 }
        stats.forEach(s => {
          if (counts[s.category] !== undefined) {
            counts[s.category] += s.cnt
          }
        })
        this.categoryCounts = counts
      } catch (e) {
        console.error('Failed to load counts:', e)
      }
    },

    async loadArticles(reset = false) {
      if (reset) {
        this.offset = 0
        this.loading = this.articles.length === 0
      } else {
        this.loadingMore = true
      }

      try {
        const params = { limit: this.limit, offset: this.offset }
        if (this.activeCategory) params.category = this.activeCategory

        const data = await getArticles(params)

        if (reset) {
          this.articles = data
        } else {
          this.articles = [...this.articles, ...data]
        }

        this.hasMore = data.length >= this.limit
        this.offset += data.length
      } catch (e) {
        console.error('Failed to load articles:', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
        this.loadingMore = false
      }
    },

    onCategoryChange(key) {
      if (this.activeCategory === key) return
      this.activeCategory = key
      this.loadArticles(true)
    },

    goDetail(id) {
      uni.navigateTo({ url: `/pages/detail/detail?id=${id}` })
    },

    goSearch() {
      uni.navigateTo({ url: '/pages/search/search' })
    }
  }
}
</script>
