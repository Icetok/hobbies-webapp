<template>
  <div>
    <h2>Users with Similar Hobbies</h2>

    <!-- Filter Section -->
    <div class="filter-section mb-4">
      <h4>Filter by Age</h4>
      <div class="d-flex align-items-center">
        <label for="min-age" class="me-2">Min Age:</label>
        <input
          id="min-age"
          type="number"
          v-model="filters.min_age"
          @input="fetchSimilarUsers"
          placeholder="e.g. 20"
          class="form-control me-3"
        />

        <label for="max-age" class="me-2">Max Age:</label>
        <input
          id="max-age"
          type="number"
          v-model="filters.max_age"
          @input="fetchSimilarUsers"
          placeholder="e.g. 30"
          class="form-control"
        />
      </div>
    </div>

    <div v-if="loading">Loading...</div>
    
    <div v-if="referenceUser" class="alert alert-info mb-3">
      Showing similarities based on {{ referenceUser }}'s hobbies.
    </div>
    
    <div v-if="!loading && similarUsers.length > 0">
      <div v-for="user in similarUsers" :key="user.name" class="user-card mb-3 p-3 border rounded">
        <h3>{{ user.name }}</h3>
        <p>
          <strong>{{ user.similarity_score }} {{ user.similarity_score === 1 ? 'hobby' : 'hobbies' }} in common: </strong>
          <span v-for="(hobby, index) in user.common_hobbies" :key="hobby.id">
            {{ hobby.name }}{{ index < user.common_hobbies.length - 1 ? ', ' : '' }}
          </span>
        </p>
      </div>
    </div>
    
    <div v-else-if="!loading">
      <p>No users with similar hobbies found.</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

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
      referenceUser: null as string | null,
      filters: {
        min_age: null as number | null,
        max_age: null as number | null,
      },
    };
  },
  methods: {
    async fetchSimilarUsers() {
      this.loading = true;
      try {
        // Construct query parameters for the filters
        const params = new URLSearchParams();
        if (this.filters.min_age !== null) {
          params.append("min_age", this.filters.min_age.toString());
        }
        if (this.filters.max_age !== null) {
          params.append("max_age", this.filters.max_age.toString());
        }

        const response = await fetch(
          `http://127.0.0.1:8000/api/similar-users/?${params.toString()}`,
          {
            method: "GET",
            credentials: "include",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
          }
        );

        const data = await response.json();
        if (response.ok) {
          this.similarUsers = data.similar_users;
          this.referenceUser = data.reference_user;
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
  mounted() {
    this.fetchSimilarUsers();
  },
});
</script>

<style scoped>
.user-card {
  background-color: #f8f9fa;
  transition: transform 0.2s;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.alert {
  padding: 0.75rem 1.25rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
}

.alert-info {
  color: #0c5460;
  background-color: #d1ecf1;
  border-color: #bee5eb;
}
</style>