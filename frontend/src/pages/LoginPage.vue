<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input v-model="formData.username" placeholder="Username" required />
      <input v-model="formData.password" placeholder="Password" type="password" required />
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useUserStore } from '@/store/user';

export default defineComponent({
  data() {
    return {
      formData: {
        username: '',
        password: '',
      },
    };
  },
  methods: {
    async login() {
      const response = await fetch('http://127.0.0.1:8000/api/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.formData),
      });

      if (response.ok) {
        const userStore = useUserStore();
        userStore.login(); // Update the user store
        alert('Login successful!');
        this.$router.push({ name: 'Main Page' }); // Redirect to main page
      } else {
        const errorData = await response.json();
        alert(`Login failed: ${errorData.error}`);
      }
    },
  },
});
</script>
