<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary px-4">
    <div class="container-fluid">
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#userNavbarNav"
        aria-controls="userNavbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="userNavbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link text-white" to="/user/dashboard">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link text-white" to="/user/scores">Scores</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link text-white" to="/user/summary">Summary</router-link>
          </li>
        </ul>
        <span class="navbar-text me-4 text-white" style="font-size: 1.5rem;">
          Welcome, {{ userName }}!
        </span>
        <form class="d-flex me-2" @submit.prevent="onSearch">
          <input
            v-model="searchQuery"
            class="form-control me-2"
            type="search"
            placeholder="Search Quiz or Subject"
            aria-label="Search"
          />
          <button class="btn btn-outline-light" type="submit">Search</button>
        </form>
        <button class="btn btn-danger" @click="logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  userName: {
    type: String,
    default: 'User'
  }
})

const emit = defineEmits(['logout', 'search'])

const searchQuery = ref('')

function logout() {
  emit('logout')
}

function onSearch() {
  emit('search', searchQuery.value)
}
</script>