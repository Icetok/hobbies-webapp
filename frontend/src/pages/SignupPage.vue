<template>
  <div>
    <h2>Signup</h2>
    <form @submit.prevent="signup">
      <input v-model="formData.username" placeholder="Username" required />
      <input v-model="formData.name" placeholder="Name" required />
      <input v-model="formData.email" placeholder="Email" type="email" required />
      <input v-model="formData.date_of_birth" placeholder="Date of Birth" type="date" required />
      <input v-model="formData.password1" placeholder="Password" type="password" required />
      <input v-model="formData.password2" placeholder="Confirm Password" type="password" required />
      <div>
        <label>Select Hobbies:</label>
        <div v-for="hobby in hobbies" :key="hobby.id">
          <input
            type="checkbox"
            :value="hobby.id"
            v-model="formData.hobbies"
          /> {{ hobby.name }}
        </div>
      </div>
      <button type="submit">Sign Up</button>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      formData: {
        username: '',
        name: '',
        email: '',
        date_of_birth: '',
        password1: '',
        password2: '',
        hobbies: [], // Array to store selected hobby IDs
      },
      hobbies: [], // List of available hobbies
    };
  },
  async mounted() {
    await this.fetchHobbies();
  },
  methods: {
    async fetchHobbies() {
      const response = await fetch('http://127.0.0.1:8000/api/hobbies/');
      const data = await response.json();
      this.hobbies = data.hobbies;
    },
    async signup() {
      const response = await fetch('http://127.0.0.1:8000/api/signup/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.formData),
      });

      if (response.ok) {
        alert('Signup successful!');
        this.$router.push({ name: 'Login' });
      } else {
        const errorData = await response.json();
        alert(`Signup failed: ${JSON.stringify(errorData.errors)}`);
      }
    },
  },
});
</script>
