<template>
  <div>
    <!-- Hero Section -->
    <div class="bg-dark text-white py-5 mb-4 shadow-sm">
      <div class="container text-center py-4">
        <h1 class="display-5 fw-bold mb-3">
          Explore The Wild Trails <i class="bi bi-compass text-warning"></i>
        </h1>
        <p class="lead text-light opacity-75 col-lg-8 mx-auto mb-4">
          Book unforgettable trekking experiences across the Himalayas, Western Ghats, and beyond. Verified guides, transparent booking, and real-time slot inventory.
        </p>
      </div>
    </div>

    <!-- Main Container -->
    <div class="container">
      <!-- Search & Filters Toolbar -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-3 p-md-4">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label small fw-semibold">Search Trek or Location</label>
              <div class="input-group">
                <span class="input-group-text bg-light"><i class="bi bi-search"></i></span>
                <input
                  v-model="filters.search"
                  @input="debouncedFetch"
                  type="text"
                  class="form-control"
                  placeholder="e.g. Kedarkantha or Uttarakhand"
                />
              </div>
            </div>

            <div class="col-md-3">
              <label class="form-label small fw-semibold">Difficulty Level</label>
              <select v-model="filters.difficulty" @change="fetchTreks" class="form-select">
                <option value="">All Difficulties</option>
                <option value="Easy">Easy</option>
                <option value="Moderate">Moderate</option>
                <option value="Hard">Hard</option>
              </select>
            </div>

            <div class="col-md-3">
              <label class="form-label small fw-semibold">Max Price (₹)</label>
              <input
                v-model.number="filters.max_price"
                @input="debouncedFetch"
                type="number"
                min="0"
                step="500"
                class="form-control"
                placeholder="Max budget in INR"
              />
            </div>

            <div class="col-md-2 d-flex align-items-end">
              <button @click="resetFilters" class="btn btn-outline-secondary w-100">
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

      <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 mb-5">
        <div v-for="trek in treks" :key="trek.id" class="col">
          <div class="card h-100 border-0 shadow-sm d-flex flex-column">
            <div class="card-body p-4 d-flex flex-column">
              <div class="d-flex justify-content-between align-items-start mb-2">
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
                <span v-if="trek.available_slots === 0" class="badge bg-danger">Sold Out</span>
                <span v-else class="badge bg-success-subtle text-success border border-success-subtle">
                  {{ trek.available_slots }} / {{ trek.total_slots }} slots left
                </span>
              </div>

              <h5 class="card-title fw-bold text-dark mb-1">{{ trek.name }}</h5>
              <p class="text-muted small mb-3">
                <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ trek.location }}
              </p>

              <p class="card-text text-secondary small flex-grow-1">
                {{ truncate(trek.description, 110) }}
              </p>

              <hr class="my-3 opacity-25" />

              <div class="d-flex justify-content-between align-items-center mb-3 small text-muted">
                <div>
                  <i class="bi bi-calendar-event me-1"></i>
                  <span>{{ formatDate(trek.start_date) }}</span>
                </div>
                <div>
                  <i class="bi bi-arrow-right me-1"></i>
                  <span>{{ formatDate(trek.end_date) }}</span>
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center mt-auto">
                <div>
                  <span class="fs-4 fw-bold text-primary">₹{{ trek.price.toLocaleString('en-IN') }}</span>
                  <span class="text-muted small"> / person</span>
                </div>
                <router-link
                  :to="`/treks/${trek.id}`"
                  class="btn btn-outline-primary btn-sm fw-semibold"
                >
                  Details & Book <i class="bi bi-arrow-right-short"></i>
                </router-link>
              </div>
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
