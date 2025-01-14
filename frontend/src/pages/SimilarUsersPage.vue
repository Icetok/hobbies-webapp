<template>
    <div class="similar-users-container">
      <h2>Users with Similar Hobbies</h2>
      <div v-if="loading" class="text-center">
        Loading...
      </div>
      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
      </div>
      <div v-else>
        <div v-if="similarUsers.length === 0" class="alert alert-info">
          No users with similar hobbies found.
        </div>
        <div v-else class="user-cards">
          <div v-for="user in similarUsers" :key="user.username" class="card mb-3">
            <div class="card-body">
              <h5 class="card-title">{{ user.name }} ({{ user.username }})</h5>
              <p class="card-text">
                <strong>Common Hobbies ({{ user.similarity_score }}):</strong>
                {{ user.common_hobbies.join(', ') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  interface SimilarUser {
    username: string;
    name: string;
    common_hobbies: string[];
    similarity_score: number;
  }
  
  export default defineComponent({
    data() {
      return {
        similarUsers: [] as SimilarUser[],
        loading: true,
        error: null as string | null,
      };
    },
    async mounted() {
      await this.fetchSimilarUsers();
    },
    methods: {
      async fetchSimilarUsers() {
        try {
          const response = await fetch('http://127.0.0.1:8000/api/similar-users/', {
            credentials: 'include',
          });
          
          if (!response.ok) {
            throw new Error('Failed to fetch similar users');
          }
          
          const data = await response.json();
          this.similarUsers = data.similar_users;
        } catch (err) {
          this.error = err instanceof Error ? err.message : 'An error occurred';
        } finally {
          this.loading = false;
        }
      },
    },
  });
  </script>
  
  <style scoped>
  .similar-users-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .user-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .card {
    border: 1px solid #ddd;
    border-radius: 8px;
    transition: transform 0.2s;
  }
  
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  </style>