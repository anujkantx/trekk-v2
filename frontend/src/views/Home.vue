<template>
  <div class="container">
    <!-- Compact Search & Filters Toolbar -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-2 p-md-3">
        <div class="row g-2 align-items-center">
          <div class="col-12 col-md-4">
            <div class="input-group input-group-sm">
              <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
              <input
                v-model="filters.search"
                @input="debouncedFetch"
                type="text"
                class="form-control"
                placeholder="Search trek or location..."
              />
            </div>
          </div>

          <div class="col-6 col-md-3">
            <select v-model="filters.difficulty" @change="fetchTreks" class="form-select form-select-sm">
              <option value="">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Moderate">Moderate</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <div class="col-6 col-md-3">
            <div class="input-group input-group-sm">
              <span class="input-group-text bg-white text-muted">₹</span>
              <input
                v-model.number="filters.max_price"
                @input="debouncedFetch"
                type="number"
                min="0"
                step="500"
                class="form-control"
                placeholder="Max budget (₹)"
              />
            </div>
          </div>

          <div class="col-12 col-md-2">
            <button @click="resetFilters" class="btn btn-outline-secondary btn-sm w-100">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>

      <!-- Treks Grid -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading treks...</span>
        </div>
        <p class="text-muted mt-2 small">Fetching available expeditions...</p>
      </div>

      <div v-else-if="errorMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ errorMessage }}
      </div>

      <div v-else-if="treks.length === 0" class="card border-0 shadow-sm text-center py-5">
        <div class="card-body">
          <i class="bi bi-emoji-neutral text-muted display-4"></i>
          <h4 class="mt-3 fw-bold">No Treks Found</h4>
          <p class="text-muted small">Try adjusting your search terms or filters to find open trails.</p>
          <button @click="resetFilters" class="btn btn-primary btn-sm mt-2">Clear Filters</button>
        </div>
      </div>

      <div v-else class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-3 mb-5">
        <div v-for="trek in treks" :key="trek.id" class="col">
          <div
            class="card trek-card h-100 border-0 shadow-sm d-flex flex-column"
            :class="{
              'trek-card-easy': trek.difficulty === 'Easy',
              'trek-card-moderate': trek.difficulty === 'Moderate',
              'trek-card-hard': trek.difficulty === 'Hard'
            }"
          >
            <div class="card-body p-3 d-flex flex-column">
              <!-- Top Badges Row -->
              <div class="d-flex justify-content-between align-items-center mb-3 gap-1 flex-wrap">
                <span
                  class="badge text-white px-2 py-1"
                  :class="{
                    'badge-easy': trek.difficulty === 'Easy',
                    'badge-moderate': trek.difficulty === 'Moderate',
                    'badge-hard': trek.difficulty === 'Hard'
                  }"
                >
                  {{ trek.difficulty }}
                </span>

                <span v-if="trek.available_slots === 0" class="badge bg-danger-subtle text-danger border border-danger-subtle">
                  Sold Out
                </span>
                <span v-else-if="trek.available_slots <= 5" class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle">
                  Only {{ trek.available_slots }} left
                </span>
                <span v-else class="badge bg-success-subtle text-success border border-success-subtle">
                  {{ trek.available_slots }} slots
                </span>
              </div>

              <!-- Title & Location -->
              <h6 class="card-title fw-bold text-dark mb-1 lh-sm fs-6">{{ trek.name }}</h6>
              <p class="text-muted small mb-3">
                <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ trek.location }}
              </p>

              <!-- Schedule Box -->
              <div class="bg-light p-2 rounded-2 mb-3 small text-muted d-flex justify-content-between align-items-center">
                <div>
                  <i class="bi bi-calendar3 text-primary me-1"></i>
                  <span>{{ formatDate(trek.start_date) }}</span>
                </div>
                <i class="bi bi-arrow-right text-muted opacity-50"></i>
                <div>
                  <i class="bi bi-flag-fill text-secondary me-1"></i>
                  <span>{{ formatDate(trek.end_date) }}</span>
                </div>
              </div>

              <hr class="my-2 opacity-25 mt-auto" />

              <!-- Price & CTA -->
              <div class="d-flex justify-content-between align-items-center pt-1">
                <div>
                  <span class="fs-5 fw-bold text-primary">₹{{ trek.price.toLocaleString('en-IN') }}</span>
                  <span class="text-muted small d-block" style="font-size: 0.72rem; margin-top: -3px;">per trekker</span>
                </div>
                <router-link
                  :to="`/treks/${trek.id}`"
                  class="btn btn-primary btn-sm px-3 fw-semibold shadow-sm"
                >
                  <span>Book</span>
                  <i class="bi bi-arrow-right-short ms-1"></i>
                </router-link>
              </div>
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
const errorMessage = ref('')

const filters = reactive({
  search: '',
  difficulty: '',
  max_price: null
})

let debounceTimer = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchTreks()
  }, 300)
}

const fetchTreks = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const params = {}
    if (filters.search.trim()) params.search = filters.search.trim()
    if (filters.difficulty) params.difficulty = filters.difficulty
    if (filters.max_price !== null && filters.max_price !== '') params.max_price = filters.max_price

    const res = await api.get('/treks', { params })
    treks.value = res.data.data
  } catch (err) {
    errorMessage.value = 'Failed to load treks. Please ensure the backend is running.'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.difficulty = ''
  filters.max_price = null
  fetchTreks()
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const truncate = (text, len) => {
  if (!text) return ''
  return text.length > len ? text.substring(0, len) + '...' : text
}

onMounted(() => {
  fetchTreks()
})
</script>
