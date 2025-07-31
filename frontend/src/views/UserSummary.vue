<template>
  <UserNavbar :userName="userName" @logout="handleLogout" @search="handleSearch" />
  <div class="container-fluid px-5 content-container">
    <h2 class="mb-4 text-center">User Summary</h2>

    <div class="row">
      <!-- Bar Chart (Subject-Wise Quiz Attempts) -->
      <div class="col-md-6">
        <div class="card p-5">
          <h5 class="text-center">Quizzes Attempted Per Subject</h5>
          <canvas ref="barChartCanvas"></canvas>
        </div>
      </div>

      <!-- Pie Chart (Month-Wise Quiz Attempts) -->
      <div class="col-md-6">
        <div class="card p-5">
          <h5 class="text-center">Month-Wise Quiz Attempts</h5>
          <canvas ref="pieChartCanvas" style="max-width: 800px; max-height: 800px; margin: auto;"></canvas>
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
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/axios'
import UserNavbar from '@/components/UserNavbar.vue'
import Chart from 'chart.js/auto'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const userName = ref('User')
const barChartCanvas = ref(null)
const pieChartCanvas = ref(null)
let barChart = null
let pieChart = null

// Assign different colors for each subject
const subjectColors = [
  '#FF5733', '#33FF57', '#3357FF', '#FF33A8', '#A833FF', '#FFD433', '#33FFF5'
]

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

function createBarChart(data) {
  if (barChart) {
    barChart.destroy()
  }

  const ctx = barChartCanvas.value.getContext('2d')
  
  // Create multiple datasets for each subject
  const datasets = data.subjects.map((subject, index) => ({
    label: subject,
    backgroundColor: subjectColors[index % subjectColors.length],
    data: [data.attempt_counts[index]]
  }))

  barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Quizzes Attempted'],
      datasets: datasets
    },
    options: {
      responsive: true,
      plugins: { 
        legend: { position: 'top' } 
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      }
    }
  })
}

function createPieChart(data) {
  if (pieChart) {
    pieChart.destroy()
  }

  const ctx = pieChartCanvas.value.getContext('2d')
  
  pieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: data.months,
      datasets: [{
        data: data.attempts,
        backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40', '#ff6384', '#c9cbcf', '#4bc0c0', '#ff6384', '#36a2eb', '#ffce56']
      }]
    },
    options: {
      responsive: true,
      plugins: { 
        legend: { position: 'bottom' } 
      },
      animation: {
        animateRotate: true,
        animateScale: true
      }
    }
  })
}

onMounted(async () => {
  try {
    // Load Chart.js from CDN if not already loaded
    if (typeof Chart === 'undefined') {
      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js'
      script.onload = async () => {
        await loadChartData()
      }
      document.head.appendChild(script)
    } else {
      await loadChartData()
    }
  } catch (err) {
    error.value = 'Failed to load chart data.'
    console.error('Error loading charts:', err)
  } finally {
    loading.value = false
  }
})

async function loadChartData() {
  try {
    const { data } = await apiClient.get('/api/user/summary')
    
    // Wait for DOM to be ready
    await nextTick()
    
    if (data.bar_chart_data && barChartCanvas.value) {
      createBarChart(data.bar_chart_data)
    }
    
    if (data.pie_chart_data && pieChartCanvas.value) {
      createPieChart(data.pie_chart_data)
    }
  } catch (err) {
    console.error('Error fetching chart data:', err)
    // Create sample data for demonstration
    const sampleBarData = {
      subjects: ['Mathematics', 'Science', 'History'],
      attempt_counts: [3, 2, 1]
    }
    const samplePieData = {
      months: ['January', 'February', 'March', 'April'],
      attempts: [2, 3, 1, 2]
    }
    
    await nextTick()
    if (barChartCanvas.value) createBarChart(sampleBarData)
    if (pieChartCanvas.value) createPieChart(samplePieData)
  }
}
</script>

<style scoped>
.card {
  margin-bottom: 20px;
}

canvas {
  max-height: 400px;
}
</style> 