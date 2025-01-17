<template>
    <div>
      <h2>Friend Requests</h2>
      <div v-if="loading">Loading...</div>
      <div v-if="!loading && friendRequests.length > 0">
        <div v-for="request in friendRequests" :key="request.id" class="request-card mb-3 p-3 border rounded">
          <p>{{ request.sender.username }} sent you a friend request.</p>
          <button class="btn btn-success me-2" @click="respondToRequest(request.id, 'accept')">
            Accept
          </button>
          <button class="btn btn-danger" @click="respondToRequest(request.id, 'reject')">
            Reject
          </button>
        </div>
      </div>
      <div v-else-if="!loading">
        <p>No pending friend requests.</p>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from "vue";
  
  interface FriendRequest {
    id: number;
    sender: {
      id: number;
      username: string;
    };
  }
  
  export default defineComponent({
    data() {
      return {
        friendRequests: [] as FriendRequest[],
        loading: true,
      };
    },
    methods: {
      async fetchFriendRequests() {
        this.loading = true;
        try {
          const response = await fetch("http://127.0.0.1:8000/api/friend-requests/", {
            method: "GET",
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
          });
          const data = await response.json();
          if (response.ok) {
            this.friendRequests = data.friend_requests;
          } else {
            console.error("Failed to fetch friend requests:", data.error);
          }
        } catch (error) {
          console.error("Error fetching friend requests:", error);
        } finally {
          this.loading = false;
        }
      },
      async respondToRequest(requestId: number, action: "accept" | "reject") {
        try {
          const response = await fetch("http://127.0.0.1:8000/api/friend-requests/respond/", {
            method: "POST",
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ request_id: requestId, action }),
          });
          if (response.ok) {
            this.friendRequests = this.friendRequests.filter((req) => req.id !== requestId);
            alert(`Friend request ${action}ed successfully!`);
          } else {
            const errorData = await response.json();
            alert(`Failed to ${action} friend request: ${errorData.error}`);
          }
        } catch (error) {
          console.error(`Error ${action}ing friend request:`, error);
          alert(`Failed to ${action} friend request. Please try again.`);
        }
      },
    },
    mounted() {
      this.fetchFriendRequests();
    },
  });
  </script>
  
  <style scoped>
  .request-card {
    background-color: #f8f9fa;
    transition: transform 0.2s;
  }
  .request-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  </style>
  