<template>
  <div class="navbar-wrapper">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary px-4">
      <div class="container-fluid d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center gap-3">
          <router-link class="nav-link text-white" to="/admin">Home</router-link>
          <router-link class="nav-link text-white" to="/admin/quizzes">Quiz</router-link>
          <router-link class="nav-link text-white" to="/admin/users">Users</router-link>
          <router-link class="nav-link text-white" to="/admin/summary">Summary</router-link>
        </div>

        <span class="text-white fw-semibold fs-5">Welcome Admin!</span>

        <div class="d-flex align-items-center gap-2">
          <select v-model="searchCategory" class="form-select form-select-sm" style="width: 120px;">
            <option value="users">Users</option>
            <option value="subjects">Subjects</option>
            <option value="quizzes">Quizzes</option>
          </select>
          <input v-model="searchQuery" type="text" class="form-control form-control-sm" placeholder="Search..." @keyup.enter="searchData" />
          <button @click="searchData" class="btn btn-sm btn-light">Search</button>
          <button @click="logout" class="btn btn-sm btn-danger">Logout</button>
        </div>
      </div>
    </nav>

    <!-- Search Results Modal -->
    <div v-if="searchResults.length > 0 || (hasSearched && searchResults.length === 0)" class="modal fade show" style="display: block; background-color: rgba(0,0,0,0.5);" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Search Results</h5>
            <button type="button" class="btn-close" @click="clearSearch"></button>
          </div>
          <div class="modal-body">
            <div v-if="searchResults.length > 0">
              <div class="row">
                <div class="col-12">
                  <div class="card shadow-sm">
                    <ul class="list-group list-group-flush">
                      <li v-for="(item, index) in searchResults" :key="index" class="list-group-item">
                        <!-- Quiz Results -->
                        <div v-if="searchCategory === 'quizzes'">
                          <strong>Quiz ID:</strong> {{ item.id }}<br>
                          <strong>Chapter:</strong> {{ item.chapter_name }}<br>
                          <strong>Subject:</strong> {{ item.subject_name }}<br>
                          <strong>Date:</strong> {{ formatDate(item.date_of_quiz) }}
                        </div>

                        <!-- Subject Results -->
                        <div v-else-if="searchCategory === 'subjects'">
                          <strong>Subject:</strong> {{ item.name }}<br>
                          <strong>Description:</strong> {{ item.description || 'No description' }}<br>
                          
                          <div v-if="item.chapters && item.chapters.length > 0">
                            <strong>Quizzes:</strong>
                            <ul>
                              <li v-for="chapter in item.chapters" :key="chapter.id">
                                <div v-for="quiz in chapter.quizzes" :key="quiz.id">
                                  <ul>
                                    <li>
                                      <b>Quiz ID:</b> {{ quiz.id }}<br>
                                      <b>Date of Quiz:</b> {{ formatDate(quiz.date_of_quiz) }}
                                    </li>
                                  </ul>
                                </div>
                              </li>
                            </ul>
                          </div>
                          <div v-else>
                            <p>No quizzes available for this subject.</p>
                          </div>
                        </div>

                        <!-- User Results -->
                        <div v-else-if="searchCategory === 'users'">
                          <strong>Name:</strong> {{ item.full_name }}<br>
                          <strong>Email:</strong> {{ item.email }}<br>
                          <strong>Qualification:</strong> {{ item.qualification || 'N/A' }}<br>
                          <strong>DOB:</strong> {{ formatDate(item.dob) || 'N/A' }}
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-danger">No results found.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="clearSearch">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Subjects & Chapters -->
    <div class="w-100 mt-5" style="padding-left:0;padding-right:0;">
      <div class="text-center my-4">
        <h2 class="fw-bold">Subjects</h2>
        <p class="text-muted">Total subjects: {{ subjects.length }}</p>
        <div v-if="isLoading" class="d-flex justify-content-center align-items-center gap-2">
          <div class="spinner-border spinner-border-sm text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <span class="text-muted">Loading subjects...</span>
        </div>
      </div>
      <div v-if="subjects.length === 0" class="text-center py-5">
        <div class="alert alert-info">
          <h5>No subjects found</h5>
          <p>Create your first subject to get started!</p>
        </div>
      </div>
      <div v-else class="row g-4 w-100" style="margin:0;">
        <div class="col-12 col-md-6 col-lg-4 mb-4 subject-card" v-for="subject in subjects" :key="subject.id">
          <div class="card h-100 shadow-sm">
            <div class="card-header bg-primary text-white text-center">
              <h5 class="mb-0">{{ subject.name }}</h5>
            </div>
            <div class="card-body">
              <div v-if="subject.chapters.length === 0" class="text-center text-muted py-3">
                <p>No chapters yet. Add your first chapter!</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Description</th>
                      <th>No. of Questions</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="chapter in subject.chapters" :key="chapter.id">
                      <td>{{ chapter.id }}</td>
                      <td>{{ chapter.name }}</td>
                      <td>{{ chapter.description || 'No description' }}</td>
                      <td>{{ chapter.question_count || 0 }}</td>
                      <td>
                        <button class="btn btn-sm btn-warning me-1" @click="editChapter(chapter.id)">Edit</button>
                        <button class="btn btn-sm btn-danger" @click="deleteChapter(chapter.id)">Delete</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="card-footer text-center">
              <div>
                <button class="btn btn-sm btn-danger me-2" @click="deleteSubject(subject.id)">Delete Subject</button>
                <button class="btn btn-sm btn-warning me-2" @click="editSubject(subject.id)">Edit Subject</button>
              </div>
              <div>
                <button class="btn btn-sm btn-success me-2" @click="addChapter(subject.id)">+ Add Chapter</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="text-center mt-4">
        <router-link to="/admin/subject/create" class="btn btn-outline-success btn-lg me-2">+ Add Subject</router-link>
        <router-link to="/admin/users" class="btn btn-outline-primary btn-lg me-2">Users</router-link>
        <router-link to="/admin/summary" class="btn btn-outline-info btn-lg">Summary</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/axios';

const router = useRouter();
const subjects = ref([]);
const searchCategory = ref('subjects');
const searchQuery = ref('');
const searchResults = ref([]);
const hasSearched = ref(false);
const isLoading = ref(false);

const fetchSubjects = async (forceRefresh = false) => {
  try {
    isLoading.value = true;
    
    const url = forceRefresh ? `/api/admin/subjects?_t=${Date.now()}` : '/api/admin/subjects';
    
    const response = await apiClient.get(url);
    
    if (response.data && response.data.subjects) {
      subjects.value = response.data.subjects;
    } else {
      subjects.value = [];
    }
  } catch (err) {
    console.error('Error fetching subjects:', err);
    if (err.response) {
      if (err.response.status === 401) {
        alert('Please log in again');
        localStorage.removeItem('is_logged_in');
        localStorage.removeItem('is_admin');
        router.push('/login');
      } else if (err.response.status === 403) {
        alert('Access denied. Please log in as admin.');
        localStorage.removeItem('is_logged_in');
        localStorage.removeItem('is_admin');
        router.push('/login');
      }
    }
    subjects.value = [];
  } finally {
    isLoading.value = false;
  }
};

const searchData = async () => {
  if (!searchQuery.value.trim()) {
    alert('Please enter a search query');
    return;
  }

  try {
    hasSearched.value = true;
    let endpoint = '';
    
    switch (searchCategory.value) {
      case 'users':
        endpoint = `/api/admin/search/users?q=${encodeURIComponent(searchQuery.value)}`;
        break;
      case 'subjects':
        endpoint = `/api/admin/search/subjects?q=${encodeURIComponent(searchQuery.value)}`;
        break;
      case 'quizzes':
        endpoint = `/api/admin/search/quizzes?q=${encodeURIComponent(searchQuery.value)}`;
        break;
      default:
        endpoint = `/api/admin/search/subjects?q=${encodeURIComponent(searchQuery.value)}`;
    }

    const response = await apiClient.get(endpoint);
    searchResults.value = response.data.results || [];
  } catch (error) {
    console.error('Error searching:', error);
    searchResults.value = [];
  }
};

const clearSearch = () => {
  searchQuery.value = '';
  searchResults.value = [];
  hasSearched.value = false;
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

const editSubject = (id) => {
  router.push(`/admin/subject/edit/${id}`);
};

const deleteSubject = async (id) => {
  if (confirm('Are you sure you want to delete this subject?')) {
    try {
      const response = await apiClient.delete(`/api/admin/subject/${id}`);
      
      // Remove from local state immediately for better UX
      subjects.value = subjects.value.filter(subject => subject.id !== id);
      
      // Force refresh subjects data with cache busting
      await fetchSubjects(true); // Force refresh with cache busting
      
    } catch (error) {
      console.error('Error deleting subject:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
        
        if (error.response.status === 403) {
          alert('Access denied. Please log in again as an admin.');
          // Redirect to login
          localStorage.removeItem('isAdmin');
          localStorage.removeItem('isLoggedIn');
          router.push('/login');
        } else if (error.response.status === 404) {
          alert(`Subject not found: ${error.response.data.message || 'Subject may have been deleted already'}`);
        } else {
          alert(`Failed to delete subject: ${error.response.data.message || 'Unknown error'}`);
        }
      } else {
        alert('Failed to delete subject: Network error');
      }
    }
  }
};

const addChapter = (subjectId) => {
  router.push(`/admin/chapter/add/${subjectId}`);
};

const editChapter = (id) => {
  router.push(`/admin/chapter/edit/${id}`);
};

const deleteChapter = async (id) => {
  if (confirm('Are you sure you want to delete this chapter?')) {
    try {
      const response = await apiClient.delete(`/api/admin/chapter/${id}`);
      
      // Force refresh subjects data
      await fetchSubjects();
      
    } catch (error) {
      console.error('Error deleting chapter:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
        
        if (error.response.status === 403) {
          alert('Access denied. Please log in again as an admin.');
          localStorage.removeItem('isAdmin');
          localStorage.removeItem('isLoggedIn');
          router.push('/login');
        } else if (error.response.status === 404) {
          alert(`Chapter not found: ${error.response.data.message || 'Chapter may have been deleted already'}`);
        } else {
          alert(`Failed to delete chapter: ${error.response.data.message || 'Unknown error'}`);
        }
      } else {
        alert('Failed to delete chapter: Network error');
      }
    }
  }
};

const logout = () => {
  localStorage.removeItem('isAdmin');
  localStorage.removeItem('isLoggedIn');
  router.push('/');
};

// Close modal when clicking outside
const closeModalOnOutsideClick = (event) => {
  if (event.target.classList.contains('modal')) {
    clearSearch()
  }
}

// Add event listener when search results are shown
watch(() => searchResults.value.length > 0 || hasSearched.value, (showModal) => {
  if (showModal) {
    document.addEventListener('click', closeModalOnOutsideClick)
  } else {
    document.removeEventListener('click', closeModalOnOutsideClick)
  }
})

onMounted(() => {
  // Check if user is logged in as admin
  const isLoggedIn = localStorage.getItem('is_logged_in');
  const isAdmin = localStorage.getItem('is_admin');
  
  if (!isLoggedIn || !isAdmin) {
    router.push('/login');
    return;
  }
  
  fetchSubjects(true); // Force fresh data on mount
});
</script>

<style scoped>
.subject-card {
  min-width: calc(33.333% + 200px);
  max-width: calc(33.333% + 200px);
}

@media (max-width: 991.98px) {
  .subject-card {
    min-width: calc(50% + 200px);
    max-width: calc(50% + 200px);
  }
}

@media (max-width: 767.98px) {
  .subject-card {
    min-width: calc(100% + 200px);
    max-width: calc(100% + 200px);
  }
}

.list-group-item {
  border-left: 4px solid #007bff;
  margin-bottom: 8px;
  border-radius: 8px;
}

.list-group-item:hover {
  background-color: #f8f9fa;
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

/* Ensure table content doesn't overflow */
.table {
  font-size: 0.875rem;
}

.table th, .table td {
  padding: 0.5rem 0.25rem;
  vertical-align: middle;
}

/* Specific column widths to ensure actions are visible */
.table th:nth-child(1), .table td:nth-child(1) { /* ID */
  width: 50px;
  min-width: 50px;
  max-width: 50px;
}

.table th:nth-child(2), .table td:nth-child(2) { /* Name */
  width: 100px;
  min-width: 100px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table th:nth-child(3), .table td:nth-child(3) { /* Description */
  width: 120px;
  min-width: 120px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table th:nth-child(4), .table td:nth-child(4) { /* No. of Questions */
  width: 80px;
  min-width: 80px;
  max-width: 80px;
}

.table th:nth-child(5), .table td:nth-child(5) { /* Actions */
  width: 160px;
  min-width: 160px;
  max-width: 160px;
  white-space: nowrap;
}

/* Make the card body scrollable if needed */
.card-body {
  max-height: 400px;
  overflow-y: auto;
}

/* Responsive table adjustments */
@media (max-width: 1200px) {
  .table th, .table td {
    padding: 0.25rem 0.125rem;
    font-size: 0.8rem;
  }
  
  .table th:nth-child(2), .table td:nth-child(2) { /* Name */
    width: 80px;
    min-width: 80px;
    max-width: 80px;
  }
  
  .table th:nth-child(3), .table td:nth-child(3) { /* Description */
    width: 100px;
    min-width: 100px;
    max-width: 100px;
  }
  
  .table th:nth-child(5), .table td:nth-child(5) { /* Actions */
    width: 140px;
    min-width: 140px;
    max-width: 140px;
  }
}

@media (max-width: 768px) {
  .table th, .table td {
    padding: 0.125rem;
    font-size: 0.75rem;
  }
  
  .table th:nth-child(2), .table td:nth-child(2) { /* Name */
    width: 60px;
    min-width: 60px;
    max-width: 60px;
  }
  
  .table th:nth-child(3), .table td:nth-child(3) { /* Description */
    width: 80px;
    min-width: 80px;
    max-width: 80px;
  }
  
  .table th:nth-child(5), .table td:nth-child(5) { /* Actions */
    width: 120px;
    min-width: 120px;
    max-width: 120px;
  }
  
  .btn-sm {
    padding: 0.125rem 0.25rem;
    font-size: 0.75rem;
  }
}

/* Ensure action buttons are always visible */
.table td:last-child {
  white-space: nowrap;
  min-width: 160px;
  padding-right: 8px;
}

.table td:last-child .btn {
  margin: 0 2px;
  min-width: 60px;
}

/* Modal styles */
.modal {
  z-index: 1050;
}

.modal-dialog {
  max-width: 800px;
}

.list-group-item {
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}
</style>
