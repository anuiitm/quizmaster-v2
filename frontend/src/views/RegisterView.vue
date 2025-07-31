<template>
  <div class="auth-wrapper">
    <div class="card">
      <h2 class="title">Register</h2>

      <div v-if="successMessage" class="alert alert-success text-center">
        {{ successMessage }}
      </div>

      <div v-if="error" class="alert alert-danger text-center">
        {{ error }}
      </div>

      <form @submit.prevent="handleRegister" v-if="!successMessage">
        <div class="form-group">
          <label>Email</label>
          <input v-model="email" type="email" required placeholder="Enter email" />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required placeholder="Enter password" />
        </div>

        <div class="form-group">
          <label>Full Name</label>
          <input v-model="fullName" type="text" required placeholder="Your full name" />
        </div>

        <div class="form-group">
          <label>Qualification</label>
          <select v-model="qualification" required>
            <option disabled value="">Select Qualification</option>
            <option>10th</option>
            <option>12th</option>
            <option>Bachelors</option>
            <option>Masters</option>
            <option>Doctorate</option>
          </select>
        </div>

        <div class="form-group">
          <label>Date of Birth</label>
          <input v-model="dob" type="date" required />
        </div>

        <button type="submit" class="btn btn-register" :disabled="isSubmitting">
          {{ isSubmitting ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <p class="alt-link" v-if="!successMessage">
        Already have an account? <router-link to="/login">Login</router-link>
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
const fullName = ref('')
const qualification = ref('')
const dob = ref('')
const error = ref('')
const successMessage = ref('')
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

const handleRegister = async () => {
  error.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  
  try {
    const response = await apiClient.post('/api/auth/register', {
      email: email.value,
      password: password.value,
      full_name: fullName.value,
      qualification: qualification.value,
      dob: dob.value
    })

    if (response.status === 201) {
      successMessage.value = response.data.message || 'Registration successful! Redirecting to login...'
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Registration failed.'
    console.error('Register error:', err)
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

.form-group input,
.form-group select {
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

.alert-success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.alert-danger {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}
</style>
