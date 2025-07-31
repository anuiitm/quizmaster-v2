<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="logout" />
  <div class="container-fluid">
    <div class="row justify-content-center">
      <div class="col-12 col-xl-8">
        <div class="mt-4">
          <h2 class="text-center mb-4">Create Quiz</h2>
          
          <div class="card">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Quiz Details</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="createQuiz">
                <div class="mb-3">
                  <label for="chapter" class="form-label">Chapter</label>
                  <select v-model="quizData.chapter_id" class="form-select" required>
                    <option value="">Select a chapter</option>
                    <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                      {{ chapter.name }} ({{ chapter.subject?.name }})
                    </option>
                  </select>
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
                  <button type="submit" class="btn btn-success btn-lg action-btn d-flex align-items-center justify-content-center">Create Quiz</button>
                </div>
              </form>
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
const chapterId = route.params.chapterId;
const chapters = ref([]);
const searchCategory = ref('quizzes');
const searchQuery = ref('');

const quizData = ref({
  chapter_id: chapterId || '',
  date: '',
  duration: ''
});

const today = ref(new Date().toISOString().slice(0, 10));

const fetchChapters = async () => {
  try {
    const response = await apiClient.get('/api/admin/chapters');
    chapters.value = response.data.chapters;
  } catch (err) {
    console.error('Error fetching chapters:', err);
  }
};

const createQuiz = async () => {
  try {
    const response = await apiClient.post('/api/admin/quiz', quizData.value);
    alert('Quiz created successfully!');
    router.push('/admin/quizzes');
  } catch (err) {
    alert('Failed to create quiz. Please try again.');
    console.error('Error creating quiz:', err);
  }
};

const logout = () => {
  localStorage.removeItem('isAdmin');
  localStorage.removeItem('isLoggedIn');
  router.push('/');
};

onMounted(fetchChapters);
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