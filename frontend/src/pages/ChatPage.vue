<template>
  <div class="chat-container">
    <!-- 侧边栏 - 会话列表 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>医疗AI助手</h2>
        <el-button
          type="primary"
          size="small"
          :icon="Plus"
          @click="createNewConversation"
        >
          新建对话
        </el-button>
      </div>
      
      <div class="conversation-list">
          <ConversationItem
            v-for="conversation in chatStore.conversations"
            :key="conversation.id"
            :conversation="conversation"
            :is-active="conversation.id === chatStore.currentConversation?.id"
            @select="selectConversation"
            @delete="deleteConversation"
          />
        </div>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <el-avatar :size="32" :icon="UserFilled" />
          <span>{{ authStore.user?.username }}</span>
        </div>
        <el-button
          type="text"
          size="small"
          @click="handleLogout"
        >
          退出登录
        </el-button>
      </div>
    </div>
    
    <!-- 主聊天区域 -->
    <div class="chat-main">
      <div v-if="!chatStore.currentConversation" class="welcome-screen">
        <div class="welcome-content">
          <h1>欢迎使用医疗AI助手</h1>
          <p>请选择一个对话或创建新的对话开始咨询</p>
          <el-button
            type="primary"
            size="large"
            :icon="Plus"
            @click="createNewConversation"
          >
            开始新对话
          </el-button>
        </div>
      </div>
      
      <div v-else class="chat-content">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <h3>{{ chatStore.currentConversation.title }}</h3>
          <div class="chat-controls">
            <el-select
              v-model="chatStore.currentModel"
              placeholder="选择模型"
              size="small"
              style="width: 200px"
            >
              <el-option
                v-for="model in chatStore.availableModels"
                :key="model.id"
                :label="model.name"
                :value="model.id"
              />
            </el-select>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <div ref="messageListRef" class="message-list">
          <MessageItem
            v-for="message in chatStore.messages"
            :key="message.id"
            :message="message"
            @rate="rateMessage"
          />
          
          <!-- 流式输入指示器 -->
          <TypingIndicator v-if="chatStore.isStreaming" />
        </div>
        
        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-container">
            <el-input
              v-model="messageInput"
              type="textarea"
              :rows="3"
              placeholder="请输入您的医疗咨询问题..."
              :disabled="chatStore.isStreaming"
              @keydown.ctrl.enter="sendMessage"
            />
            <div class="input-actions">
              <span class="input-tip">Ctrl + Enter 发送</span>
              <el-button
                type="primary"
                :loading="chatStore.isStreaming"
                :disabled="!messageInput.trim()"
                @click="sendMessage"
              >
                {{ chatStore.isStreaming ? '发送中...' : '发送' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Delete,
  UserFilled,
  Star,
  StarFilled
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import MessageItem from '@/components/MessageItem.vue'
import ConversationItem from '@/components/ConversationItem.vue'
import TypingIndicator from '@/components/TypingIndicator.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const messageInput = ref('')
const messageListRef = ref<HTMLElement>()

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}



// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 创建新对话
const createNewConversation = async () => {
  try {
    await chatStore.createConversation()
    ElMessage.success('创建新对话成功')
  } catch (error) {
    ElMessage.error('创建对话失败')
  }
}

// 选择对话
const selectConversation = async (conversationId: string) => {
  try {
    await chatStore.selectConversation(conversationId)
    scrollToBottom()
  } catch (error) {
    ElMessage.error('加载对话失败')
  }
}

// 删除对话
const deleteConversation = async (conversationId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个对话吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await chatStore.deleteConversation(conversationId)
    ElMessage.success('删除对话成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除对话失败')
    }
  }
}

// 发送消息
const sendMessage = async () => {
  if (!messageInput.value.trim() || chatStore.isStreaming) return
  
  const message = messageInput.value.trim()
  messageInput.value = ''
  
  try {
    await chatStore.sendMessage(message)
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送消息失败')
  }
}

// 评价消息
const rateMessage = async (messageId: string, rating: number) => {
  try {
    await chatStore.rateMessage(messageId, rating)
    ElMessage.success('评价成功')
  } catch (error) {
    console.error('评价失败:', error)
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '确认退出',
      {
        confirmButtonText: '退出',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退出登录失败')
    }
  }
}

// 监听消息变化，自动滚动到底部
watch(
  () => chatStore.messages.length,
  () => {
    scrollToBottom()
  }
)

// 页面加载时初始化数据
onMounted(async () => {
  try {
    await Promise.all([
      chatStore.fetchModels(),
      chatStore.fetchConversations()
    ])
  } catch (error) {
    ElMessage.error('初始化数据失败')
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

/* 侧边栏样式 */
.sidebar {
  width: 300px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h2 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 18px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.conversation-item:hover {
  background-color: #f5f7fa;
}

.conversation-item.active {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
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
}

.conversation-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #2c3e50;
}

/* 主聊天区域样式 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-content {
  text-align: center;
  color: #7f8c8d;
}

.welcome-content h1 {
  margin: 0 0 16px 0;
  color: #2c3e50;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-header h3 {
  margin: 0;
  color: #2c3e50;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

.message-item {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-start;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 12px;
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
}

.message-item.user .message-text {
  background: #409eff;
  color: white;
}

.message-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.message-actions .el-button.active {
  color: #f56c6c;
}

.message-actions .el-button.active.negative {
  color: #909399;
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
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-tip {
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 250px;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>