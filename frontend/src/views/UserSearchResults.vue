<template>
  <UserNavbar :userName="userName" @logout="handleLogout" @search="handleSearch" />
  <div class="container-fluid px-5 content-container">
    <h2 class="mb-4 text-center">Search Results</h2>
    
    <div class="card shadow-sm p-3 mb-5 bg-white rounded search-results-card">
      <div class="card-body">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Searching...</span>
          </div>
        </div>
        
        <div v-else-if="error" class="alert alert-danger text-center">
          {{ error }}
        </div>
        
        <div v-else>
          <div class="mb-3">
            <h5>Search Query: "{{ searchQuery }}"</h5>
            <p class="text-muted">{{ results.length }} results found</p>
          </div>
          
          <div v-if="results.length === 0" class="text-center text-muted">
            <p>No results found for your search query.</p>
            <p>Try different keywords or check your spelling.</p>
          </div>
          
          <div v-else class="row">
            <!-- Quiz Results -->
            <div v-for="result in results" :key="result.id" class="col-md-4 mb-3">
              <div class="card shadow-sm h-100">
                <div class="card-body">
                  <h5 class="card-title">Quiz ID: {{ result.id }}</h5>
                  <p class="card-text"><strong>Chapter:</strong> {{ result.chapter?.name || 'N/A' }}</p>
                  <p class="card-text"><strong>Subject:</strong> {{ result.chapter?.subject?.name || 'N/A' }}</p>
                  <p class="card-text"><strong>Date:</strong> {{ formatDate(result.date_of_quiz) }}</p>
                  <p class="card-text">
                    <strong>Marks Achieved:</strong> 
                    <span v-if="quizResults[result.id] !== undefined" class="text-primary fw-bold">
                      {{ quizResults[result.id] }}%
                    </span>
                    <span v-else class="text-muted">Not Attempted</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="mt-4 text-center">
      <router-link to="/user/dashboard" class="btn btn-danger btn-lg">
        ← Back to Dashboard
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiClient from '@/api/axios'
import UserNavbar from '@/components/UserNavbar.vue'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref('')
const results = ref([])
const searchQuery = ref('')
const userName = ref('User')
const quizResults = ref({})

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch (error) {
    return dateString
  }
}

function handleLogout() {
  apiClient.post('/api/auth/logout').finally(() => {
    localStorage.removeItem('is_admin')
    localStorage.removeItem('is_logged_in')
    router.push('/login')
  })
}

function handleSearch(query) {
  if (query && query.trim()) {
    router.push({ name: 'UserSearchResults', query: { q: query } })
  }
}

onMounted(async () => {
  try {
    searchQuery.value = route.query.q || ''
    
    if (!searchQuery.value) {
      results.value = []
      return
    }
    
    const { data } = await apiClient.get('/api/user/search', {
      params: { q: searchQuery.value }
    })
    
    results.value = data.results || []
    quizResults.value = data.quiz_results || {}
  } catch (err) {
    error.value = 'Failed to perform search.'
    console.error('Search error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.search-results-card {
  max-width: 1200px;
  margin: auto;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style> 