import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';

import MainPage from '../pages/MainPage.vue';
import AddHobby from '../pages/AddHobby.vue';
import SignupPage from '../pages/SignupPage.vue';
import LoginPage from '../pages/LoginPage.vue';
import SimilarUsersPage from '../pages/SimilarUsersPage.vue';
import FriendRequestsPage from '../pages/FriendRequestsPage.vue';

let base = (import.meta.env.MODE === 'development') ? import.meta.env.BASE_URL : '';

const router = createRouter({
  history: createWebHistory(base),
  routes: [
    {
      path: '/',
      name: 'Main Page',
      component: MainPage,
      meta: { requiresAuth: true },
    },
    { path: '/signup/', name: 'Signup', component: SignupPage },
    { path: '/login/', name: 'Login', component: LoginPage },
    {
      path: '/add-hobby/',
      name: 'Add Hobby',
      component: AddHobby,
      meta: { requiresAuth: true },
    },
    {
      path: '/similar-users/',
      name: 'Similar Users',
      component: SimilarUsersPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/friend-requests/',
      name: 'Friend Requests',
      component: FriendRequestsPage,
      meta: { requiresAuth: true },
    },
  ],
});

// Add a global navigation guard
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();

  // Check authentication status if not already done
  if (!userStore.isAuthenticated) {
    await userStore.checkAuth();
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    // If the route requires auth and the user is not logged in, redirect to Login
    next({ name: 'Login' });
  } else {
    next(); // Allow navigation
  }
});

export default router;
