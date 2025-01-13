import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    isAuthenticated: false, // Tracks user authentication status
  }),
  actions: {
    async login() {
      // Simulate login or add your backend API call here
      this.isAuthenticated = true;
    },
    async logout() {
      // Simulate logout or add your backend API call here
      this.isAuthenticated = false;
    },
    async checkAuth() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/auth-status/', {
          credentials: 'include', // Include cookies for session-based auth
        });
        const data = await response.json();
        this.isAuthenticated = data.isAuthenticated;
      } catch (error) {
        this.isAuthenticated = false;
      }
    },    
  },
});
