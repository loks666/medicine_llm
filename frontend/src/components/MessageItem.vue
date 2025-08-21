<template>
  <div class="message-item" :class="message.role">
    <div class="message-avatar">
      <el-avatar
        v-if="message.role === 'user'"
        :size="32"
        :icon="UserFilled"
      />
      <el-avatar
        v-else
        :size="32"
        style="background-color: #409eff"
      >
        AI
      </el-avatar>
    </div>
    
    <div class="message-content">
      <div class="message-text" v-html="formattedContent"></div>
      
      <div v-if="message.role === 'assistant'" class="message-actions">
        <el-button
          type="text"
          size="small"
          :icon="message.rating === 1 ? StarFilled : Star"
          :class="{ active: message.rating === 1 }"
          @click="handleRate(1)"
        >
          好评
        </el-button>
        <el-button
          type="text"
          size="small"
          :icon="message.rating === -1 ? StarFilled : Star"
          :class="{ active: message.rating === -1, negative: true }"
          @click="handleRate(-1)"
        >
          差评
        </el-button>
      </div>
      
      <div class="message-time">
        {{ formatTime(message.created_at) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UserFilled, Star, StarFilled } from '@element-plus/icons-vue'
import type { Message } from '@/types'

interface Props {
  message: Message
}

interface Emits {
  rate: [messageId: string, rating: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 格式化消息内容（支持简单的markdown）
const formattedContent = computed(() => {
  return props.message.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
})

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return date.toLocaleDateString()
}

// 处理评价
const handleRate = (rating: number) => {
  emit('rate', props.message.id, rating)
}
</script>

<style scoped>
.message-item {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-start;
  animation: fadeIn 0.3s ease-in-out;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 12px;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  min-width: 0;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  word-wrap: break-word;
  position: relative;
}

.message-item.user .message-text {
  background: #409eff;
  color: white;
}

.message-text :deep(code) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.message-item.user .message-text :deep(code) {
  background-color: rgba(255, 255, 255, 0.2);
}

.message-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-item:hover .message-actions {
  opacity: 1;
}

.message-actions .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

.message-actions .el-button.active {
  color: #f56c6c;
}

.message-actions .el-button.active.negative {
  color: #909399;
}

.message-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-item:hover .message-time {
  opacity: 1;
}

.message-item.user .message-time {
  text-align: right;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .message-text {
    padding: 10px 12px;
  }
  
  .message-actions {
    opacity: 1;
  }
  
  .message-time {
    opacity: 1;
  }
}
</style>