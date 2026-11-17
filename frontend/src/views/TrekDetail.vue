<template>
  <div class="container py-4">
    <div class="mb-3">
      <router-link to="/" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-arrow-left me-1"></i> Back to All Treks
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading trek...</span>
      </div>
    </div>

    <div v-else-if="errorMessage" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ errorMessage }}
    </div>

    <div v-else-if="trek" class="row g-4">
      <!-- Left Column: Trek Info -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm p-4 mb-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span
              class="badge text-white px-3 py-2 text-uppercase fs-6"
              :class="{
                'badge-easy': trek.difficulty === 'Easy',
                'badge-moderate': trek.difficulty === 'Moderate',
                'badge-hard': trek.difficulty === 'Hard'
              }"
            >
              {{ trek.difficulty }} Difficulty
            </span>
            <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-3 py-2">
              Status: {{ trek.status }}
            </span>
          </div>

          <h2 class="fw-bold mb-2">{{ trek.name }}</h2>
          <p class="text-muted fs-5 mb-4">
            <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ trek.location }}
          </p>

          <div class="row g-3 text-center my-2 p-3 bg-light rounded">
            <div class="col-4 border-end">
              <span class="text-muted small d-block">Start Date</span>
              <span class="fw-bold text-dark">{{ formatDate(trek.start_date) }}</span>
            </div>
            <div class="col-4 border-end">
              <span class="text-muted small d-block">End Date</span>
              <span class="fw-bold text-dark">{{ formatDate(trek.end_date) }}</span>
            </div>
            <div class="col-4">
              <span class="text-muted small d-block">Available Slots</span>
              <span class="fw-bold" :class="trek.available_slots > 0 ? 'text-success' : 'text-danger'">
                {{ trek.available_slots }} / {{ trek.total_slots }}
              </span>
            </div>
          </div>

          <h5 class="fw-bold mt-4 mb-3">About The Trek</h5>
          <p class="text-secondary lh-lg" style="white-space: pre-line;">
            {{ trek.description }}
          </p>
        </div>
      </div>

      <!-- Right Column: Booking Box -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm p-4 sticky-top" style="top: 80px;">
          <h4 class="fw-bold mb-3">Reserve Your Spot</h4>

          <div class="mb-4">
            <span class="text-muted small d-block">Price per participant</span>
            <span class="fs-2 fw-bold text-primary">₹{{ trek.price.toLocaleString('en-IN') }}</span>
          </div>

          <div v-if="bookingAlert.message" :class="`alert alert-${bookingAlert.type} py-2 small mb-3`">
            <i :class="bookingAlert.type === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-1"></i>
            {{ bookingAlert.message }}
          </div>

          <!-- If Not Logged In -->
          <div v-if="!isLoggedIn" class="text-center py-3 border rounded bg-light mb-3">
            <p class="small text-muted mb-2">You need to sign in to book this trek.</p>
            <router-link :to="`/login?redirect=/treks/${trek.id}`" class="btn btn-primary btn-sm w-100">
              Sign In to Book
            </router-link>
          </div>

          <!-- If Logged in as Admin or Staff -->
          <div v-else-if="userRole !== 'user'" class="alert alert-info small mb-3">
            <i class="bi bi-info-circle me-1"></i>
            You are signed in as <strong>{{ userRole }}</strong>. Bookings are reserved for trekkers. You can manage this trek from your dashboard.
          </div>

          <!-- If Sold Out -->
          <div v-else-if="trek.available_slots === 0" class="alert alert-danger text-center small mb-3">
            <i class="bi bi-x-circle-fill me-1"></i> This trek is completely sold out.
          </div>

          <!-- Booking Form for Trekker -->
          <form v-else @submit.prevent="handleBooking">
            <div class="mb-3">
              <label class="form-label small fw-semibold">Number of Slots</label>
              <select v-model.number="slotsToBook" class="form-select">
                <option v-for="n in maxSelectableSlots" :key="n" :value="n">
                  {{ n }} {{ n === 1 ? 'Slot' : 'Slots' }}
                </option>
              </select>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3 py-2 border-top border-bottom">
              <span class="fw-semibold">Total Amount:</span>
              <span class="fs-4 fw-bold text-success">
                ₹{{ (slotsToBook * trek.price).toLocaleString('en-IN') }}
              </span>
            </div>

            <button
              type="submit"
              class="btn btn-success w-100 py-2 fw-semibold"
              :disabled="bookingLoading"
            >
              <span v-if="bookingLoading" class="spinner-border spinner-border-sm me-2"></span>
              <span>{{ bookingLoading ? 'Reserving...' : 'Confirm Booking' }}</span>
            </button>
          </form>

          <div class="text-muted small mt-3 text-center">
            <i class="bi bi-shield-check text-success me-1"></i> Free cancellation before trek start date.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { authState } from '../api'

const route = useRoute()
const router = useRouter()

const trek = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const slotsToBook = ref(1)
const bookingLoading = ref(false)
const bookingAlert = ref({ type: '', message: '' })

const isLoggedIn = computed(() => authState.isAuthenticated())
const userRole = computed(() => authState.getRole())

const maxSelectableSlots = computed(() => {
  if (!trek.value) return 1
  return Math.min(trek.value.available_slots, 10)
})

const fetchTrek = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get(`/treks/${route.params.id}`)
    trek.value = res.data.data
  } catch (err) {
    if (err.response && err.response.status === 404) {
      errorMessage.value = 'Trek not found or has not been opened to the public.'
    } else {
      errorMessage.value = 'Failed to load trek details.'
    }
  } finally {
    loading.value = false
  }
}

const handleBooking = async () => {
  bookingAlert.value = { type: '', message: '' }
  bookingLoading.value = true

  try {
    const res = await api.post('/bookings', {
      trek_id: trek.value.id,
      num_slots: slotsToBook.value
    })

    bookingAlert.value = {
      type: 'success',
      message: `Trek booked successfully! Booking #${res.data.data.id}`
    }

    // Refresh trek details to show updated remaining slots
    await fetchTrek()

    // Redirect to user dashboard after 1.5 seconds
    setTimeout(() => {
      router.push('/my-bookings')
    }, 1500)
  } catch (err) {
    if (err.response && err.response.data && err.response.data.message) {
      bookingAlert.value = {
        type: 'danger',
        message: err.response.data.message
      }
    } else {
      bookingAlert.value = {
        type: 'danger',
        message: 'Booking failed. Please try again.'
      }
    }
  } finally {
    bookingLoading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(() => {
  fetchTrek()
})
</script>
