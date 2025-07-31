<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="logout" />
  <div class="container-fluid">
    <div class="row justify-content-center">
      <div class="col-12 col-xl-8">
        <div class="mt-4">
          <h2 class="text-center mb-4">Create Question</h2>
          
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
                <h5 class="mb-0">Question Details</h5>
              </div>
              <div class="card-body">
                <form @submit.prevent="createQuestion">
                  <div class="mb-3">
                    <label for="quizId" class="form-label">Quiz ID</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      :value="quizId" 
                      readonly 
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="title" class="form-label">Question Title</label>
                    <input 
                      type="text" 
                      v-model="questionData.title" 
                      class="form-control" 
                      placeholder="Enter question title"
                      required
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="description" class="form-label">Question Description</label>
                    <textarea 
                      v-model="questionData.question_statement" 
                      class="form-control" 
                      rows="3"
                      placeholder="Enter question description"
                      required
                    ></textarea>
                  </div>
                  
                  <div class="row">
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label for="option1" class="form-label">Option 1</label>
                        <input 
                          type="text" 
                          v-model="questionData.option1" 
                          class="form-control" 
                          placeholder="Enter option 1"
                          required
                        />
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label for="option2" class="form-label">Option 2</label>
                        <input 
                          type="text" 
                          v-model="questionData.option2" 
                          class="form-control" 
                          placeholder="Enter option 2"
                          required
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div class="row">
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label for="option3" class="form-label">Option 3</label>
                        <input 
                          type="text" 
                          v-model="questionData.option3" 
                          class="form-control" 
                          placeholder="Enter option 3"
                          required
                        />
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label for="option4" class="form-label">Option 4</label>
                        <input 
                          type="text" 
                          v-model="questionData.option4" 
                          class="form-control" 
                          placeholder="Enter option 4"
                          required
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label for="correctOption" class="form-label">Correct Option</label>
                    <select v-model="questionData.correct_option" class="form-select" required>
                      <option value="">Select correct option</option>
                      <option value="1">Option 1</option>
                      <option value="2">Option 2</option>
                      <option value="3">Option 3</option>
                      <option value="4">Option 4</option>
                    </select>
                  </div>
                  
                  <div class="d-flex justify-content-center align-items-center gap-3 mt-4">
                    <button type="button" class="btn btn-danger btn-lg action-btn d-flex align-items-center justify-content-center" @click="router.push('/admin/quizzes')">Cancel</button>
                    <button type="submit" class="btn btn-success btn-lg action-btn d-flex align-items-center justify-content-center">Create Question</button>
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
const quizId = route.params.quizId;
const loading = ref(false);
const error = ref('');
const searchCategory = ref('quizzes');
const searchQuery = ref('');

const questionData = ref({
  quiz_id: quizId,
  title: '',
  question_statement: '',
  option1: '',
  option2: '',
  option3: '',
  option4: '',
  correct_option: ''
});

const createQuestion = async () => {
  try {
    loading.value = true;
    const response = await apiClient.post('/api/admin/question', questionData.value);
    alert('Question created successfully!');
    router.push('/admin/quizzes');
  } catch (err) {
    alert('Failed to create question. Please try again.');
    console.error('Error creating question:', err);
  } finally {
    loading.value = false;
  }
};

const logout = () => {
  localStorage.removeItem('isAdmin');
  localStorage.removeItem('isLoggedIn');
  router.push('/');
};

onMounted(() => {
  // Set the quiz_id from the route parameter
  questionData.value.quiz_id = quizId;
});
</script>

<style scoped>
.action-btn {
  min-width: 160px;
  height: 48px;
  padding: 0 2rem;
  font-size: 1.25rem;
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
  line-height: 1;
  box-sizing: border-box;
  border: none;
  outline: none;
}
</style> 