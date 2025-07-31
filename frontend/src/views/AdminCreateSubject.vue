<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="() => { localStorage.removeItem('isAdmin'); localStorage.removeItem('isLoggedIn'); router.push('/'); }" />
  <div class="container mt-5">
    <h2 class="text-center mb-4">Create New Subject</h2>

    <div v-if="message" class="alert alert-success text-center">{{ message }}</div>
    <div v-if="errors.global" class="alert alert-danger text-center">{{ errors.global }}</div>

    <form @submit.prevent="handleSubmit" class="card p-4 shadow-sm" style="max-width: 600px; margin: auto;">
      <div class="mb-3">
        <label for="name" class="form-label">Subject Name</label>
        <input v-model="form.name" id="name" class="form-control" />
        <div v-if="errors.name" class="text-danger">{{ errors.name }}</div>
      </div>

      <div class="mb-3">
        <label for="description" class="form-label">Description</label>
        <textarea v-model="form.description" id="description" class="form-control" rows="3" />
        <div v-if="errors.description" class="text-danger">{{ errors.description }}</div>
      </div>

      <div class="d-flex justify-content-center align-items-center gap-3 mt-3">
        <button type="button" class="btn btn-danger btn-lg action-btn d-flex align-items-center justify-content-center" @click="router.push('/admin')">Cancel</button>
        <button type="submit" class="btn btn-success btn-lg action-btn d-flex align-items-center justify-content-center">Create Subject</button>
      </div>
    </form>
  </div>
</template>
<script setup>
import AdminNavbar from '@/components/AdminNavbar.vue'
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// 1. Import the configured apiClient instead of using fetch
import apiClient from '@/api/axios'; 

const form = ref({
  name: '',
  description: ''
});

const errors = ref({});
const message = ref('');
const router = useRouter();

const searchCategory = ref('subjects');
const searchQuery = ref('');

const handleSubmit = async () => {
  // Clear previous messages and errors
  errors.value = {};
  message.value = '';

  try {
    // 2. Use apiClient.post() instead of the fetch call.
    // The apiClient will automatically handle the URL, credentials, and CSRF token.
    const response = await apiClient.post('/api/admin/create_subject', form.value);

    // On success (status 2xx), this code will run
    message.value = response.data.message;
    form.value = { name: '', description: '' }; // Reset the form

    // Optional: Redirect the admin back to the dashboard after a short delay
    setTimeout(() => {
      router.push('/admin');
    }, 2000);

  } catch (err) {
    // 3. Handle errors from apiClient. The error structure is slightly different.
    // Axios places the server's response in err.response.
    if (err.response && err.response.data && err.response.data.errors) {
      // This will catch the validation errors from your Flask backend
      errors.value = err.response.data.errors;
    } else {
      // Generic error for network issues or other problems
      errors.value.global = 'An unexpected error occurred. Please try again.';
      console.error(err); // Log the full error for debugging
    }
  }
};
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
