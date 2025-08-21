import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { get, post, del, createSSEConnection } from '@/utils/api'

interface Model {
  id: string
  name: string
  description?: string
}

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  rating?: number
  created_at: string
}

interface ChatRequest {
  message: string
  model?: string
  system_prompt?: string
}

interface SSEChunk {
  type: 'chunk'
  content: string
}

interface SSEDone {
  type: 'done'
  message_id: string
}

type SSEEvent = SSEChunk | SSEDone

export const useChatStore = defineStore('chat', () => {
  // 状态
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const messages = ref<Message[]>([])
  const currentModel = ref('gpt-3.5-turbo')
  const systemPrompt = ref('你是一个专业的医疗AI助手，请为用户提供准确、有用的医疗咨询建议。')
  const isStreaming = ref(false)
  const availableModels = ref<Model[]>([])
  const loading = ref(false)

  // 计算属性
  const hasConversations = computed(() => conversations.value.length > 0)
  const currentMessages = computed(() => 
    messages.value.filter(msg => msg.conversation_id === currentConversation.value?.id)
  )

  // 获取可用模型列表
  const fetchModels = async () => {
    try {
      const response = await get<Model[]>('/chat/models')
      availableModels.value = response.data
    } catch (error) {
      console.error('获取模型列表失败:', error)
    }
  }

  // 获取会话列表
  const fetchConversations = async () => {
    loading.value = true
    try {
      const response = await get<Conversation[]>('/conversations')
      conversations.value = response.data
    } catch (error) {
      console.error('获取会话列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 创建新会话
  const createConversation = async (title?: string) => {
    try {
      const response = await post<Conversation>('/conversations', {
        title: title || '新对话'
      })
      
      const newConversation = response.data
      conversations.value.unshift(newConversation)
      currentConversation.value = newConversation
      messages.value = []
    } catch (error) {
      console.error('创建会话失败:', error)
      throw error
    }
  }

  // 选择会话并加载消息
  const selectConversation = async (conversationId: string) => {
    loading.value = true
    try {
      // 设置当前会话
      const conversation = conversations.value.find(c => c.id === conversationId)
      if (!conversation) {
        throw new Error('会话不存在')
      }
      
      currentConversation.value = conversation
      
      // 获取会话消息
      const response = await get<{ messages: Message[] }>(`/conversations/${conversationId}`)
      messages.value = response.data.messages || []
    } catch (error) {
      console.error('选择会话失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除会话
  const deleteConversation = async (conversationId: string) => {
    try {
      await del(`/conversations/${conversationId}`)
      
      // 从列表中移除
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      
      // 如果删除的是当前会话，清空当前会话
      if (currentConversation.value?.id === conversationId) {
        currentConversation.value = null
        messages.value = []
      }
    } catch (error) {
      console.error('删除会话失败:', error)
      throw error
    }
  }

  // 发送消息
  const sendMessage = async (content: string) => {
    if (!currentConversation.value) {
      throw new Error('请先选择或创建一个会话')
    }
    
    if (isStreaming.value) {
      throw new Error('正在发送消息，请稍候')
    }

    // 添加用户消息到界面
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: currentConversation.value.id,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)

    isStreaming.value = true
    let assistantMessage: Message | null = null
    let assistantContent = ''
    let sseConnection: any = null

    try {
      const chatRequest: ChatRequest = {
        message: content,
        model: currentModel.value,
        system_prompt: systemPrompt.value
      }

      // 先发送聊天请求
      await post(`/chat/stream/${currentConversation.value.id}`, chatRequest)
      
      // 然后建立SSE连接接收流式响应
      sseConnection = createSSEConnection(`/chat/stream/${currentConversation.value.id}`, {
        onMessage: (event: SSEEvent) => {
          if (event.type === 'chunk') {
            assistantContent += event.content
            
            // 如果还没有助手消息，创建一个
            if (!assistantMessage) {
              assistantMessage = {
                id: `temp-assistant-${Date.now()}`,
                conversation_id: currentConversation.value!.id,
                role: 'assistant',
                content: assistantContent,
                created_at: new Date().toISOString()
              }
              messages.value.push(assistantMessage)
            } else {
              // 更新现有消息内容
              assistantMessage.content = assistantContent
            }
          } else if (event.type === 'done') {
            // 流结束，更新消息ID
            if (assistantMessage) {
              assistantMessage.id = event.message_id
            }
            sseConnection?.close()
            isStreaming.value = false
          }
        },
        onError: (error) => {
          console.error('SSE连接错误:', error)
          sseConnection?.close()
          isStreaming.value = false
        },
        onClose: () => {
          isStreaming.value = false
        }
      })
    } catch (error) {
      console.error('发送消息失败:', error)
      
      // 移除用户消息
      messages.value = messages.value.filter(msg => msg.id !== userMessage.id)
      
      if (sseConnection) {
        sseConnection.close()
      }
      
      isStreaming.value = false
      throw error
    }
  }

  // 评价消息
  const rateMessage = async (messageId: string, rating: number) => {
    try {
      await post(`/messages/${messageId}/rate`, { rating })
      
      // 更新本地消息评价
      const message = messages.value.find(msg => msg.id === messageId)
      if (message) {
        message.rating = rating
      }
    } catch (error) {
      console.error('评价消息失败:', error)
      throw error
    }
  }

  return {
    // 状态
    conversations,
    currentConversation,
    messages,
    currentModel,
    systemPrompt,
    isStreaming,
    availableModels,
    loading,
    
    // 计算属性
    hasConversations,
    currentMessages,
    
    // 方法
    fetchModels,
    fetchConversations,
    createConversation,
    selectConversation,
    deleteConversation,
    sendMessage,
    rateMessage
  }
})