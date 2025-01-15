<template>
  <div v-if="isAuthenticated">
    <h2>User Profile</h2>
    <div v-if="loading">Loading...</div>
    
    <div v-else>
      <p><strong>Name:</strong> {{ userProfile.name }}</p>
      <p><strong>Email:</strong> {{ userProfile.email }}</p>
      <p><strong>Date of Birth:</strong> {{ userProfile.date_of_birth }}</p>

      <div v-if="userProfile.hobbies.length > 0">
        <strong>Hobbies:</strong>
        <ul>
          <li v-for="hobby in userProfile.hobbies" :key="hobby.id">{{ hobby.name }}</li>
        </ul>
      </div>
      <div v-else>
        <p>No hobbies found.</p>
      </div>
    </div>
  </div>

  <div v-else>
    <p>Please log in to view your profile.</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router"; // Vue Router for redirection

export default defineComponent({
  data() {
    return {
      userProfile: {
        name: '',
        email: '',
        date_of_birth: '',
        hobbies: [],
      },
      loading: true,
    };
  },
  computed: {
    isAuthenticated() {
      const userStore = useUserStore();
      return userStore.isAuthenticated;
    },
  },
  methods: {
    async fetchUserProfile() {
      try {
        // Make GET request to fetch user profile with session cookies included
        const response = await fetch("http://127.0.0.1:8000/api/user-profile/", {
          method: "GET",
          credentials: "include", // Ensure cookies (sessionid and csrftoken) are included
        });

        if (response.ok) {
          const data = await response.json();
          this.userProfile = data;
        } else {
          console.error("Failed to fetch user profile");
        }
      } catch (error) {
        console.error("Error fetching user profile:", error);
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    if (!this.isAuthenticated) {
      // Redirect to login page if user is not authenticated
      this.$router.push('/login');
    } else {
      this.fetchUserProfile(); // Fetch user profile when authenticated
    }
  },
});
</script>

<style scoped>
/* Add styles here */
</style>