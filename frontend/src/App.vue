<template>
  <div class="d-flex flex-column min-vh-100">
    <Navbar />
    <main class="flex-grow-1 py-4">
      <router-view />
    </main>
    <footer class="bg-white border-top text-muted text-center py-3 mt-auto">
      <div class="container small">
        <span class="fw-semibold text-dark">Trekking Management Application</span> &bull; IIT Madras BS Degree MAD-2
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>
