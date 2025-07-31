<template>
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
        <select :value="searchCategory" @change="$emit('update:searchCategory', $event.target.value)" class="form-select form-select-sm" style="width: 120px;">
          <option value="users">Users</option>
          <option value="subjects">Subjects</option>
          <option value="quizzes">Quizzes</option>
        </select>
        <input :value="searchQuery" @input="$emit('update:searchQuery', $event.target.value)" type="text" class="form-control form-control-sm" placeholder="Search..." />
        <button @click="$emit('search')" class="btn btn-sm btn-light">Search</button>
        <button @click="$emit('logout')" class="btn btn-sm btn-danger">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
const props = defineProps({
  searchCategory: String,
  searchQuery: String
})
const emits = defineEmits(['search', 'logout', 'update:searchCategory', 'update:searchQuery'])
</script> 