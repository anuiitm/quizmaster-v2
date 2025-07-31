import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import AdminEditSubject from '@/views/AdminEditSubject.vue'
import AdminCreateChapter from '@/views/AdminCreateChapter.vue'
import AdminEditChapter from '@/views/AdminEditChapter.vue'
import AdminUsers from '@/views/AdminUsers.vue'
import AdminQuizzes from '@/views/AdminQuizzes.vue'
import AdminCreateQuiz from '@/views/AdminCreateQuiz.vue'
import AdminEditQuiz from '@/views/AdminEditQuiz.vue'
import AdminCreateQuestion from '@/views/AdminCreateQuestion.vue'
import AdminEditQuestion from '@/views/AdminEditQuestion.vue'
import AdminSummary from '@/views/AdminSummary.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  {
    path: '/user/dashboard',
    component: () => import('../views/UserDashboard.vue'),
    meta: { requiresAuth: true, userOnly: true }
  },
  {
    path: '/dashboard',
    redirect: '/user/dashboard'
  },
  {
    path: '/admin',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
  path: '/admin/subject/create',
  component: () => import('../views/AdminCreateSubject.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/subject/edit/:id',
  name: 'AdminEditSubject',
  component: AdminEditSubject,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/chapter/add/:subjectId',
  name: 'AdminCreateChapter',
  component: AdminCreateChapter,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/chapter/edit/:id',
  name: 'AdminEditChapter',
  component: AdminEditChapter,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/users',
  name: 'AdminUsers',
  component: AdminUsers,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/quizzes',
  name: 'AdminQuizzes',
  component: AdminQuizzes,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/quiz/create',
  name: 'AdminCreateQuiz',
  component: AdminCreateQuiz,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/quiz/create/:chapterId',
  name: 'AdminCreateQuizWithChapter',
  component: AdminCreateQuiz,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/quiz/edit/:id',
  name: 'AdminEditQuiz',
  component: AdminEditQuiz,
  meta: { requiresAuth: true, requiresAdmin: true }
},
{
  path: '/admin/question/create/:quizId',
  name: 'AdminCreateQuestion',
  component: AdminCreateQuestion,
  meta: { requiresAuth: true, requiresAdmin: true }
},
  {
    path: '/admin/question/edit/:id',
    name: 'AdminEditQuestion',
    component: AdminEditQuestion,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/user/scores',
    component: () => import('../views/UserScores.vue'),
    meta: { requiresAuth: true, userOnly: true }
  },
  {
    path: '/user/summary',
    component: () => import('../views/UserSummary.vue'),
    meta: { requiresAuth: true, userOnly: true }
  },
  {
    path: '/user/quiz/:quizId/start',
    component: () => import('../views/UserTakeQuiz.vue'),
    meta: { requiresAuth: true, userOnly: true }
  },
  {
    path: '/user/search-results',
    name: 'UserSearchResults',
    component: () => import('../views/UserSearchResults.vue'),
    meta: { requiresAuth: true, userOnly: true }
  },
  {
    path: '/admin/summary',
    name: 'AdminSummary',
    component: AdminSummary,
    meta: { requiresAuth: true, adminOnly: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ✅ Navigation Guard
router.beforeEach((to, from, next) => {
  const isAdmin = localStorage.getItem('is_admin') === 'true'
  const isLoggedIn = localStorage.getItem('is_logged_in') === 'true'

  // Block any protected route if not logged in
  if (to.meta.requiresAuth && !isLoggedIn) {
    return next('/login')
  }

  // Block non-admins from admin route
  if (to.meta.adminOnly && (!isLoggedIn || !isAdmin)) {
    return next('/dashboard')
  }

  // Block admins from user dashboard
  if (to.meta.userOnly && isAdmin) {
    return next('/admin')
  }

  next()
})

export default router
