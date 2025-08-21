<template>
  <div class="message-item assistant">
    <div class="message-avatar">
      <el-avatar :size="32" style="background-color: #409eff">
        AI
      </el-avatar>
    </div>
    <div class="message-content">
      <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 无需任何逻辑，纯展示组件
</script>

<style scoped>
.message-item {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-start;
  animation: fadeIn 0.3s ease-in-out;
}

.message-avatar {
  margin: 0 12px;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  min-width: 0;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #c0c4cc;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>