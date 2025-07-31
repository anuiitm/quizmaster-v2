<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="logout" />
  <div class="container mt-5">
    <h2 class="text-center mb-4">Edit Subject</h2>
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
        <button type="button" class="btn btn-danger btn-lg action-btn" @click="router.push('/admin')">Cancel</button>
        <button type="submit" class="btn btn-success btn-lg action-btn">Save Changes</button>
      </div>
    </form>
  </div>
</template>
<script setup>
import AdminNavbar from '@/components/AdminNavbar.vue'
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient from '@/api/axios';

const router = useRouter();
const route = useRoute();
const subjectId = route.params.id;

const form = ref({ name: '', description: '' });
const errors = ref({});
const message = ref('');
const searchCategory = ref('subjects');
const searchQuery = ref('');

const fetchSubject = async () => {
  try {
    const res = await apiClient.get(`/api/admin/subject/${subjectId}`);
    form.value = {
      name: res.data.name,
      description: res.data.description
    };
  } catch (err) {
    errors.value.global = 'Failed to fetch subject.';
  }
};

const handleSubmit = async () => {
  errors.value = {};
  message.value = '';
  try {
    await apiClient.put(`/api/admin/subject/${subjectId}`, form.value);
    message.value = 'Subject updated successfully!';
    setTimeout(() => router.push('/admin'), 1500);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.errors) {
      errors.value = err.response.data.errors;
    } else {
      errors.value.global = 'An unexpected error occurred. Please try again.';
    }
  }
};

const logout = () => {
  localStorage.removeItem('isAdmin');
  localStorage.removeItem('isLoggedIn');
  router.push('/');
};

onMounted(fetchSubject);
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
}
</style> 