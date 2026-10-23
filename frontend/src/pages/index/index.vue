<template>
  <view class="page">
    <view class="header">
      <text class="org">河北农业大学校医院</text>
      <text class="title">结核病筛查预约</text>
      <text class="subtitle">预约 · 到场核销 · 结果归档</text>
    </view>

    <view class="card">
      <view class="status-row">
        <view class="dot"></view>
        <text class="status-text">项目脚手架已就绪</text>
      </view>
      <text class="desc">
        当前为最小可运行版本，仅用于验证工程链路。预约、核销、结果录入等业务功能尚未开发。
      </text>
    </view>

    <view class="card">
      <text class="card-title">下一步</text>
      <view class="item"><text class="idx">1</text><text class="item-text">确认 PRD 中 Q1–Q18 未定事项</text></view>
      <view class="item"><text class="idx">2</text><text class="item-text">实现邮箱验证码登录</text></view>
      <view class="item"><text class="idx">3</text><text class="item-text">实现号源配置与预约提交</text></view>
    </view>

    <view class="footer">
      <text class="version">v0.1.0 · MVP 脚手架</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {}
  },
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 60rpx 40rpx 40rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  flex-direction: column;
  padding: 20rpx 0 48rpx;
}

.org {
  font-size: 26rpx;
  color: #8a9099;
  letter-spacing: 1rpx;
}

.title {
  margin-top: 18rpx;
  font-size: 52rpx;
  font-weight: 600;
  color: #1f2329;
  letter-spacing: 2rpx;
}

.subtitle {
  margin-top: 14rpx;
  font-size: 26rpx;
  color: #9aa0a8;
}

.card {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 36rpx 32rpx;
  margin-bottom: 28rpx;
  box-shadow: 0 2rpx 12rpx rgba(31, 35, 41, 0.04);
}

.status-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background-color: #07c160;
  margin-right: 14rpx;
}

.status-text {
  font-size: 30rpx;
  font-weight: 500;
  color: #1f2329;
}

.desc {
  display: block;
  margin-top: 20rpx;
  font-size: 26rpx;
  line-height: 44rpx;
  color: #6b7280;
}

.card-title {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #1f2329;
  margin-bottom: 24rpx;
}

.item {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 14rpx 0;
}

.idx {
  width: 40rpx;
  height: 40rpx;
  line-height: 40rpx;
  text-align: center;
  border-radius: 50%;
  background-color: #f0f1f3;
  color: #8a9099;
  font-size: 22rpx;
  margin-right: 18rpx;
}

.item-text {
  font-size: 26rpx;
  color: #4b5563;
}

.footer {
  margin-top: auto;
  padding-top: 40rpx;
  text-align: center;
}

.version {
  font-size: 22rpx;
  color: #b0b5bd;
}
</style>
