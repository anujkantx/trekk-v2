<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-5">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <i class="bi bi-compass text-warning display-4"></i>
              <h2 class="fw-bold mt-2">Welcome Back</h2>
              <p class="text-muted small">Sign in to manage your treks and bookings</p>
            </div>

            <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-1"></i> {{ errorMessage }}
            </div>

            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label small fw-semibold">Username or Email</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-person"></i></span>
                  <input
                    v-model="form.identifier"
                    type="text"
                    class="form-control"
                    placeholder="e.g. admin or trekker@example.com"
                    required
                  />
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label small fw-semibold">Password</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-lock"></i></span>
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100 py-2 fw-semibold"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <span>{{ loading ? 'Signing In...' : 'Sign In' }}</span>
              </button>
            </form>

            <div class="text-center mt-4 pt-2 border-top">
              <span class="text-muted small">Don't have an account? </span>
              <router-link to="/register" class="small fw-semibold text-decoration-none">
                Register as Trekker
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api, { authState } from '../api'

const router = useRouter()
const route = useRoute()

const form = reactive({
  identifier: '',
  password: ''
})

const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true

  try {
    const res = await api.post('/auth/login', {
      identifier: form.identifier.trim(),
      password: form.password
    })

    const { token, user } = res.data.data
    authState.setAuth(token, user)

    const redirectPath = route.query.redirect
    if (redirectPath) {
      router.push(redirectPath)
    } else if (user.role === 'admin') {
      router.push('/admin')
    } else if (user.role === 'staff') {
      router.push('/staff')
    } else {
      router.push('/my-bookings')
    }
  } catch (err) {
    if (err.response && err.response.data && err.response.data.message) {
      errorMessage.value = err.response.data.message
    } else {
      errorMessage.value = 'Failed to connect to backend server. Make sure Flask is running.'
    }
  } finally {
    loading.value = false
  }
}
</script>
