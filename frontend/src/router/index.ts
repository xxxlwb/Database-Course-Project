import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    children: [
      { path: '', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'topics', component: () => import('../views/Topics.vue') },
      { path: 'topics/:id', component: () => import('../views/TopicDetail.vue') },
      { path: 'topics/:id/graph', component: () => import('../views/Graph.vue') },
      { path: 'documents', component: () => import('../views/Documents.vue') },
      { path: 'documents/:id', component: () => import('../views/DocumentDetail.vue') },
      { path: 'entities', component: () => import('../views/Entities.vue') },
      { path: 'relationships', component: () => import('../views/Relationships.vue') },
      { path: 'jobs', component: () => import('../views/Jobs.vue') },
      { path: 'audit', component: () => import('../views/Audit.vue') },
      { path: 'dev/sql', component: () => import('../views/SqlConsole.vue') },
      { path: 'settings', component: () => import('../views/Settings.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) return next()
  if (!auth.user) return next('/login')
  next()
})

export default router
