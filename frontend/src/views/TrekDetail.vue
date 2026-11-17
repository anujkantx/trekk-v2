<template>
  <div class="container py-3 py-md-4">
    <!-- Breadcrumb / Back button -->
    <div class="mb-3">
      <router-link to="/" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-arrow-left me-1"></i> Back to All Treks
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading expedition details...</span>
      </div>
      <p class="text-muted small mt-2">Loading expedition details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="alert alert-danger shadow-sm" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ errorMessage }}
    </div>

    <!-- Main Trek Detail Content -->
    <div v-else-if="trek" class="row g-4">
      <!-- Left Column: Comprehensive Expedition Details -->
      <div class="col-lg-8">
        <div
          class="card trek-card border-0 shadow-sm p-4 mb-4"
          :class="{
            'trek-card-easy': trek.difficulty === 'Easy',
            'trek-card-moderate': trek.difficulty === 'Moderate',
            'trek-card-hard': trek.difficulty === 'Hard'
          }"
        >
          <!-- Top Badges Header -->
          <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
            <div class="d-flex gap-2 align-items-center">
              <span
                class="badge text-white px-3 py-2 text-uppercase fw-semibold"
                :class="{
                  'badge-easy': trek.difficulty === 'Easy',
                  'badge-moderate': trek.difficulty === 'Moderate',
                  'badge-hard': trek.difficulty === 'Hard'
                }"
              >
                {{ trek.difficulty }} Difficulty
              </span>
              <span v-if="trek.duration_days" class="badge bg-light text-secondary border px-3 py-2">
                <i class="bi bi-clock me-1 text-primary"></i>{{ trek.duration_days }} Days Expedition
              </span>
            </div>

            <span
              class="badge px-3 py-2 fw-semibold"
              :class="trek.status === 'Open' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-secondary-subtle text-secondary border'"
            >
              <i class="bi bi-circle-fill me-1" style="font-size: 0.5rem;"></i> {{ trek.status }}
            </span>
          </div>

          <!-- Trek Title & Location -->
          <h1 class="display-6 fw-bold text-dark mb-2">{{ trek.name }}</h1>
          <p class="text-muted fs-6 mb-4">
            <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ trek.location }}
          </p>

          <!-- Key Metrics Grid -->
          <div class="row g-2 text-center p-3 bg-light rounded-3 mb-4">
            <div class="col-4 border-end">
              <span class="text-muted small d-block">Start Date</span>
              <span class="fw-bold text-dark d-block">
                <i class="bi bi-calendar-event text-primary me-1"></i>{{ formatDate(trek.start_date) }}
              </span>
            </div>
            <div class="col-4 border-end">
              <span class="text-muted small d-block">End Date</span>
              <span class="fw-bold text-dark d-block">
                <i class="bi bi-flag-fill text-secondary me-1"></i>{{ formatDate(trek.end_date) }}
              </span>
            </div>
            <div class="col-4">
              <span class="text-muted small d-block">Available Inventory</span>
              <span class="fw-bold d-block" :class="trek.available_slots > 0 ? 'text-success' : 'text-danger'">
                {{ trek.available_slots }} / {{ trek.total_slots }} Slots
              </span>
            </div>
          </div>

          <!-- Description Section -->
          <h5 class="fw-bold text-dark mb-3">
            <i class="bi bi-file-text text-primary me-2"></i>About This Expedition
          </h5>
          <p class="text-secondary lh-lg mb-4" style="white-space: pre-line;">
            {{ trek.description }}
          </p>

          <hr class="my-4 opacity-25" />

          <!-- Included Highlights Box -->
          <h5 class="fw-bold text-dark mb-3">
            <i class="bi bi-check-circle-fill text-success me-2"></i>What's Included in This Trek
          </h5>
          <div class="row g-3">
            <div class="col-md-6">
              <div class="d-flex align-items-center p-2 rounded bg-light">
                <i class="bi bi-shield-check text-success fs-5 me-2"></i>
                <span class="small fw-semibold text-dark">Forest Permits & Entry Fees</span>
              </div>
            </div>
            <div class="col-md-6">
              <div class="d-flex align-items-center p-2 rounded bg-light">
                <i class="bi bi-person-badge text-primary fs-5 me-2"></i>
                <span class="small fw-semibold text-dark">
                  Certified Mountain Guide {{ trek.assigned_staff_name ? '(' + trek.assigned_staff_name + ')' : '' }}
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <div class="d-flex align-items-center p-2 rounded bg-light">
                <i class="bi bi-heart-pulse text-danger fs-5 me-2"></i>
                <span class="small fw-semibold text-dark">First Aid & Emergency Support</span>
              </div>
            </div>
            <div class="col-md-6">
              <div class="d-flex align-items-center p-2 rounded bg-light">
                <i class="bi bi-cup-hot text-warning fs-5 me-2"></i>
                <span class="small fw-semibold text-dark">Meals & Campsite Accommodation</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Sticky Booking Widget -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm p-4 sticky-top" style="top: 80px;">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">Reserve Spot</h4>
            <span v-if="trek.available_slots <= 5 && trek.available_slots > 0" class="badge bg-warning-subtle text-warning-emphasis border">
              Limited Seats
            </span>
          </div>

          <!-- Price Display -->
          <div class="bg-light p-3 rounded-3 mb-4">
            <span class="text-muted small d-block">Price per trekker</span>
            <span class="fs-2 fw-bold text-primary">₹{{ trek.price.toLocaleString('en-IN') }}</span>
            <span class="text-muted small d-block mt-1">All taxes & permits included</span>
          </div>

          <!-- Alerts -->
          <div v-if="bookingAlert.message" :class="`alert alert-${bookingAlert.type} py-2 small mb-3`">
            <i :class="bookingAlert.type === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-1"></i>
            {{ bookingAlert.message }}
          </div>

          <!-- If Not Logged In -->
          <div v-if="!isLoggedIn" class="text-center py-4 border rounded-3 bg-light mb-3">
            <i class="bi bi-lock-fill text-muted fs-3 d-block mb-2"></i>
            <p class="small text-muted mb-3">You need to sign in with your trekker account to reserve slots.</p>
            <router-link :to="`/login?redirect=/treks/${trek.id}`" class="btn btn-primary btn-sm px-4 fw-semibold">
              Sign In to Book
            </router-link>
          </div>

          <!-- If Logged in as Admin or Staff -->
          <div v-else-if="userRole !== 'user'" class="alert alert-info small mb-3">
            <i class="bi bi-info-circle me-1"></i>
            You are signed in as <strong>{{ userRole }}</strong>. Expeditions can only be booked by trekker accounts. Manage this trek from your dashboard.
          </div>

          <!-- If Sold Out -->
          <div v-else-if="trek.available_slots === 0" class="alert alert-danger text-center small mb-3">
            <i class="bi bi-x-circle-fill me-1"></i> All slots for this expedition are completely booked.
          </div>

          <!-- Booking Form for Trekker -->
          <form v-else @submit.prevent="handleBooking">
            <div class="mb-3">
              <label class="form-label small fw-semibold">Select Number of Slots</label>
              <select v-model.number="slotsToBook" class="form-select">
                <option v-for="n in maxSelectableSlots" :key="n" :value="n">
                  {{ n }} {{ n === 1 ? 'Slot' : 'Slots' }} (₹{{ (n * trek.price).toLocaleString('en-IN') }})
                </option>
              </select>
            </div>

            <!-- Price Breakdown Box -->
            <div class="p-3 bg-light rounded-3 mb-3 small">
              <div class="d-flex justify-content-between text-muted mb-1">
                <span>Base Fare ({{ slotsToBook }} x ₹{{ trek.price.toLocaleString('en-IN') }})</span>
                <span>₹{{ (slotsToBook * trek.price).toLocaleString('en-IN') }}</span>
              </div>
              <div class="d-flex justify-content-between text-muted mb-2">
                <span>Permits & Insurance</span>
                <span class="text-success fw-semibold">Free</span>
              </div>
              <hr class="my-1 opacity-25" />
              <div class="d-flex justify-content-between align-items-center pt-1">
                <span class="fw-bold text-dark">Total Amount:</span>
                <span class="fs-4 fw-bold text-success">
                  ₹{{ (slotsToBook * trek.price).toLocaleString('en-IN') }}
                </span>
              </div>
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100 py-2 fw-semibold shadow-sm"
              :disabled="bookingLoading"
            >
              <span v-if="bookingLoading" class="spinner-border spinner-border-sm me-2"></span>
              <span>{{ bookingLoading ? 'Reserving...' : 'Confirm Reservation' }}</span>
            </button>
          </form>

          <!-- Security & Guarantee Notices -->
          <div class="mt-3 pt-3 border-top small text-muted">
            <div class="d-flex align-items-center mb-1">
              <i class="bi bi-shield-check text-success me-2"></i>
              <span>Free cancellation before start date</span>
            </div>
            <div class="d-flex align-items-center">
              <i class="bi bi-lightning-charge-fill text-warning me-2"></i>
              <span>Instant slot reservation & confirmation</span>
            </div>
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
