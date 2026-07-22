<template>
  <view>
    <view v-for="i in count" :key="i" class="skeleton skeleton-card">
      <view class="skeleton skeleton-line" style="width: 85%;" />
      <view class="skeleton skeleton-line" style="width: 40%;" />
      <view class="skeleton skeleton-line" />
    </view>
  </view>
</template>

<script>
export default {
  name: 'LoadingSkeleton',
  props: {
    count: { type: Number, default: 4 }
  }
}
</script>
