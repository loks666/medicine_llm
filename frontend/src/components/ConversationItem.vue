<template>
  <div
    class="conversation-item"
    :class="{ active: isActive }"
    @click="handleSelect"
  >
    <div class="conversation-content">
      <div class="conversation-title">{{ conversation.title }}</div>
      <div class="conversation-time">{{ formatTime(conversation.updated_at) }}</div>
    </div>
    <el-button
      type="text"
      size="small"
      :icon="Delete"
      class="delete-btn"
      @click.stop="handleDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { Delete } from '@element-plus/icons-vue'
import type { Conversation } from '@/types'

interface Props {
  conversation: Conversation
  isActive: boolean
}

interface Emits {
  select: [conversationId: string]
  delete: [conversationId: string]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

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

// 处理选择会话
const handleSelect = () => {
  emit('select', props.conversation.id)
}

// 处理删除会话
const handleDelete = () => {
  emit('delete', props.conversation.id)
}
</script>

<style scoped>
.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.conversation-item:hover {
  background-color: #f5f7fa;
}

.conversation-item.active {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
}

.conversation-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: #409eff;
  border-radius: 0 2px 2px 0;
}

.conversation-content {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.conversation-item.active .conversation-title {
  color: #409eff;
}

.conversation-time {
  font-size: 12px;
  color: #909399;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
  padding: 4px;
  margin-left: 8px;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .delete-btn {
    opacity: 1;
  }
}
</style>