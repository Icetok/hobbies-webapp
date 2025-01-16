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
import { defineComponent, computed } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";

export default defineComponent({
  setup() {
    const userStore = useUserStore();
    return {
      userStore,
    };
  },
  computed: {
    isAuthenticated() {
      return this.userStore.isAuthenticated;
    },
    userProfile() {
      return this.userStore.profile;
    },
  },
  data() {
    return {
      loading: true,
    };
  },
  mounted() {
    if (!this.isAuthenticated) {
      this.$router.push('/login');
    } else {
      this.loading = false;
    }
  },
});
</script>

<style scoped>
/* Add styles here */
</style>