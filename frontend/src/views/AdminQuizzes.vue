<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="logout" />
  <div class="container-fluid">
    <div class="row justify-content-center">
      <div class="col-12 col-xl-10">
        <div class="mt-4">
          <h2 class="text-center mb-4">Quizzes</h2>
          
          <div v-if="loading" class="text-center">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else-if="error" class="alert alert-danger text-center">
            {{ error }}
          </div>
          
          <div v-else>
            <div class="row g-4">
              <div class="col-12 col-md-6 col-lg-4 mb-4 quiz-card" v-for="quiz in allQuizzes" :key="quiz.id">
                <div class="card h-100 shadow-sm">
                  <div class="card-header bg-primary text-white text-center">
                    <h5 class="mb-0">Quiz {{ quiz.id }}:
                    {{ quiz.chapter_name }} </h5>
                  </div>
                  <div class="card-body">
                    <div v-if="quiz.questions.length === 0" class="text-center text-muted py-3">
                      <p>No questions yet. Add your first question!</p>
                    </div>
                    <div v-else class="table-responsive">
                      <table class="table table-hover">
                        <thead>
                          <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="question in quiz.questions" :key="question.id">
                            <td>{{ question.id }}</td>
                            <td class="question-title">{{ question.title || 'Untitled Question' }}</td>
                            <td>
                              <button class="btn btn-sm btn-warning me-1" @click="editQuestion(question.id)">Edit</button>
                              <button class="btn btn-sm btn-danger" @click="deleteQuestion(question.id)">Delete</button>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div class="card-footer text-center">
                    <div>
                      <button class="btn btn-sm btn-danger me-2" @click="deleteQuiz(quiz.id)">Delete Quiz</button>
                      <button class="btn btn-sm btn-warning me-2" @click="editQuiz(quiz.id)">Edit Quiz</button>
                    </div>
                    <div>
                      <button class="btn btn-sm btn-success me-2" @click="addQuestion(quiz.id)">+ Add Question</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="text-center mt-4">
              <router-link to="/admin/quiz/create" class="btn btn-outline-success btn-lg me-2">+ Create Quiz</router-link>
              <button @click="clearSearch" class="btn btn-info btn-lg me-2" :disabled="loading" title="Refresh data and clear cache">
                <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i> 
                {{ loading ? 'Refreshing...' : 'Refresh' }}
              </button>
              <button @click="clearSearch" class="btn btn-danger btn-lg">
          ← Back to Admin Dashboard
        </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AdminNavbar from '@/components/AdminNavbar.vue'
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/axios';

const router = useRouter();
const allQuizzes = ref([]);
const loading = ref(true);
const error = ref('');
const searchCategory = ref('quizzes');
const searchQuery = ref('');

const fetchQuizzes = async (forceRefresh = false) => {
  try {
    loading.value = true;
    error.value = '';
    
    const url = forceRefresh ? `/api/admin/quizzes?_t=${Date.now()}` : '/api/admin/quizzes';
    const response = await apiClient.get(url);
    
    if (response.data && response.data.quizzes) {
      allQuizzes.value = response.data.quizzes;
    } else {
      allQuizzes.value = [];
    }
  } catch (err) {
    error.value = 'Failed to fetch quizzes.';
    console.error('Error fetching quizzes:', err);
    allQuizzes.value = [];
  } finally {
    loading.value = false;
  }
};

const addQuiz = (chapterId) => {
  router.push(`/admin/quiz/create/${chapterId}`);
};

const editQuiz = (quizId) => {
  router.push(`/admin/quiz/edit/${quizId}`);
};

const deleteQuiz = async (quizId) => {
  if (!confirm('Are you sure you want to delete this quiz?')) return;
  
  try {
    const response = await apiClient.delete(`/api/admin/quiz/${quizId}`);
    
    allQuizzes.value = allQuizzes.value.filter(quiz => quiz.id !== quizId);
    
    await fetchQuizzes(true);
    
  } catch (err) {
    console.error('Error deleting quiz:', err);
    alert('Failed to delete quiz.');
  }
};

const addQuestion = (quizId) => {
  router.push(`/admin/question/create/${quizId}`);
};

const editQuestion = (questionId) => {
  router.push(`/admin/question/edit/${questionId}`);
};

const deleteQuestion = async (questionId) => {
  if (!confirm('Are you sure you want to delete this question?')) return;
  
  try {
    const response = await apiClient.delete(`/api/admin/question/${questionId}`);
    
    await fetchQuizzes(true);
    
  } catch (err) {
    console.error('Error deleting question:', err);
    alert('Failed to delete question.');
  }
};

const editChapter = (chapterId) => {
  router.push(`/admin/chapter/edit/${chapterId}`);
};

const deleteChapter = async (chapterId) => {
  if (!confirm('Are you sure you want to delete this chapter?')) return;
  
  try {
    await apiClient.delete(`/api/admin/chapter/${chapterId}`);
    await fetchChapters(); // Refresh the list
  } catch (err) {
    alert('Failed to delete chapter.');
  }
};

const clearSearch = () => {
  router.push('/admin');
};

const logout = () => {
  localStorage.removeItem('isAdmin');
  localStorage.removeItem('isLoggedIn');
  router.push('/');
};

const formatDate = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleDateString();
};

const formatDuration = (duration) => {
  if (!duration) return 'Not set';
  // duration is in HH:MM format
  const [hours, minutes] = duration.split(':');
  return `${hours}h ${minutes}m`;
};

onMounted(() => {
  fetchQuizzes(true); // Force fresh data on mount
});
</script>

<style scoped>
.quiz-card {
  min-width: calc(33.333% + 200px);
  max-width: calc(33.333% + 200px);
}

@media (max-width: 991.98px) {
  .quiz-card {
    min-width: calc(50% + 200px);
    max-width: calc(50% + 200px);
  }
}

@media (max-width: 767.98px) {
  .quiz-card {
    min-width: calc(100% + 200px);
    max-width: calc(100% + 200px);
  }
}

.table-responsive {
  max-height: 300px;
  overflow-y: auto;
}

.table th {
  position: sticky;
  top: 0;
  background-color: #f8f9fa;
  z-index: 1;
  font-size: 0.875rem;
  padding: 0.5rem 0.25rem;
}

.table {
  width: 100%;
  margin-bottom: 0;
  font-size: 0.875rem;
}

.table td, .table th {
  padding: 0.5rem 0.25rem;
  vertical-align: middle;
}

/* Specific column widths to ensure actions are visible */
.table th:nth-child(1), .table td:nth-child(1) { /* ID */
  width: 50px;
  min-width: 50px;
  max-width: 50px;
}

.table th:nth-child(2), .table td:nth-child(2) { /* Title */
  width: 120px;
  min-width: 120px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table th:nth-child(3), .table td:nth-child(3) { /* Actions */
  width: 160px;
  min-width: 160px;
  max-width: 160px;
  white-space: nowrap;
}

.question-title {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card {
  width: 100%;
  margin: 0;
}

.card-body {
  padding: 1rem;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .table th, .table td {
    padding: 0.25rem 0.125rem;
    font-size: 0.8rem;
  }
  
  .table th:nth-child(2), .table td:nth-child(2) { /* Title */
    width: 120px;
    max-width: 120px;
  }
  
  .table th:nth-child(3), .table td:nth-child(3) { /* Actions */
    width: 120px;
    max-width: 120px;
  }
  
  .question-title {
    max-width: 120px;
  }
}

@media (max-width: 768px) {
  .table th, .table td {
    padding: 0.125rem;
    font-size: 0.75rem;
  }
  
  .table th:nth-child(2), .table td:nth-child(2) { /* Title */
    width: 100px;
    max-width: 100px;
  }
  
  .table th:nth-child(3), .table td:nth-child(3) { /* Actions */
    width: 100px;
    max-width: 100px;
  }
  
  .question-title {
    max-width: 100px;
  }
  
  .btn-sm {
    padding: 0.125rem 0.25rem;
    font-size: 0.75rem;
  }
}

/* Ensure action buttons are always visible */
.table td:last-child {
  white-space: nowrap;
  min-width: 140px;
}

.table td:last-child .btn {
  margin: 0 2px;
}
</style> 