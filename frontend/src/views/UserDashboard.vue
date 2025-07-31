<template>
  <UserNavbar :userName="userName" @logout="handleLogout" @search="handleSearch" />
  <div class="container-fluid px-5 content-container">
    <h2 class="mb-4 text-center">Quizzes</h2>
    <div class="card shadow-sm p-3 mb-5 bg-white rounded user-dashboard-card">
      <div class="card-body">
        <template v-if="allQuizzes.length">
          <table class="table table-hover text-center">
            <thead>
              <tr>
                <th>Quiz ID</th>
                <th>No. of Questions</th>
                <th>Quiz Date</th>
                <th>Duration</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in allQuizzes" :key="quiz.id">
                <td>{{ quiz.id }}</td>
                <td>{{ quiz.questions.length }}</td>
                <td>{{ formatDate(quiz.date_of_quiz) }}</td>
                <td>{{ quiz.time_duration }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-info me-1"
                    @click="openModal(quiz)"
                  >
                    View Quiz
                  </button>
                  <button
                    v-if="takenQuizIds.includes(quiz.id)"
                    class="btn btn-sm btn-secondary"
                    disabled
                  >
                    Taken
                  </button>
                  <button
                    v-else
                    class="btn btn-sm btn-success"
                    @click="startQuiz(quiz.id)"
                  >
                    Start Quiz
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </template>
        <template v-else>
          <p class="text-center text-muted">No upcoming quizzes.</p>
        </template>
      </div>
    </div>

    <!-- Quiz Details Modal -->
    <div
      class="modal fade"
      tabindex="-1"
      :class="{ show: showModal }"
      :style="{ display: showModal ? 'block' : 'none' }"
      aria-modal="true"
      role="dialog"
      v-if="selectedQuiz && showModal"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Quiz Details</h5>
            <button
              type="button"
              class="btn-close"
              @click="closeModal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p><strong>Quiz ID:</strong> {{ selectedQuiz.id }}</p>
            <p><strong>Subject:</strong> {{ selectedQuiz.chapter.subject.name }}</p>
            <p><strong>Chapter:</strong> {{ selectedQuiz.chapter.name }}</p>
            <p><strong>No. of Questions:</strong> {{ selectedQuiz.questions.length }}</p>
            <p><strong>Scheduled Date:</strong> {{ formatDate(selectedQuiz.date_of_quiz) }}</p>
            <p><strong>Duration:</strong> {{ selectedQuiz.time_duration }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-danger" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4 text-center">
      <router-link to="/user/scores" class="btn btn-outline-success btn-lg me-2">
        Scores
      </router-link>
      <router-link to="/user/summary" class="btn btn-outline-info btn-lg">
        Summary
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/axios'
import UserNavbar from '@/components/UserNavbar.vue'

const allQuizzes = ref([])
const takenQuizIds = ref([])
const showModal = ref(false)
const selectedQuiz = ref(null)
const router = useRouter()
const userName = ref('User') // TODO: Replace with actual user name from store or API

function formatDate(dateStr) {
  if (!dateStr) return ''
  // Accepts 'YYYY-MM-DD' or Date object
  const d = typeof dateStr === 'string' ? new Date(dateStr) : dateStr
  // Format as DD-MM-YYYY
  return d instanceof Date && !isNaN(d) ? `${d.getDate().toString().padStart(2, '0')}-${(d.getMonth()+1).toString().padStart(2, '0')}-${d.getFullYear()}` : ''
}

function openModal(quiz) {
  selectedQuiz.value = quiz
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedQuiz.value = null
}

function startQuiz(quizId) {
  router.push(`/user/quiz/${quizId}/start`)
}

function handleLogout() {
  // Example logout logic
  apiClient.post('/api/auth/logout').finally(() => {
    localStorage.removeItem('is_admin')
    localStorage.removeItem('is_logged_in')
    router.push('/login')
  })
}

function handleSearch(query) {
  // Example: route to a search results page with the query as a param
  if (query && query.trim()) {
    router.push({ name: 'UserSearchResults', query: { q: query } })
  }
}

onMounted(async () => {
  try {
    const { data } = await apiClient.get('/api/user/quizzes')
    allQuizzes.value = data.all_quizzes || []
    takenQuizIds.value = data.taken_quiz_ids || []
  } catch (e) {
    allQuizzes.value = []
    takenQuizIds.value = []
  }
})
</script>

<style scoped>
.user-dashboard-card {
  max-width: 750px;
  margin: auto;
}
.modal {
  background: rgba(0,0,0,0.3);
}
.modal-backdrop {
  z-index: 1040;
}
.modal.show {
  display: block;
}
</style>
