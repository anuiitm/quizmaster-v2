<template>
  <UserNavbar :userName="userName" @logout="handleLogout" @search="handleSearch" />
  <div class="container-fluid px-5 content-container">
    <div v-if="loading" class="text-center mt-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading quiz...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger text-center mt-5">
      {{ error }}
    </div>
    
    <div v-else-if="quiz" class="quiz-container">
      <div class="card shadow-sm">
        <div class="card-header bg-primary text-white">
          <h3 class="mb-0">Quiz #{{ quiz.id }}</h3>
          <p class="mb-0">{{ quiz.chapter?.subject?.name }} - {{ quiz.chapter?.name }}</p>
        </div>
        
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span>Question {{ currentQuestionIndex + 1 }} of {{ quiz.questions.length }}</span>
            <span class="badge bg-info">{{ timeLeft }}</span>
          </div>
          
          <div v-if="currentQuestion" class="question-container">
            <h4 class="mb-3">{{ currentQuestion.question_statement }}</h4>
            
            <div class="options-container">
              <div 
                v-for="(option, index) in options" 
                :key="index"
                class="option-item"
                :class="{ 'selected': selectedAnswer === index + 1 }"
                @click="selectAnswer(index + 1)"
              >
                <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                <span class="option-text">{{ option }}</span>
              </div>
            </div>
            
            <div class="mt-4 d-flex justify-content-between">
              <button 
                class="btn btn-secondary" 
                @click="previousQuestion"
                :disabled="currentQuestionIndex === 0"
              >
                ← Previous
              </button>
              
              <button 
                v-if="currentQuestionIndex < quiz.questions.length - 1"
                class="btn btn-primary" 
                @click="nextQuestion"
              >
                Next →
              </button>
              
              <button 
                v-else
                class="btn btn-success" 
                @click="submitQuiz"
                :disabled="submitting"
              >
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                Submit Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="mt-4 text-center">
      <router-link to="/user/dashboard" class="btn btn-outline-secondary">
        ← Back to Dashboard
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiClient from '@/api/axios'
import UserNavbar from '@/components/UserNavbar.vue'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref('')
const quiz = ref(null)
const currentQuestionIndex = ref(0)
const selectedAnswer = ref(null)
const answers = ref({})
const submitting = ref(false)
const timeLeft = ref('00:00')
const timer = ref(null)
const userName = ref('User')

const currentQuestion = computed(() => {
  return quiz.value?.questions[currentQuestionIndex.value] || null
})

const options = computed(() => {
  if (!currentQuestion.value) return []
  return [
    currentQuestion.value.option1,
    currentQuestion.value.option2,
    currentQuestion.value.option3,
    currentQuestion.value.option4
  ].filter(option => option)
})

function selectAnswer(answer) {
  selectedAnswer.value = answer
  answers.value[currentQuestionIndex.value] = answer
}

function nextQuestion() {
  if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
    currentQuestionIndex.value++
    selectedAnswer.value = answers.value[currentQuestionIndex.value] || null
  }
}

function previousQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    selectedAnswer.value = answers.value[currentQuestionIndex.value] || null
  }
}

function calculateScore() {
  let correct = 0
  let total = quiz.value.questions.length
  
  quiz.value.questions.forEach((question, index) => {
    if (answers.value[index] === question.correct_option) {
      correct++
    }
  })
  
  return Math.round((correct / total) * 100)
}

async function submitQuiz() {
  submitting.value = true
  
  try {
    const score = calculateScore()
    await apiClient.post(`/api/user/quiz/${quiz.value.id}/submit`, { score })
    
    // Redirect to scores page
    router.push('/user/scores')
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to submit quiz.'
    submitting.value = false
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

function startTimer() {
  const duration = quiz.value.time_duration || '00:30'
  
  // Parse HH:MM format from backend
  const [hours, minutes] = duration.split(':').map(Number)
  let totalSeconds = (hours * 60 + minutes) * 60 // Convert to seconds
  
  timer.value = setInterval(() => {
    totalSeconds--
    const mins = Math.floor(totalSeconds / 60)
    const secs = totalSeconds % 60
    timeLeft.value = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    
    if (totalSeconds <= 0) {
      clearInterval(timer.value)
      submitQuiz()
    }
  }, 1000)
}

onMounted(async () => {
  try {
    const quizId = route.params.quizId
    const { data } = await apiClient.get(`/api/user/quiz/${quizId}`)
    quiz.value = data.quiz
    startTimer()
  } catch (err) {
    error.value = 'Failed to load quiz.'
    console.error('Error fetching quiz:', err)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped>
.quiz-container {
  max-width: 800px;
  margin: auto;
}

.question-container {
  min-height: 400px;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.option-item.selected {
  border-color: #007bff;
  background-color: #e3f2fd;
}

.option-label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 30px;
}

.option-text {
  flex: 1;
}
</style> 