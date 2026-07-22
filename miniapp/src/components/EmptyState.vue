<template>
  <view class="empty-state">
    <view class="empty-icon" />
    <text class="empty-text">{{ text }}</text>
  </view>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    text: { type: String, default: '暂无数据' }
  }
}
</script>
