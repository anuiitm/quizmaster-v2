<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="logout" />
  <div class="container-fluid px-5 content-container">
    <h2 class="mb-4 text-center">Summary</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger text-center">
      {{ error }}
    </div>

    <div v-else>
      <!-- Summary Statistics -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title text-primary">{{ summaryStats.totalUsers }}</h5>
              <p class="card-text">Total Users</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title text-success">{{ summaryStats.totalQuizzes }}</h5>
              <p class="card-text">Total Quizzes</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title text-info">{{ summaryStats.totalSubjects }}</h5>
              <p class="card-text">Total Subjects</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title text-warning">{{ summaryStats.totalAttempts }}</h5>
              <p class="card-text">Total Attempts</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Subject Performance Table -->
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Subject-Wise Performance</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Highest Score</th>
                      <th>Lowest Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(subject, index) in barChartData.subjects" :key="index">
                      <td>{{ subject }}</td>
                      <td>
                        <span class="badge bg-success">{{ barChartData.max_scores[index] }}%</span>
                      </td>
                      <td>
                        <span class="badge bg-danger">{{ barChartData.min_scores[index] }}%</span>
                      </td>
                    </tr>
                    <tr v-if="barChartData.subjects.length === 0">
                      <td colspan="3" class="text-center text-muted">No data available</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Subject Attempts Table -->
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Subject-Wise Attempts</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Total Attempts</th>
                      <th>Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(subject, index) in pieChartData.subjects" :key="index">
                      <td>{{ subject }}</td>
                      <td>
                        <span class="badge bg-info">{{ pieChartData.attempts[index] }}</span>
                      </td>
                      <td>
                        <div class="progress" style="height: 20px;">
                          <div 
                            class="progress-bar" 
                            :style="{ width: getPercentage(pieChartData.attempts[index]) + '%' }"
                            :class="getProgressBarClass(index)"
                          >
                            {{ getPercentage(pieChartData.attempts[index]) }}%
                          </div>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="pieChartData.subjects.length === 0">
                      <td colspan="3" class="text-center text-muted">No data available</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="text-center mt-4">
      <router-link to="/admin" class="btn btn-danger">
        ← Back to Admin Dashboard
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/axios'
import AdminNavbar from '@/components/AdminNavbar.vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const searchCategory = ref('subjects')
const searchQuery = ref('')

// Summary statistics
const summaryStats = ref({
  totalUsers: 0,
  totalQuizzes: 0,
  totalSubjects: 0,
  totalAttempts: 0
})

// Chart data (now used for tables)
const barChartData = ref({
  subjects: [],
  max_scores: [],
  min_scores: []
})

const pieChartData = ref({
  subjects: [],
  attempts: []
})

function logout() {
  apiClient.post('/api/auth/logout').finally(() => {
    localStorage.removeItem('is_admin')
    localStorage.removeItem('is_logged_in')
    router.push('/login')
  })
}

function getPercentage(attempts) {
  const total = pieChartData.value.attempts.reduce((sum, val) => sum + val, 0)
  if (total === 0) return 0
  return Math.round((attempts / total) * 100)
}

function getProgressBarClass(index) {
  const classes = ['bg-primary', 'bg-success', 'bg-info', 'bg-warning', 'bg-danger', 'bg-secondary']
  return classes[index % classes.length]
}

async function fetchSummaryData() {
  try {
    loading.value = true
    error.value = ''
    
    const response = await apiClient.get('/api/admin/summary')
    const data = response.data
    
    // Update summary statistics
    summaryStats.value = data.summary_stats
    
    // Update chart data (now used for tables)
    barChartData.value = data.bar_chart_data
    pieChartData.value = data.pie_chart_data
    
  } catch (err) {
    error.value = 'Failed to load summary data.'
    console.error('Summary error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSummaryData()
})
</script>

<style scoped>
.content-container {
  padding-top: 2rem;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: box-shadow 0.15s ease-in-out;
  margin-bottom: 1rem;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-weight: 600;
}

.table {
  margin-bottom: 0;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.875em;
}

.progress {
  background-color: #e9ecef;
  border-radius: 0.375rem;
}

.progress-bar {
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.2;
}
</style> 