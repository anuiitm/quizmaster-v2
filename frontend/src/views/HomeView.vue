<template>
  <div class="home-wrapper text-center">
    <div>
      <h1 class="title">QuizMaster</h1>
      <p class="subtitle">Test your knowledge. Track your progress. Learn better.</p>
      <div class="buttons">
        <router-link to="/login" class="btn btn-login">Login</router-link>
        <router-link to="/register" class="btn btn-register">Register</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// no logic needed
</script>

<style scoped>
.home-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--light-bg);
}

.buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}
</style>
