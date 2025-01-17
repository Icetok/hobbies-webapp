<template>
  <main class="container pt-4">
    <div class="d-flex justify-content-between align-items-center">
      <div>
        <router-link v-if="!isAuthenticated" :to="{ name: 'Signup' }">Signup</router-link> |
        <router-link v-if="!isAuthenticated" :to="{ name: 'Login' }">Login</router-link> |
        <router-link v-if="isAuthenticated" :to="{ name: 'Main Page' }">Main Page</router-link> |
        <router-link v-if="isAuthenticated" :to="{ name: 'Add Hobby' }">Add Hobby</router-link> |
        <router-link v-if="isAuthenticated" :to="{ name: 'Similar Users' }">Similar Users</router-link> |
        <router-link v-if="isAuthenticated" :to="{ name: 'Friend Requests' }">Friend Requests</router-link> |
        <button v-if="isAuthenticated" @click="logout">Logout</button>
      </div>
      <div v-if="isAuthenticated" class="text-muted">
        Logged in as: {{ username }}
      </div>
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

    // Reactive computed properties
    const isAuthenticated = computed(() => userStore.isAuthenticated);
    const username = computed(() => userStore.username);

    const logout = async () => {
      const response = await fetch('http://127.0.0.1:8000/api/logout/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        userStore.logout();
        router.push('/login');
      } else {
        console.error('Logout failed');
      }
    };

    return {
      isAuthenticated,
      username,
      logout,
    };
  },
});
</script>
