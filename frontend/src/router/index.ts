import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/lookup-tables',
      name: 'lookup-tables',
      component: () => import('../views/LookupTablesView.vue'),
    },
    {
      path: '/agentes-infecciosos',
      name: 'agentes-infecciosos',
      component: () => import('../views/AgentesInfecciosView.vue'),
    },
    {
      path: '/doentes',
      name: 'doentes',
      component: () => import('../views/DoentesView.vue'),
    },
    {
      path: '/internamentos',
      name: 'internamentos',
      component: () => import('../views/InternamentosView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
