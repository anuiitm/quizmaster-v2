<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="logout" />
  <div class="container-fluid">
    <div class="row justify-content-center">
      <div class="col-12 col-xl-8">
        <div class="mt-4">
          <h2 class="text-center mb-4">Edit Quiz</h2>
          
          <div v-if="loading" class="text-center">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else-if="error" class="alert alert-danger text-center">
            {{ error }}
          </div>
          
          <div v-else>
            <div class="card">
              <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Quiz Details</h5>
              </div>
              <div class="card-body">
                <form @submit.prevent="updateQuiz">
                  <div class="mb-3">
                    <label for="chapter" class="form-label">Chapter</label>
                    <input type="text" class="form-control" :value="quizData.chapter_name" readonly />
                  </div>
                  
                  <div class="mb-3">
                    <label for="date" class="form-label">Quiz Date</label>
                    <input 
                      type="date" 
                      v-model="quizData.date" 
                      class="form-control" 
                      :min="today"
                      required
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="duration" class="form-label">Duration (minutes)</label>
                    <input 
                      type="number" 
                      v-model="quizData.duration" 
                      class="form-control" 
                      placeholder="Enter duration in minutes"
                      min="1"
                      max="180"
                      required
                    />
                  </div>
                  
                  <div class="d-flex justify-content-center align-items-center gap-3 mt-4">
                    <button type="button" class="btn btn-danger btn-lg action-btn d-flex align-items-center justify-content-center" @click="router.push('/admin/quizzes')">Cancel</button>
                    <button type="submit" class="btn btn-success btn-lg action-btn d-flex align-items-center justify-content-center">Update Quiz</button>
                  </div>
                </form>
              </div>
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
import { useRouter, useRoute } from 'vue-router';
import apiClient from '@/api/axios';

const router = useRouter();
const route = useRoute();
const quizId = route.params.id;
const loading = ref(true);
const error = ref('');
const searchCategory = ref('quizzes');
const searchQuery = ref('');

const quizData = ref({
  chapter_name: '',
  date: '',
  duration: ''
});

const today = ref(new Date().toISOString().slice(0, 10));

const fetchQuiz = async () => {
  try {
    loading.value = true;
    const response = await apiClient.get(`/api/admin/quiz/${quizId}`);
    const quiz = response.data.quiz;
    
    const [hours, minutes] = quiz.time_duration.split(':');
    const durationInMinutes = parseInt(hours) * 60 + parseInt(minutes);
    
    quizData.value = {
      chapter_name: quiz.chapter?.name || 'Unknown Chapter',
      date: quiz.date_of_quiz,
      duration: durationInMinutes
    };
  } catch (err) {
    error.value = 'Failed to fetch quiz details.';
    console.error('Error fetching quiz:', err);
  } finally {
    loading.value = false;
  }
};

const updateQuiz = async () => {
  try {
    const response = await apiClient.put(`/api/admin/quiz/${quizId}`, quizData.value);
    alert('Quiz updated successfully!');
    router.push('/admin/quizzes');
  } catch (err) {
    alert('Failed to update quiz. Please try again.');
    console.error('Error updating quiz:', err);
  }
};

const logout = () => {
  localStorage.removeItem('isAdmin');
  localStorage.removeItem('isLoggedIn');
  router.push('/');
};

onMounted(fetchQuiz);
</script>

<style scoped>
.action-btn {
  min-width: 160px;
  height: 48px;
  padding: 0 2rem;
  font-size: 1.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  line-height: 1;
  box-sizing: border-box;
  border: none;
  outline: none;
}
</style> 