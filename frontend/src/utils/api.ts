import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// JWT Token 管理
const TOKEN_KEY = 'jwt_token'

export const tokenManager = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },
  
  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },
  
  removeToken(): void {
    localStorage.removeItem(TOKEN_KEY)
  },
  
  hasToken(): boolean {
    return !!this.getToken()
  }
}

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加JWT token到请求头
    const token = tokenManager.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    console.error('Response error:', error)
    
    // 处理常见错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('请先登录后再操作')
          // 清除无效token
          tokenManager.removeToken()
          // 自动跳转到登录页面
          setTimeout(() => {
            if (window.location.pathname !== '/login') {
              window.location.href = '/login'
            }
          }, 1500)
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.detail || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络或稍后重试')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default api

// 导出常用的请求方法
export const get = <T = any>(url: string, params?: any): Promise<AxiosResponse<T>> => {
  return api.get(url, { params })
}

export const post = <T = any>(url: string, data?: any): Promise<AxiosResponse<T>> => {
  return api.post(url, data)
}

export const put = <T = any>(url: string, data?: any): Promise<AxiosResponse<T>> => {
  return api.put(url, data)
}

export const del = <T = any>(url: string): Promise<AxiosResponse<T>> => {
  return api.delete(url)
}

// SSE连接工具函数
export const createSSEConnection = (url: string, options: {
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  onClose?: () => void
  signal?: AbortSignal
} = {}) => {
  const { onMessage, onError, onClose, signal } = options
  
  const eventSource = new EventSource(`http://localhost:8000${url}`, {
    withCredentials: true
  })
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage?.(data)
    } catch (error) {
      console.error('Failed to parse SSE data:', error)
    }
  }
  
  eventSource.onerror = (error) => {
    console.error('SSE error:', error)
    onError?.(error)
  }
  
  eventSource.onopen = () => {
    console.log('SSE connection opened')
  }
  
  // 处理中断信号
  if (signal) {
    signal.addEventListener('abort', () => {
      eventSource.close()
      onClose?.()
    })
  }
  
  return {
    close: () => {
      eventSource.close()
      onClose?.()
    },
    readyState: () => eventSource.readyState
  }
}