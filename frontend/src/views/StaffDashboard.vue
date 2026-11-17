<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-0">Staff Portal</h2>
      </div>
      <div>
        <button @click="fetchTreks" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Alert Messages -->
    <div v-if="alert.message" :class="`alert alert-${alert.type} alert-dismissible fade show small py-2`">
      <i :class="alert.type === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-1"></i>
      {{ alert.message }}
      <button type="button" class="btn-close py-2" @click="alert.message = ''"></button>
    </div>

    <!-- Assigned Treks Section -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted mt-2 small">Loading your assigned treks...</p>
    </div>

    <div v-else-if="treks.length === 0" class="card border-0 shadow-sm text-center py-5">
      <div class="card-body">
        <i class="bi bi-compass text-muted display-4"></i>
        <h5 class="fw-bold mt-3">No Assigned Treks</h5>
        <p class="text-muted small">You currently have no treks assigned to your profile. Please contact an administrator.</p>
      </div>
    </div>

    <div v-else class="row g-4">
      <div v-for="t in treks" :key="t.id" class="col-12 col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body p-4 d-flex flex-column">
            <!-- Top Badges -->
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span
                class="badge text-white px-2 py-1"
                :class="{
                  'badge-easy': t.difficulty === 'Easy',
                  'badge-moderate': t.difficulty === 'Moderate',
                  'badge-hard': t.difficulty === 'Hard'
                }"
              >
                {{ t.difficulty }}
              </span>
              <div class="dropdown">
                <button
                  class="btn btn-sm dropdown-toggle fw-semibold text-uppercase px-2 py-1"
                  :class="{
                    'btn-success': t.status === 'Open',
                    'btn-info text-white': t.status === 'Approved',
                    'btn-warning text-dark': t.status === 'Pending',
                    'btn-secondary': t.status === 'Closed',
                    'btn-primary': t.status === 'Completed'
                  }"
                  type="button"
                  data-bs-toggle="dropdown"
                >
                  {{ t.status }}
                </button>
                <ul class="dropdown-menu dropdown-menu-end shadow-sm small">
                  <li><h6 class="dropdown-header">Change Trek Status</h6></li>
                  <li v-for="st in ['Open', 'Closed', 'Completed']" :key="st">
                    <button
                      class="dropdown-item"
                      :class="{ 'active': t.status === st }"
                      @click="changeStatus(t, st)"
                    >
                      Mark as {{ st }}
                    </button>
                  </li>
                </ul>
              </div>
            </div>

            <h5 class="card-title fw-bold text-dark mb-1">{{ t.name }}</h5>
            <p class="text-muted small mb-3">
              <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ t.location }}
            </p>

            <div class="row g-2 text-center bg-light p-2 rounded mb-3 small">
              <div class="col-6 border-end">
                <span class="text-muted d-block">Timeline</span>
                <span class="fw-semibold">{{ formatDate(t.start_date) }} - {{ formatDate(t.end_date) }}</span>
              </div>
              <div class="col-6">
                <span class="text-muted d-block">Slots Available</span>
                <span class="fw-bold" :class="t.available_slots > 0 ? 'text-success' : 'text-danger'">
                  {{ t.available_slots }} / {{ t.total_slots }}
                </span>
              </div>
            </div>

            <p class="text-secondary small mb-4 flex-grow-1">
              {{ t.description }}
            </p>

            <div class="mt-auto d-flex justify-content-between align-items-center pt-2 border-top">
              <span class="fs-5 fw-bold text-primary">₹{{ t.price.toLocaleString('en-IN') }}</span>
              <button
                @click="openParticipantsModal(t)"
                class="btn btn-outline-primary btn-sm fw-semibold"
              >
                <i class="bi bi-people-fill me-1"></i> View Participants
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Participants Modal -->
    <div
      class="modal fade"
      id="participantsModal"
      tabindex="-1"
      aria-hidden="true"
      ref="modalRef"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-bottom d-flex justify-content-between align-items-center">
            <h5 class="modal-title fw-bold">
              Participants: {{ selectedTrek ? selectedTrek.name : '' }}
            </h5>
            <div class="d-flex align-items-center gap-2">
              <button
                v-if="participants.length > 0"
                @click="exportRosterCsv"
                :disabled="exportingRoster"
                class="btn btn-outline-success btn-sm fw-semibold"
              >
                <span v-if="exportingRoster" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-file-earmark-spreadsheet me-1"></i>
                {{ exportingRoster ? 'Exporting...' : 'Export CSV' }}
              </button>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
          </div>

          <div class="modal-body p-0">
            <div v-if="modalLoading" class="text-center py-4">
              <div class="spinner-border text-primary spinner-border-sm" role="status"></div>
              <p class="text-muted mt-2 small">Loading participants roster...</p>
            </div>

            <div v-else-if="participants.length === 0" class="text-center py-5">
              <i class="bi bi-person-x text-muted display-4"></i>
              <p class="text-muted mt-2">No bookings recorded for this expedition yet.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light small text-muted">
                  <tr>
                    <th class="ps-3">Booking ID</th>
                    <th>Trekker</th>
                    <th>Email</th>
                    <th>Slots</th>
                    <th>Status</th>
                    <th class="text-end pe-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in participants" :key="p.id">
                    <td class="ps-3 fw-bold text-muted">#{{ p.id }}</td>
                    <td class="fw-semibold text-dark">{{ p.username }}</td>
                    <td class="small text-muted">{{ p.user_email }}</td>
                    <td>
                      <span class="badge bg-light text-dark border">
                        {{ p.num_slots }} {{ p.num_slots === 1 ? 'Slot' : 'Slots' }}
                      </span>
                    </td>
                    <td>
                      <span
                        class="badge px-2 py-1"
                        :class="{
                          'bg-success': p.status === 'Booked',
                          'bg-primary': p.status === 'Completed',
                          'bg-secondary': p.status === 'Cancelled'
                        }"
                      >
                        {{ p.status }}
                      </span>
                    </td>
                    <td class="text-end pe-3">
                      <button
                        v-if="p.status === 'Booked' && selectedTrek && selectedTrek.status === 'Completed'"
                        @click="updateBookingStatus(p, 'Completed')"
                        class="btn btn-outline-primary btn-sm py-0"
                      >
                        Complete
                      </button>
                      <button
                        v-else-if="p.status === 'Booked'"
                        @click="updateBookingStatus(p, 'Cancelled')"
                        class="btn btn-outline-danger btn-sm py-0"
                      >
                        Cancel
                      </button>
                      <span v-else class="text-muted small">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="modal-footer border-top">
            <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'

const treks = ref([])
const loading = ref(true)
const alert = reactive({ type: '', message: '' })

const selectedTrek = ref(null)
const participants = ref([])
const modalLoading = ref(false)
const exportingRoster = ref(false)
let bootstrapModalInstance = null

const fetchTreks = async () => {
  loading.value = true
  try {
    const res = await api.get('/treks')
    treks.value = res.data.data
  } catch (err) {
    showAlert('danger', 'Failed to load assigned treks.')
  } finally {
    loading.value = false
  }
}

const changeStatus = async (trek, newStatus) => {
  if (trek.status === newStatus) return

  try {
    await api.patch(`/treks/${trek.id}/status`, { status: newStatus })
    showAlert('success', `Trek status updated to "${newStatus}"`)
    await fetchTreks()
  } catch (err) {
    const msg = err.response?.data?.message || 'Failed to update trek status.'
    showAlert('danger', msg)
  }
}

const openParticipantsModal = async (trek) => {
  selectedTrek.value = trek
  modalLoading.value = true
  participants.value = []

  // Initialize Bootstrap modal lazily
  const modalEl = document.getElementById('participantsModal')
  if (window.bootstrap && !bootstrapModalInstance) {
    bootstrapModalInstance = new window.bootstrap.Modal(modalEl)
  }
  if (bootstrapModalInstance) {
    bootstrapModalInstance.show()
  }

  try {
    const res = await api.get('/bookings', { params: { trek_id: trek.id } })
    participants.value = res.data.data
  } catch (err) {
    showAlert('danger', 'Failed to load participants.')
  } finally {
    modalLoading.value = false
  }
}

const exportRosterCsv = async () => {
  if (!selectedTrek.value) return
  exportingRoster.value = true
  try {
    const res = await api.get(`/treks/${selectedTrek.value.id}/roster/csv`, {
      responseType: 'blob'
    })
    const filename = `roster_trek_${selectedTrek.value.id}.csv`
    const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showAlert('success', 'Participant roster exported successfully.')
  } catch (err) {
    showAlert('danger', 'Failed to export participant roster.')
  } finally {
    exportingRoster.value = false
  }
}

const updateBookingStatus = async (booking, status) => {
  try {
    await api.put(`/bookings/${booking.id}`, { status })
    showAlert('success', `Booking #${booking.id} marked as ${status}`)
    // Refresh participants list
    if (selectedTrek.value) {
      const res = await api.get('/bookings', { params: { trek_id: selectedTrek.value.id } })
      participants.value = res.data.data
    }
    await fetchTreks()
  } catch (err) {
    const msg = err.response?.data?.message || 'Failed to update booking status.'
    showAlert('danger', msg)
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
  fetchTreks()
})
</script>
