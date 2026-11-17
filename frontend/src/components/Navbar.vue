<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom sticky-top">
    <div class="container">
      <router-link to="/" class="navbar-brand fw-bold d-flex align-items-center text-dark" title="Explore Treks">
        <i class="bi bi-backpack2-fill me-2 text-primary fs-4"></i>
        <span>TrekManagement</span>
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li v-if="user && user.role === 'user'" class="nav-item">
            <router-link to="/my-bookings" class="nav-link text-secondary" active-class="active fw-semibold text-primary">
              <i class="bi bi-bookmark-check-fill me-1"></i> My Bookings
            </router-link>
          </li>
          <li v-if="user && user.role === 'staff'" class="nav-item">
            <router-link to="/staff" class="nav-link text-secondary" active-class="active fw-semibold text-primary">
              <i class="bi bi-clipboard2-check-fill me-1"></i> Staff Portal
            </router-link>
          </li>
          <li v-if="user && user.role === 'admin'" class="nav-item">
            <router-link to="/admin" class="nav-link text-secondary" active-class="active fw-semibold text-primary">
              <i class="bi bi-speedometer2 me-1"></i> Admin Panel
            </router-link>
          </li>
        </ul>

        <div class="d-flex align-items-center">
          <template v-if="user">
            <span class="badge bg-light text-dark border me-3 px-3 py-2 text-capitalize">
              <i class="bi bi-person-circle me-1 text-primary"></i> {{ user.username }} ({{ user.role }})
            </span>
            <button @click="logout" class="btn btn-outline-danger btn-sm">
              <i class="bi bi-box-arrow-right me-1"></i> Logout
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn btn-outline-primary btn-sm me-2">
              <i class="bi bi-box-arrow-in-right me-1"></i> Login
            </router-link>
            <router-link to="/register" class="btn btn-primary btn-sm fw-semibold">
              <i class="bi bi-person-plus me-1"></i> Register
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authState } from '../api'

const router = useRouter()
const route = useRoute()
const user = ref(authState.getUser())

const updateAuthUser = () => {
  user.value = authState.getUser()
}

watch(route, () => {
  updateAuthUser()
})

onMounted(() => {
  updateAuthUser()
})

const logout = () => {
  authState.clearAuth()
  updateAuthUser()
  router.push('/login')
}
</script>
