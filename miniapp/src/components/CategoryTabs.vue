<template>
  <view class="cat-tabs">
    <view
      v-for="tab in tabs"
      :key="tab.key"
      class="cat-tab"
      :class="{ active: active === tab.key }"
      @click="$emit('change', tab.key)"
    >
      {{ tab.label }}
      <text class="count" v-if="tab.count > 0">{{ tab.count }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CategoryTabs',
  props: {
    active: { type: String, default: '' },
    counts: { type: Object, default: () => ({}) }
  },
  emits: ['change'],
  computed: {
    tabs() {
      return [
        { key: '',   label: '全部', count: this.totalCount },
        { key: 'tech',   label: '科技', count: this.counts.tech || 0 },
        { key: 'finance', label: '财经', count: this.counts.finance || 0 },
        { key: 'local',   label: '本地', count: this.counts.local || 0 }
      ]
    },
    totalCount() {
      return (this.counts.tech || 0) + (this.counts.finance || 0) + (this.counts.local || 0)
    }
  }
}
</script>
