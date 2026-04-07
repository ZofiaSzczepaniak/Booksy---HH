import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  { path: '/login',   component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/',        component: () => import('../views/DashboardView.vue') },
  { path: '/admin',   component: () => import('../views/AdminView.vue'), meta: { admin: true } },
  { path: '/:path(.*)', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn) return '/login'
  if (to.meta.admin && !auth.isAdmin) return '/'
  if (to.path === '/login' && auth.isLoggedIn) return '/'
})

export default router
