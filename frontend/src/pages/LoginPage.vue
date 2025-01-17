<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input v-model="formData.username" placeholder="Username" required />
      <input v-model="formData.password" placeholder="Password" type="password" required />
      <button type="submit">Login</button>
    </form>
    <div v-if="successMessage" class="alert alert-success mt-3">
      {{ successMessage }}
    </div>
    <div v-if="errorMessage" class="alert alert-danger mt-3">
      {{ errorMessage }}
    </div>
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
      successMessage: '', // For success alert
      errorMessage: '', // For error alert
    };
  },
  methods: {
    async login() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/login/', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.formData),
        });

        const data = await response.json();
        
        if (response.ok && data.isAuthenticated) {
          const userStore = useUserStore();
          userStore.login(data.username);
          userStore.setProfile(data.profile);
          console.log('Login successful, session:', data.sessionid);
          
          this.successMessage = `Logged in as: ${data.username}`; // Show success message
          this.errorMessage = ''; // Clear any previous error message

          // Wait a brief moment for the session to be established
          await new Promise(resolve => setTimeout(resolve, 100));
          
          this.$router.push('/');
        } else {
          console.error('Login failed:', data.error);
          this.errorMessage = `Login failed: ${data.error}`; // Show error message
          this.successMessage = ''; // Clear any previous success message
        }
      } catch (error) {
        console.error('Login error:', error);
        this.errorMessage = 'Login failed: Network error'; // Show network error
        this.successMessage = ''; // Clear any previous success message
      }
    },
  },
});
</script>

<style scoped>
.alert {
  padding: 1rem;
  border-radius: 0.25rem;
}
.alert-success {
  color: #155724;
  background-color: #d4edda;
  border-color: #c3e6cb;
}
.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}
.mt-3 {
  margin-top: 1rem;
}
</style>
