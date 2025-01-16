<template>
    <div v-if="isAuthenticated">
      <h2>Users with Similar Hobbies</h2>
      <div v-if="loading">Loading...</div>
      
      <div v-else-if="similarUsers.length > 0">
        <div v-for="user in similarUsers" :key="user.name" class="user-card mb-3 p-3 border rounded">
          <h3>{{ user.name }}</h3>
          <p>
            <strong>Common Hobbies ({{ user.similarity_score }}):</strong>
            <span v-for="(hobby, index) in user.common_hobbies" :key="hobby.id">
              {{ hobby.name }}{{ index < user.common_hobbies.length - 1 ? ', ' : '' }}
            </span>
          </p>
        </div>
      </div>
      
      <div v-else>
        <p>No users with similar hobbies found.</p>
      </div>
    </div>
  
    <div v-else>
      <p>Please log in to view similar users.</p>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from "vue";
  import { useUserStore } from "@/store/user";
  
  interface Hobby {
    id: number;
    name: string;
  }
  
  interface SimilarUser {
    name: string;
    common_hobbies: Hobby[];
    similarity_score: number;
  }
  
  export default defineComponent({
    data() {
      return {
        similarUsers: [] as SimilarUser[],
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
      async fetchSimilarUsers() {
        try {
          const response = await fetch("http://127.0.0.1:8000/api/similar-users/", {
            method: "GET",
            credentials: "include",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            }
          });

          const data = await response.json();
          if (response.ok) {
            this.similarUsers = data.similar_users;
            console.log("Fetched similar users:", data);
          } else {
            console.error("Failed to fetch similar users:", data.error);
          }
        } catch (error) {
          console.error("Error fetching similar users:", error);
        } finally {
          this.loading = false;
        }
      },
    },
    async mounted() {
      await this.fetchSimilarUsers();
    },
  });
  </script>
  
  <style scoped>
  .user-card {
    background-color: #f8f9fa;
  }
  </style>