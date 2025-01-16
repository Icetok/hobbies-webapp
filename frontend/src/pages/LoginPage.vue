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
          
          // Wait a brief moment for the session to be established
          await new Promise(resolve => setTimeout(resolve, 100));
          
          this.$router.push('/');
        } else {
          console.error('Login failed:', data.error);
          alert(`Login failed: ${data.error}`);
        }
      } catch (error) {
        console.error('Login error:', error);
        alert('Login failed: Network error');
      }
    },
  },
});
</script>
