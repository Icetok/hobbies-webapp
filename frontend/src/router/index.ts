import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';

import MainPage from '../pages/MainPage.vue';
import OtherPage from '../pages/OtherPage.vue';
import SignupPage from '../pages/SignupPage.vue';
import LoginPage from '../pages/LoginPage.vue';
import SimilarUsersPage from '../pages/SimilarUsersPage.vue';

let base = (import.meta.env.MODE === 'development') ? import.meta.env.BASE_URL : '';

const router = createRouter({
  history: createWebHistory(base),
  routes: [
    { path: '/signup/', name: 'Signup', component: SignupPage },
    { path: '/login/', name: 'Login', component: LoginPage },
    {
      path: '/',
      name: 'Main Page',
      component: MainPage,
      meta: { requiresAuth: true }, // Protect this route
    },
    {
      path: '/other/',
      name: 'Other Page',
      component: OtherPage,
      meta: { requiresAuth: true }, // Protect this route
    },
    {
      path: '/similar-users/',
      name: 'Similar Users',
      component: SimilarUsersPage,
      meta: { requiresAuth: true },
    }
  ],
});

// Add a global navigation guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    // If the route requires auth and the user is not logged in, redirect to Login
    next({ name: 'Login' });
  } else {
    next(); // Allow navigation
  }
});

export default router;
