<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
      <div>
        <h2 class="fw-bold mb-1">
          <i class="bi bi-person-circle text-primary me-2"></i>My Trekker Dashboard
        </h2>
        <p class="text-muted small mb-0">Manage your adventure reservations and booking history</p>
      </div>
      <div>
        <button
          @click="triggerExport"
          class="btn btn-outline-success btn-sm fw-semibold"
          :disabled="exportLoading"
        >
          <span v-if="exportLoading" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-file-earmark-spreadsheet me-1"></i>
          <span>{{ exportLoading ? 'Exporting...' : 'Export History to CSV' }}</span>
        </button>
      </div>
    </div>

    <!-- Alert Messages -->
    <div v-if="alert.message" :class="`alert alert-${alert.type} alert-dismissible fade show small py-2`">
      <i :class="alert.type === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-1"></i>
      {{ alert.message }}
      <button type="button" class="btn-close py-2" @click="alert.message = ''"></button>
    </div>

    <!-- Metrics Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3">
          <span class="text-muted small">Total Bookings</span>
          <span class="fs-3 fw-bold text-dark">{{ bookings.length }}</span>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3">
          <span class="text-muted small">Active Expeditions</span>
          <span class="fs-3 fw-bold text-success">{{ countByStatus('Booked') }}</span>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3">
          <span class="text-muted small">Completed Treks</span>
          <span class="fs-3 fw-bold text-primary">{{ countByStatus('Completed') }}</span>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center p-3">
          <span class="text-muted small">Cancelled</span>
          <span class="fs-3 fw-bold text-secondary">{{ countByStatus('Cancelled') }}</span>
        </div>
      </div>
    </div>

    <!-- Bookings Table Card -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
        <h5 class="fw-bold mb-0">Booking History</h5>
        <button @click="fetchBookings" class="btn btn-sm btn-outline-secondary">
          <i class="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>

      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary spinner-border-sm" role="status"></div>
          <p class="text-muted mt-2 small">Loading your bookings...</p>
        </div>

        <div v-else-if="bookings.length === 0" class="text-center py-5">
          <i class="bi bi-backpack text-muted display-4"></i>
          <p class="text-muted mt-3 mb-2">You haven't booked any treks yet.</p>
          <router-link to="/" class="btn btn-primary btn-sm">Explore Open Treks</router-link>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light small text-muted">
              <tr>
                <th class="ps-3">ID</th>
                <th>Trek Details</th>
                <th>Schedule</th>
                <th>Slots</th>
                <th>Status</th>
                <th>Booked On</th>
                <th class="text-end pe-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td class="ps-3 fw-bold text-muted">#{{ b.id }}</td>
                <td>
                  <router-link :to="`/treks/${b.trek_id}`" class="fw-semibold text-dark text-decoration-none">
                    {{ b.trek_name }}
                  </router-link>
                  <span class="d-block text-muted small">
                    <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ b.trek_location }}
                  </span>
                </td>
                <td class="small text-muted">
                  <div>{{ formatDate(b.trek_start_date) }}</div>
                  <div class="text-secondary opacity-75">to {{ formatDate(b.trek_end_date) }}</div>
                </td>
                <td>
                  <span class="badge bg-light text-dark border px-2 py-1">
                    {{ b.num_slots }} {{ b.num_slots === 1 ? 'Slot' : 'Slots' }}
                  </span>
                </td>
                <td>
                  <span
                    class="badge px-2 py-1"
                    :class="{
                      'bg-success': b.status === 'Booked',
                      'bg-primary': b.status === 'Completed',
                      'bg-secondary': b.status === 'Cancelled'
                    }"
                  >
                    {{ b.status }}
                  </span>
                </td>
                <td class="small text-muted">{{ formatDate(b.booking_date) }}</td>
                <td class="text-end pe-3">
                  <button
                    v-if="b.can_cancel"
                    @click="confirmCancel(b)"
                    class="btn btn-outline-danger btn-sm"
                    :disabled="cancellingId === b.id"
                  >
                    <span v-if="cancellingId === b.id" class="spinner-border spinner-border-sm"></span>
                    <span v-else><i class="bi bi-x-circle me-1"></i>Cancel</span>
                  </button>
                  <span v-else-if="b.status === 'Booked'" class="badge bg-light text-muted small border">
                    Past Cutoff
                  </span>
                  <span v-else class="text-muted small">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Export Jobs Section -->
    <div v-if="exportJobs.length > 0" class="card border-0 shadow-sm">
      <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
        <h6 class="fw-bold mb-0">
          <i class="bi bi-clock-history me-1"></i> Generated CSV Downloads
        </h6>
        <button @click="fetchExportJobs" class="btn btn-link btn-sm text-decoration-none p-0">
          Refresh List
        </button>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm align-middle mb-0">
            <thead class="table-light small text-muted">
              <tr>
                <th class="ps-3">Job ID</th>
                <th>Requested At</th>
                <th>Status</th>
                <th class="text-end pe-3">Download</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in exportJobs" :key="job.id">
                <td class="ps-3 fw-bold">#{{ job.id }}</td>
                <td class="small text-muted">{{ formatDate(job.created_at) }}</td>
                <td>
                  <span
                    class="badge"
                    :class="{
                      'bg-success': job.status === 'COMPLETED',
                      'bg-warning text-dark': job.status === 'PENDING' || job.status === 'PROCESSING',
                      'bg-danger': job.status === 'FAILED'
                    }"
                  >
                    {{ job.status }}
                  </span>
                </td>
                <td class="text-end pe-3">
                  <a
                    v-if="job.status === 'COMPLETED'"
                    :href="`/api/bookings/export/${job.id}/download`"
                    class="btn btn-outline-primary btn-sm py-0"
                    target="_blank"
                    download
                  >
                    <i class="bi bi-download me-1"></i> Download CSV
                  </a>
                  <span v-else class="text-muted small">Processing in Celery...</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'

const bookings = ref([])
const exportJobs = ref([])
const loading = ref(true)
const exportLoading = ref(false)
const cancellingId = ref(null)
const alert = reactive({ type: '', message: '' })

const fetchBookings = async () => {
  loading.value = true
  try {
    const res = await api.get('/bookings')
    bookings.value = res.data.data
  } catch (err) {
    showAlert('danger', 'Failed to load bookings.')
  } finally {
    loading.value = false
  }
}

const fetchExportJobs = async () => {
  try {
    const res = await api.get('/bookings/export-jobs')
    exportJobs.value = res.data.data
  } catch (err) {
    // Silent fail for export jobs
  }
}

const countByStatus = (status) => {
  return bookings.value.filter((b) => b.status === status).length
}

const confirmCancel = async (booking) => {
  if (!confirm(`Are you sure you want to cancel your booking for "${booking.trek_name}"? Restoring ${booking.num_slots} slot(s).`)) {
    return
  }

  cancellingId.value = booking.id
  try {
    await api.post(`/bookings/${booking.id}/cancel`)
    showAlert('success', `Booking #${booking.id} has been cancelled and slots restored.`)
    await fetchBookings()
  } catch (err) {
    const msg = err.response?.data?.message || 'Failed to cancel booking.'
    showAlert('danger', msg)
  } finally {
    cancellingId.value = null
  }
}

const triggerExport = async () => {
  exportLoading.value = true
  try {
    const res = await api.post('/bookings/export')
    showAlert('success', res.data.message || 'CSV export initiated. Processing in background.')
    await fetchExportJobs()
  } catch (err) {
    showAlert('danger', 'Failed to trigger export.')
  } finally {
    exportLoading.value = false
  }
}

const showAlert = (type, message) => {
  alert.type = type
  alert.message = message
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(() => {
  fetchBookings()
  fetchExportJobs()
})
</script>
