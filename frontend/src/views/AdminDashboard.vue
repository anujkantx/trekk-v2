<template>
  <div class="container-fluid px-md-4 py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-0">Admin Dashboard</h2>
      </div>
      <div>
        <button @click="refreshAll" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh Data
        </button>
      </div>
    </div>

    <!-- Alert Messages -->
    <div v-if="alert.message" :class="`alert alert-${alert.type} alert-dismissible fade show small py-2`">
      <i :class="alert.type === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="me-1"></i>
      {{ alert.message }}
      <button type="button" class="btn-close py-2" @click="alert.message = ''"></button>
    </div>

    <!-- Navigation Tabs -->
    <ul class="nav nav-pills mb-4 gap-2">
      <li class="nav-item">
        <button
          class="nav-link fw-semibold"
          :class="{ 'active': activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >
          <i class="bi bi-bar-chart-fill me-1"></i> Overview
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link fw-semibold"
          :class="{ 'active': activeTab === 'treks' }"
          @click="activeTab = 'treks'"
        >
          <i class="bi bi-compass-fill me-1"></i> Treks
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link fw-semibold"
          :class="{ 'active': activeTab === 'staff' }"
          @click="activeTab = 'staff'"
        >
          <i class="bi bi-person-badge-fill me-1"></i> Staff
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link fw-semibold"
          :class="{ 'active': activeTab === 'users' }"
          @click="activeTab = 'users'"
        >
          <i class="bi bi-people-fill me-1"></i> Users
        </button>
      </li>
    </ul>

    <!-- TAB 1: OVERVIEW & ANALYTICS -->
    <div v-if="activeTab === 'overview'">
      <div v-if="statsLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
      <div v-else>
        <!-- Metric Cards -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-4 col-xl-2">
            <div class="card border-0 shadow-sm p-3 text-center">
              <span class="text-muted small">Registered Trekkers</span>
              <span class="fs-3 fw-bold text-dark">{{ stats.total_trekkers || 0 }}</span>
            </div>
          </div>
          <div class="col-6 col-md-4 col-xl-2">
            <div class="card border-0 shadow-sm p-3 text-center">
              <span class="text-muted small">Trek Staff</span>
              <span class="fs-3 fw-bold text-info">{{ stats.total_staff || 0 }}</span>
            </div>
          </div>
          <div class="col-6 col-md-4 col-xl-2">
            <div class="card border-0 shadow-sm p-3 text-center">
              <span class="text-muted small">Total Treks</span>
              <span class="fs-3 fw-bold text-primary">{{ stats.total_treks || 0 }}</span>
            </div>
          </div>
          <div class="col-6 col-md-4 col-xl-2">
            <div class="card border-0 shadow-sm p-3 text-center">
              <span class="text-muted small">Open For Booking</span>
              <span class="fs-3 fw-bold text-success">{{ stats.open_treks || 0 }}</span>
            </div>
          </div>
          <div class="col-6 col-md-4 col-xl-2">
            <div class="card border-0 shadow-sm p-3 text-center">
              <span class="text-muted small">Total Bookings</span>
              <span class="fs-3 fw-bold text-dark">{{ stats.total_bookings || 0 }}</span>
            </div>
          </div>
          <div class="col-6 col-md-4 col-xl-2">
            <div class="card border-0 shadow-sm p-3 text-center">
              <span class="text-muted small">Gross Revenue</span>
              <span class="fs-3 fw-bold text-success">₹{{ (stats.total_revenue || 0).toLocaleString('en-IN') }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Actions & Bookings Section -->
        <div class="row g-4">
          <!-- Card 1: Quick Actions -->
          <div class="col-12 col-lg-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h5 class="fw-bold mb-0">Quick Actions</h5>
              </div>
              <div class="card-body p-4 d-flex flex-column gap-3 justify-content-center">
                <button
                  @click="openCreateTrekModal"
                  class="btn btn-primary py-2 fw-semibold d-flex align-items-center justify-content-center shadow-sm"
                >
                  <i class="bi bi-plus-circle me-2 fs-5"></i> Add New Trek
                </button>
                <button
                  @click="openAddStaffModal"
                  class="btn btn-outline-primary py-2 fw-semibold d-flex align-items-center justify-content-center"
                >
                  <i class="bi bi-person-plus me-2 fs-5"></i> Add Staff Member
                </button>
                <button
                  @click="downloadMonthlyReport"
                  :disabled="reportDownloading"
                  class="btn btn-outline-dark py-2 fw-semibold d-flex align-items-center justify-content-center"
                >
                  <span v-if="reportDownloading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-file-earmark-pdf text-danger me-2 fs-5"></i>
                  {{ reportDownloading ? 'Generating PDF...' : 'Download Monthly Report' }}
                </button>
                <button
                  @click="activeTab = 'treks'"
                  class="btn btn-outline-secondary py-2 fw-semibold d-flex align-items-center justify-content-center"
                >
                  <i class="bi bi-compass me-2 fs-5"></i> Manage Treks Catalog
                </button>
                <button
                  @click="activeTab = 'users'"
                  class="btn btn-outline-secondary py-2 fw-semibold d-flex align-items-center justify-content-center"
                >
                  <i class="bi bi-people me-2 fs-5"></i> Moderate Users
                </button>
              </div>
            </div>
          </div>

          <!-- Card 2: Bookings -->
          <div class="col-12 col-lg-8">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
                <h5 class="fw-bold mb-0">Bookings</h5>
                <span class="badge bg-light text-dark border">{{ bookings.length }} Total</span>
              </div>
              <div class="card-body p-0">
                <div v-if="bookingsLoading" class="text-center py-5">
                  <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                  <span class="ms-2 small text-muted">Loading bookings...</span>
                </div>
                <div v-else-if="bookings.length === 0" class="text-center py-5 text-muted small">
                  <i class="bi bi-inbox text-muted display-6 d-block mb-2"></i>
                  No bookings found on the platform yet.
                </div>
                <div v-else class="table-responsive" style="max-height: 340px; overflow-y: auto;">
                  <table class="table table-hover align-middle mb-0 small">
                    <thead class="table-light sticky-top">
                      <tr>
                        <th class="ps-3">ID</th>
                        <th>Trekker</th>
                        <th>Trek</th>
                        <th>Slots</th>
                        <th>Status</th>
                        <th class="text-end pe-3">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="b in bookings" :key="b.id">
                        <td class="ps-3 fw-bold text-muted">#{{ b.id }}</td>
                        <td>
                          <span class="fw-semibold text-dark">{{ b.username }}</span>
                          <span class="d-block text-muted" style="font-size: 0.72rem;">{{ b.user_email }}</span>
                        </td>
                        <td>
                          <span class="fw-semibold text-dark">{{ b.trek_name }}</span>
                          <span class="d-block text-muted" style="font-size: 0.72rem;">{{ b.trek_location }}</span>
                        </td>
                        <td><span class="badge bg-light text-dark border">{{ b.num_slots }}</span></td>
                        <td>
                          <span
                            class="badge"
                            :class="{
                              'bg-success-subtle text-success border border-success-subtle': b.status === 'Booked',
                              'bg-danger-subtle text-danger border border-danger-subtle': b.status === 'Cancelled',
                              'bg-primary-subtle text-primary border border-primary-subtle': b.status === 'Completed'
                            }"
                          >
                            {{ b.status }}
                          </span>
                        </td>
                        <td class="text-end pe-3 text-muted">{{ formatDate(b.booking_date) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: TREK OPERATIONS -->
    <div v-else-if="activeTab === 'treks'">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
          <h5 class="fw-bold mb-0">Platform Treks Catalog</h5>
          <button @click="openCreateTrekModal" class="btn btn-primary btn-sm fw-semibold">
            <i class="bi bi-plus-lg me-1"></i> Add New Trek
          </button>
        </div>

        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small text-muted">
                <tr>
                  <th class="ps-3">ID</th>
                  <th>Name & Location</th>
                  <th>Difficulty</th>
                  <th>Slots</th>
                  <th>Price</th>
                  <th>Dates</th>
                  <th>Staff Assigned</th>
                  <th>Status</th>
                  <th class="text-end pe-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in allTreks" :key="t.id">
                  <td class="ps-3 fw-bold">#{{ t.id }}</td>
                  <td>
                    <span class="fw-semibold text-dark">{{ t.name }}</span>
                    <span class="d-block small text-muted">{{ t.location }}</span>
                  </td>
                  <td>
                    <span
                      class="badge"
                      :class="{
                        'bg-success': t.difficulty === 'Easy',
                        'bg-warning text-dark': t.difficulty === 'Moderate',
                        'bg-danger': t.difficulty === 'Hard'
                      }"
                    >
                      {{ t.difficulty }}
                    </span>
                  </td>
                  <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
                  <td>₹{{ t.price }}</td>
                  <td class="small text-muted">{{ formatDate(t.start_date) }} - {{ formatDate(t.end_date) }}</td>
                  <td>
                    <span v-if="t.assigned_staff_name" class="badge bg-light text-dark border">
                      <i class="bi bi-person me-1"></i>{{ t.assigned_staff_name }}
                    </span>
                    <span v-else class="text-muted small">Unassigned</span>
                  </td>
                  <td>
                    <select
                      v-model="t.status"
                      @change="updateTrekStatus(t)"
                      class="form-select form-select-sm"
                      style="width: 120px;"
                    >
                      <option value="Pending">Pending</option>
                      <option value="Approved">Approved</option>
                      <option value="Open">Open</option>
                      <option value="Closed">Closed</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </td>
                  <td class="text-end pe-3">
                    <button @click="openEditTrekModal(t)" class="btn btn-outline-secondary btn-sm py-0 me-1">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button @click="deleteTrek(t)" class="btn btn-outline-danger btn-sm py-0">
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: STAFF MANAGEMENT -->
    <div v-else-if="activeTab === 'staff'">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
          <h5 class="fw-bold mb-0">Staff Members</h5>
          <button @click="openAddStaffModal" class="btn btn-info text-white btn-sm fw-semibold">
            <i class="bi bi-person-plus me-1"></i> Onboard New Staff
          </button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small text-muted">
                <tr>
                  <th class="ps-3">ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Contact</th>
                  <th>Status</th>
                  <th>Registered At</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in staffUsers" :key="s.id">
                  <td class="ps-3 fw-bold">#{{ s.id }}</td>
                  <td class="fw-semibold">{{ s.username }}</td>
                  <td>{{ s.email }}</td>
                  <td>{{ s.contact_number || '-' }}</td>
                  <td>
                    <span :class="s.status === 'active' ? 'badge bg-success' : 'badge bg-danger'">
                      {{ s.status }}
                    </span>
                  </td>
                  <td class="small text-muted">{{ formatDate(s.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: USER MODERATION -->
    <div v-else-if="activeTab === 'users'">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
          <h5 class="fw-bold mb-0">User Directory & Moderation</h5>
          <div class="d-flex gap-2">
            <input
              v-model="userSearch"
              @input="fetchUsers"
              type="text"
              placeholder="Search user..."
              class="form-control form-control-sm"
              style="width: 200px;"
            />
          </div>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small text-muted">
                <tr>
                  <th class="ps-3">ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th class="text-end pe-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in allUsers" :key="u.id">
                  <td class="ps-3 fw-bold">#{{ u.id }}</td>
                  <td class="fw-semibold">{{ u.username }}</td>
                  <td>{{ u.email }}</td>
                  <td>
                    <span class="badge bg-secondary text-capitalize">{{ u.role }}</span>
                  </td>
                  <td>
                    <span :class="u.status === 'active' ? 'badge bg-success' : 'badge bg-danger'">
                      {{ u.status }}
                    </span>
                  </td>
                  <td class="text-end pe-3">
                    <button
                      v-if="u.role !== 'admin'"
                      @click="toggleUserStatus(u)"
                      class="btn btn-sm py-0"
                      :class="u.status === 'active' ? 'btn-outline-danger' : 'btn-outline-success'"
                    >
                      {{ u.status === 'active' ? 'Block User' : 'Activate User' }}
                    </button>
                    <span v-else class="text-muted small">Admin Protected</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE/EDIT TREK MODAL -->
    <div class="modal fade" id="trekModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-bottom">
            <h5 class="modal-title fw-bold">
              {{ editingTrekId ? 'Edit Trek Expedition' : 'Create New Trek' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveTrek">
            <div class="modal-body p-4">
              <div class="row g-3">
                <div class="col-md-8">
                  <label class="form-label small fw-semibold">Trek Title</label>
                  <input v-model="trekForm.name" type="text" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold">Difficulty</label>
                  <select v-model="trekForm.difficulty" class="form-select">
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Location</label>
                  <input v-model="trekForm.location" type="text" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Assign Staff Member</label>
                  <select v-model="trekForm.assigned_staff_id" class="form-select">
                    <option :value="null">None (Unassigned)</option>
                    <option v-for="s in staffUsers" :key="s.id" :value="s.id">
                      {{ s.username }} ({{ s.email }})
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Start Date</label>
                  <input v-model="trekForm.start_date" type="date" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">End Date</label>
                  <input v-model="trekForm.end_date" type="date" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Total Capacity Slots</label>
                  <input v-model.number="trekForm.total_slots" type="number" min="1" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Price per slot (INR)</label>
                  <input v-model.number="trekForm.price" type="number" min="0" step="100" class="form-control" required />
                </div>
                <div class="col-12">
                  <label class="form-label small fw-semibold">Detailed Description</label>
                  <textarea v-model="trekForm.description" rows="3" class="form-control" required></textarea>
                </div>
              </div>
            </div>
            <div class="modal-footer border-top">
              <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm fw-semibold">Save Trek</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- ONBOARD STAFF MODAL -->
    <div class="modal fade" id="staffModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-bottom">
            <h5 class="modal-title fw-bold">Onboard Staff Member</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveStaff">
            <div class="modal-body p-4">
              <div class="mb-3">
                <label class="form-label small fw-semibold">Username</label>
                <input v-model="staffForm.username" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Email Address</label>
                <input v-model="staffForm.email" type="email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Temporary Password</label>
                <input v-model="staffForm.password" type="password" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Contact Number (Optional)</label>
                <input v-model="staffForm.contact_number" type="tel" class="form-control" />
              </div>
            </div>
            <div class="modal-footer border-top">
              <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-info text-white btn-sm fw-semibold">Create Staff Account</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'

const activeTab = ref('overview')
const stats = ref({})
const statsLoading = ref(true)
const bookings = ref([])
const bookingsLoading = ref(false)
const allTreks = ref([])
const staffUsers = ref([])
const allUsers = ref([])
const userSearch = ref('')
const alert = reactive({ type: '', message: '' })
const reportDownloading = ref(false)

// Trek Form State
const editingTrekId = ref(null)
const trekForm = reactive({
  name: '',
  description: '',
  location: '',
  difficulty: 'Moderate',
  start_date: '',
  end_date: '',
  total_slots: 20,
  price: 5000,
  assigned_staff_id: null
})

// Staff Form State
const staffForm = reactive({
  username: '',
  email: '',
  password: '',
  contact_number: ''
})

const fetchStats = async () => {
  statsLoading.value = true
  try {
    const res = await api.get('/admin/dashboard-stats')
    const d = res.data.data
    stats.value = {
      total_trekkers: d.users?.total_trekkers || 0,
      total_staff: d.users?.total_staff || 0,
      total_treks: d.treks?.total || 0,
      open_treks: d.treks?.open || 0,
      pending_treks: d.treks?.pending || 0,
      completed_treks: d.treks?.completed || 0,
      closed_treks: d.treks?.closed || 0,
      total_bookings: d.bookings?.total || 0,
      active_bookings: d.bookings?.booked || 0,
      total_revenue: d.financials?.total_revenue || 0
    }
  } catch (err) {
    showAlert('danger', 'Failed to load dashboard metrics.')
  } finally {
    statsLoading.value = false
  }
}

const fetchBookings = async () => {
  bookingsLoading.value = true
  try {
    const res = await api.get('/bookings')
    bookings.value = res.data.data || []
  } catch (err) {
    showAlert('danger', 'Failed to load bookings.')
  } finally {
    bookingsLoading.value = false
  }
}

const downloadMonthlyReport = async () => {
  reportDownloading.value = true
  try {
    const res = await api.get('/admin/reports/monthly', { responseType: 'blob' })
    const now = new Date()
    const filename = `monthly_report_${now.getFullYear()}_${String(now.getMonth() + 1).padStart(2, '0')}.pdf`
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showAlert('success', 'Monthly platform report downloaded successfully.')
  } catch (err) {
    showAlert('danger', 'Failed to generate monthly report.')
  } finally {
    reportDownloading.value = false
  }
}

const fetchTreks = async () => {
  try {
    const res = await api.get('/treks')
    allTreks.value = res.data.data
  } catch (err) {
    // handled
  }
}

const fetchStaff = async () => {
  try {
    const res = await api.get('/admin/users', { params: { role: 'staff' } })
    staffUsers.value = res.data.data
  } catch (err) {
    // handled
  }
}

const fetchUsers = async () => {
  try {
    const params = {}
    if (userSearch.value.trim()) params.search = userSearch.value.trim()
    const res = await api.get('/admin/users', { params })
    allUsers.value = res.data.data
  } catch (err) {
    // handled
  }
}

const refreshAll = () => {
  fetchStats()
  fetchBookings()
  fetchTreks()
  fetchStaff()
  fetchUsers()
}

// Trek Operations
const openCreateTrekModal = () => {
  editingTrekId.value = null
  Object.assign(trekForm, {
    name: '',
    description: '',
    location: '',
    difficulty: 'Moderate',
    start_date: '',
    end_date: '',
    total_slots: 20,
    price: 5000,
    assigned_staff_id: null
  })
  showModal('trekModal')
}

const openEditTrekModal = (t) => {
  editingTrekId.value = t.id
  Object.assign(trekForm, {
    name: t.name,
    description: t.description,
    location: t.location,
    difficulty: t.difficulty,
    start_date: t.start_date,
    end_date: t.end_date,
    total_slots: t.total_slots,
    price: t.price,
    assigned_staff_id: t.assigned_staff_id
  })
  showModal('trekModal')
}

const saveTrek = async () => {
  try {
    if (editingTrekId.value) {
      await api.put(`/treks/${editingTrekId.value}`, trekForm)
      showAlert('success', 'Trek updated successfully.')
    } else {
      await api.post('/treks', trekForm)
      showAlert('success', 'Trek created successfully.')
    }
    hideModal('trekModal')
    refreshAll()
  } catch (err) {
    showAlert('danger', err.response?.data?.message || 'Failed to save trek.')
  }
}

const updateTrekStatus = async (trek) => {
  try {
    await api.patch(`/treks/${trek.id}/status`, { status: trek.status })
    showAlert('success', `Trek #${trek.id} status updated to "${trek.status}"`)
    refreshAll()
  } catch (err) {
    showAlert('danger', err.response?.data?.message || 'Status change failed.')
    fetchTreks()
  }
}

const deleteTrek = async (trek) => {
  if (!confirm(`Are you sure you want to permanently delete "${trek.name}"?`)) return
  try {
    await api.delete(`/treks/${trek.id}`)
    showAlert('success', `Trek #${trek.id} deleted.`)
    refreshAll()
  } catch (err) {
    showAlert('danger', err.response?.data?.message || 'Cannot delete trek with active bookings.')
  }
}

// Staff Onboarding
const openAddStaffModal = () => {
  Object.assign(staffForm, { username: '', email: '', password: '', contact_number: '' })
  showModal('staffModal')
}

const saveStaff = async () => {
  try {
    await api.post('/admin/staff', staffForm)
    showAlert('success', `Staff account for "${staffForm.username}" created successfully.`)
    hideModal('staffModal')
    refreshAll()
  } catch (err) {
    showAlert('danger', err.response?.data?.message || 'Failed to onboard staff.')
  }
}

// User Moderation
const toggleUserStatus = async (user) => {
  const newStatus = user.status === 'active' ? 'blocked' : 'active'
  try {
    await api.patch(`/admin/users/${user.id}/status`, { status: newStatus })
    showAlert('success', `User "${user.username}" is now ${newStatus}.`)
    fetchUsers()
  } catch (err) {
    showAlert('danger', err.response?.data?.message || 'Failed to toggle status.')
  }
}

const showModal = (id) => {
  const el = document.getElementById(id)
  if (window.bootstrap) {
    const modal = window.bootstrap.Modal.getOrCreateInstance(el)
    modal.show()
  }
}

const hideModal = (id) => {
  const el = document.getElementById(id)
  if (window.bootstrap) {
    const modal = window.bootstrap.Modal.getInstance(el)
    if (modal) modal.hide()
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
  refreshAll()
})
</script>
