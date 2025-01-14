<template>
  <div class="signup-container">
    <h2>Signup</h2>
    <form @submit.prevent="signup" class="signup-form">
      <div class="form-group">
        <input v-model="formData.username" placeholder="Username" required class="form-control" />
      </div>
      <div class="form-group">
        <input v-model="formData.name" placeholder="Name" required class="form-control" />
      </div>
      <div class="form-group">
        <input v-model="formData.email" placeholder="Email" type="email" required class="form-control" />
      </div>
      <div class="form-group">
        <input v-model="formData.date_of_birth" placeholder="Date of Birth" type="date" required class="form-control" />
      </div>
      <div class="form-group">
        <input v-model="formData.password1" placeholder="Password" type="password" required class="form-control" />
      </div>
      <div class="form-group">
        <input v-model="formData.password2" placeholder="Confirm Password" type="password" required class="form-control" />
      </div>
      
      <div class="form-group hobbies-section">
        <label class="hobbies-label">Select Hobbies (required):</label>
        <div class="hobbies-grid">
          <div v-for="hobby in hobbies" :key="hobby.id" class="hobby-item">
            <input
              type="checkbox"
              :id="'hobby-' + hobby.id"
              :value="hobby.id"
              v-model="formData.hobbies"
              class="hobby-checkbox"
            />
            <label :for="'hobby-' + hobby.id">{{ hobby.name }}</label>
          </div>
        </div>
        <div v-if="showHobbiesError" class="error-message">
          Please select at least one hobby
        </div>
      </div>

      <button type="submit" class="btn btn-primary">Sign Up</button>
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
      showHobbiesError: false,
    };
  },
  async mounted() {
    await this.fetchHobbies();
  },
  methods: {
    async fetchHobbies() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/hobbies/');
        const data = await response.json();
        this.hobbies = data.hobbies;
      } catch (error) {
        console.error('Error fetching hobbies:', error);
        alert('Failed to load hobbies. Please try again.');
      }
    },
    async signup() {
      // Reset error state
      this.showHobbiesError = false;

      // Validate hobbies selection
      if (this.formData.hobbies.length === 0) {
        this.showHobbiesError = true;
        return;
      }

      try {
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
      } catch (error) {
        console.error('Error during signup:', error);
        alert('An error occurred during signup. Please try again.');
      }
    },
  },
});
</script>

<style scoped>
.signup-container {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.signup-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.hobbies-section {
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 4px;
}

.hobbies-label {
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
}

.hobbies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.hobby-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 5px;
}

.hobby-checkbox {
  margin-right: 5px;
}
</style>
