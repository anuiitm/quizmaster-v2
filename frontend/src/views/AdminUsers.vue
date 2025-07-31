<template>
  <AdminNavbar v-model:searchCategory="searchCategory" v-model:searchQuery="searchQuery" @search="() => {}" @logout="logout" />
  <div class="container-fluid">
    <div class="row justify-content-center">
      <div class="col-12 col-xl-10">
        <div class="mt-4">
          <h2 class="text-center mb-4">Users</h2>
          
          <div v-if="loading" class="text-center">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else-if="error" class="alert alert-danger text-center">
            {{ error }}
          </div>
          
          <div v-else>
            <div class="table-responsive">
              <table class="table table-striped table-hover">
                <thead class="table-dark">
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Qualification</th>
                    <th>Date of Birth</th>
                    <th>Admin</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td>{{ user.full_name }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.qualification || 'N/A' }}</td>
                    <td>{{ formatDate(user.dob) || 'N/A' }}</td>
                    <td>
                      <span v-if="user.is_admin" class="badge bg-danger">Admin</span>
                      <span v-else class="badge bg-secondary">User</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="text-center mt-4">
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
const users = ref([]);
const loading = ref(true);
const error = ref('');
const searchCategory = ref('users');
const searchQuery = ref('');

const fetchUsers = async () => {
  try {
    loading.value = true;
    error.value = '';
    const response = await apiClient.get('/api/admin/users');
    users.value = response.data.users || [];
  } catch (err) {
    error.value = 'Failed to fetch users.';
    console.error('Error fetching users:', err);
  } finally {
    loading.value = false;
  }
};

const deleteUser = async (userId) => {
  if (!confirm('Are you sure you want to delete this user?')) return;
  
  try {
    await apiClient.delete(`/api/admin/user/${userId}`);
    users.value = users.value.filter(user => user.id !== userId);
    alert('User deleted successfully!');
  } catch (err) {
    alert('Failed to delete user.');
    console.error('Error deleting user:', err);
  }
};

const formatDate = (dateString) => {
  if (!dateString) return null;
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  } catch (error) {
    return dateString;
  }
};

const clearSearch = () => {
  router.push('/admin');
};

const logout = () => {
  apiClient.post('/api/auth/logout').finally(() => {
    localStorage.removeItem('is_admin');
    localStorage.removeItem('is_logged_in');
    router.push('/login');
  });
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.table th {
  font-weight: 600;
}

.badge {
  font-size: 0.75rem;
}
</style> 