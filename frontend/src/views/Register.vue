<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-6">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <i class="bi bi-person-plus-fill text-warning display-4"></i>
              <h2 class="fw-bold mt-2">Create Account</h2>
              <p class="text-muted small">Register as a trekker to book exciting expeditions</p>
            </div>

            <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-1"></i> {{ errorMessage }}
            </div>

            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label class="form-label small fw-semibold">Username</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-person"></i></span>
                  <input
                    v-model="form.username"
                    type="text"
                    class="form-control"
                    placeholder="Choose a username"
                    required
                  />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold">Email Address</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-envelope"></i></span>
                  <input
                    v-model="form.email"
                    type="email"
                    class="form-control"
                    placeholder="name@example.com"
                    required
                  />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold">Contact Number (Optional)</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-telephone"></i></span>
                  <input
                    v-model="form.contact_number"
                    type="tel"
                    class="form-control"
                    placeholder="10-digit mobile number"
                  />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label small fw-semibold">Password</label>
                  <input
                    v-model="form.password"
                    type="password"
                    class="form-control"
                    placeholder="At least 6 characters"
                    required
                  />
                </div>
                <div class="col-md-6 mb-4">
                  <label class="form-label small fw-semibold">Confirm Password</label>
                  <input
                    v-model="form.confirmPassword"
                    type="password"
                    class="form-control"
                    placeholder="Repeat password"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                class="btn btn-warning text-dark w-100 py-2 fw-semibold"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <span>{{ loading ? 'Creating Account...' : 'Register' }}</span>
              </button>
            </form>

            <div class="text-center mt-4 pt-2 border-top">
              <span class="text-muted small">Already registered? </span>
              <router-link to="/login" class="small fw-semibold text-decoration-none">
                Sign In
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
import { useRouter } from 'vue-router'
import api, { authState } from '../api'

const router = useRouter()

const form = reactive({
  username: '',
  email: '',
  contact_number: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  errorMessage.value = ''

  if (form.password !== form.confirmPassword) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  if (form.password.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters long.'
    return
  }

  loading.value = true

  try {
    await api.post('/auth/register', {
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
      contact_number: form.contact_number.trim() || null
    })

    // Auto login right after registration
    const loginRes = await api.post('/auth/login', {
      identifier: form.username.trim(),
      password: form.password
    })

    const token = loginRes.data.data.access_token || loginRes.data.data.token
    const user = loginRes.data.data.user
    authState.setAuth(token, user)
    router.push('/my-bookings')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.message) {
      errorMessage.value = err.response.data.message
    } else {
      errorMessage.value = 'Registration failed. Please check your connection.'
    }
  } finally {
    loading.value = false
  }
}
</script>
