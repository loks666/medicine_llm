// 用户相关类型
export interface User {
  id: string
  username: string
}

export interface LoginRequest {
  username: string
  password: string
}

// 模型相关类型
export interface Model {
  id: string
  name: string
  description?: string
}

// 会话相关类型
export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface CreateConversationRequest {
  title: string
}

export interface ConversationWithMessages {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: Message[]
}

// 消息相关类型
export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  rating?: number
  created_at: string
}

export interface ChatRequest {
  message: string
  model?: string
  system_prompt?: string
}

export interface RateMessageRequest {
  rating: number
}

// SSE事件类型
export interface SSEChunk {
  type: 'chunk'
  content: string
}

export interface SSEDone {
  type: 'done'
  message_id: string
}

export type SSEEvent = SSEChunk | SSEDone

// API响应类型
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}

export interface ApiError {
  detail: string
  status: number
}

// 组件Props类型
export interface MessageItemProps {
  message: Message
  onRate?: (messageId: string, rating: number) => void
}

export interface ConversationItemProps {
  conversation: Conversation
  isActive: boolean
  onSelect: (conversationId: string) => void
  onDelete: (conversationId: string) => void
}

// 工具函数类型
export interface SSEConnectionOptions {
  onMessage?: (data: SSEEvent) => void
  onError?: (error: Event) => void
  onClose?: () => void
  signal?: AbortSignal
}

export interface SSEConnection {
  close: () => void
  readyState: () => number
}