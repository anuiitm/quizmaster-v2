<template>
  <div class="auth-wrapper text-center">
    <div>
      <h2 class="title">Login</h2>

      <div v-if="error" class="alert alert-danger text-center">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>E-Mail</label>
          <input type="email" class="form-control" placeholder="Email" v-model="email" />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required placeholder="Enter password" />
        </div>
        <button class="btn btn-register" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <p class="alt-link">
        Don't have an account? <router-link to="/register">Register</router-link>
      </p>
      <router-link to="/" class="btn btn-success">← Back to Home</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/axios' 
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const error = ref('')
const isSubmitting = ref(false)
const router = useRouter()

onMounted(async () => {
  try {
    const response = await apiClient.get('/api/get_csrf_token');
    if (response.data && response.data.csrf_token) {
      localStorage.setItem('csrf_token', response.data.csrf_token);
    }
  } catch (err) {
    error.value = 'Error connecting to the server. Please try again later.';
  }
});

const handleLogin = async () => {
  error.value = ''
  isSubmitting.value = true
  
  try {
    const response = await apiClient.post('/api/auth/login', {
      email: email.value,
      password: password.value
    }) 

    const isAdmin = response.data.is_admin
    localStorage.setItem('is_admin', String(isAdmin))
    localStorage.setItem('is_logged_in', 'true')
    if (isAdmin) {
      router.push('/admin')
    } else {
      router.push('/user/dashboard')
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Login failed. Please check your credentials.'
  } finally {
    isSubmitting.value = false
  }
}
</script>


<style scoped>
.auth-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: var(--light-bg);
  display: flex;
  justify-content: center;
  align-items: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  text-align: left;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 6px;
}

.form-group input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}

button {
  width: 100%;
  margin-top: 10px;
}

.alt-link {
  margin-top: 20px;
  color: var(--text-light);
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-weight: 500;
}

.alert-danger {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}
</style>
