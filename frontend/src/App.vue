<template>
  <main class="container pt-4">
    <div>
      <router-link v-if="!isAuthenticated" :to="{ name: 'Signup' }">Signup</router-link> |
      <router-link v-if="!isAuthenticated" :to="{ name: 'Login' }">Login</router-link> |
      <router-link v-if="isAuthenticated" :to="{ name: 'Main Page' }">Main Page</router-link> |
      <router-link v-if="isAuthenticated" :to="{ name: 'Other Page' }">Other Page</router-link> |
      <router-link v-if="isAuthenticated" :to="{ name: 'Similar Users' }">Similar Users</router-link> |
      <button v-if="isAuthenticated" @click="logout">Logout</button>
    </div>
    <RouterView class="flex-shrink-0" />
  </main>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useUserStore } from '@/store/user';
import { useRouter } from 'vue-router';

export default defineComponent({
  setup() {
    const userStore = useUserStore();
    const router = useRouter();

    // Reactive computed property for authentication status
    const isAuthenticated = computed(() => userStore.isAuthenticated);

    const logout = async () => {
      const response = await fetch('http://127.0.0.1:8000/api/logout/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        userStore.logout();
        alert("You have been successfully logged out!");
        router.push({ name: 'Login' }); // Redirect to the login page after logout
      } else {
        alert("Failed to log out. Please try again.");
      }
    };

    return {
      isAuthenticated,
      logout,
    };
  },
});
</script>
