import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/chat'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../pages/LoginPage.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/chat',
      name: 'Chat',
      component: () => import('../pages/ChatPage.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, _, next) => {
  const authStore = useAuthStore()
  
  // 对于登录页面，直接允许访问
  if (to.path === '/login') {
    next()
    return
  }
  
  // 检查用户认证状态
  if (!authStore.isChecked) {
    try {
      await authStore.checkAuth()
    } catch (error) {
      console.warn('认证检查失败，跳转到登录页面:', error)
      // 认证检查失败时，跳转到登录页面
      next('/login')
      return
    }
  }
  
  // 需要认证的页面
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 游客页面（已登录用户不能访问）
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/chat')
    return
  }
  
  next()
})

export default router