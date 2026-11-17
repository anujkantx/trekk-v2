import { createRouter, createWebHistory } from 'vue-router'
import { authState } from '../api'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/treks/:id',
    name: 'TrekDetail',
    component: () => import('../views/TrekDetail.vue')
  },
  {
    path: '/my-bookings',
    name: 'UserDashboard',
    component: () => import('../views/UserDashboard.vue'),
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/staff',
    name: 'StaffDashboard',
    component: () => import('../views/StaffDashboard.vue'),
    meta: { requiresAuth: true, role: 'staff' }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Role-based Navigation Guard
router.beforeEach((to, from, next) => {
  const isAuth = authState.isAuthenticated()
  const role = authState.getRole()

  if (to.meta.requiresAuth && !isAuth) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (to.meta.role && to.meta.role !== role) {
    if (role === 'admin') return next('/admin')
    if (role === 'staff') return next('/staff')
    return next('/my-bookings')
  }

  if (to.meta.guestOnly && isAuth) {
    if (role === 'admin') return next('/admin')
    if (role === 'staff') return next('/staff')
    return next('/my-bookings')
  }

  next()
})

export default router
