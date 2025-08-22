import { defineStore } from 'pinia'
import { ref } from 'vue'
import { post, get } from '@/utils/api'

interface User {
  id: string
  username: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const isChecked = ref(false)
  const loading = ref(false)

  const login = async (username: string, password: string): Promise<boolean> => {
    loading.value = true
    try {
      const response = await post<User>('/auth/login', {
        username,
        password
      })
      
      if (response.status === 200) {
        user.value = response.data
        isAuthenticated.value = true
        return true
      }
      return false
    } catch (error) {
      console.error('Login failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    loading.value = true
    try {
      await post('/auth/logout')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      user.value = null
      isAuthenticated.value = false
      loading.value = false
    }
  }

  const checkAuth = async (): Promise<void> => {
    if (isChecked.value) return
    
    loading.value = true
    try {
      const response = await get<User>('/auth/me')
      
      if (response.status === 200) {
        user.value = response.data
        isAuthenticated.value = true
      } else {
        // 非200状态码，清除认证状态
        user.value = null
        isAuthenticated.value = false
      }
    } catch (error: any) {
      console.error('Auth check failed:', error)
      user.value = null
      isAuthenticated.value = false
      
      // 如果是网络错误或请求被中断，重新抛出错误
      if (error.code === 'ERR_ABORTED' || error.message?.includes('aborted') || !error.response) {
        throw error
      }
    } finally {
      isChecked.value = true
      loading.value = false
    }
  }

  return {
    user,
    isAuthenticated,
    isChecked,
    loading,
    login,
    logout,
    checkAuth
  }
})