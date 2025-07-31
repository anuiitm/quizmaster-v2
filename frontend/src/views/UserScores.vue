<template>
  <UserNavbar :userName="userName" @logout="handleLogout" @search="handleSearch" />
  <div class="container-fluid px-5 content-container">
    <h2 class="mb-4 text-center">My Quiz Scores</h2>
    
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger text-center">
      {{ error }}
    </div>
    
    <div v-else>
      <div v-if="scores.length === 0" class="text-center text-muted py-5">
        <h5>No quiz scores yet</h5>
        <p>Take some quizzes to see your scores here!</p>
        <router-link to="/user/dashboard" class="btn btn-primary">
          Go to Dashboard
        </router-link>
      </div>
      
      <div v-else>
        <div class="table-responsive">
          <table class="table table-striped table-hover">
            <thead class="table-dark">
              <tr>
                <th>Quiz ID</th>
                <th>Subject</th>
                <th>Chapter</th>
                <th>Score</th>
                <th>Date Taken</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="score in scores" :key="score.id">
                <td>{{ score.quiz_id }}</td>
                <td>{{ score.subject_name }}</td>
                <td>{{ score.chapter_name }}</td>
                <td>
                  <span class="badge" :class="getScoreBadgeClass(score.score)">
                    {{ score.score }}%
                  </span>
                </td>
                <td>{{ formatDate(score.date_taken) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="text-center mt-4">
          <router-link to="/user/dashboard" class="btn btn-primary btn-lg">
            ← Back to Dashboard
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/axios'
import UserNavbar from '@/components/UserNavbar.vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const scores = ref([])
const userName = ref('User')

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

function getScoreBadgeClass(score) {
  if (score >= 90) return 'bg-success'
  if (score >= 80) return 'bg-info'
  if (score >= 70) return 'bg-warning'
  return 'bg-danger'
}

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

onMounted(async () => {
  try {
    const { data } = await apiClient.get('/api/user/scores')
    scores.value = data.scores || []
  } catch (err) {
    error.value = 'Failed to load scores.'
    console.error('Scores error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.content-container {
  padding-top: 2rem;
}

.table th {
  font-weight: 600;
}

.badge {
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
}
</style>