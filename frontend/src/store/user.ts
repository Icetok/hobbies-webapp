import { defineStore } from 'pinia';

interface UserProfile {
  name: string;
  email: string;
  date_of_birth: string;
  hobbies: Array<{ id: number; name: string }>;
}

export const useUserStore = defineStore('user', {
  state: () => ({
    isAuthenticated: false,
    username: '',
    profile: null as UserProfile | null,
  }),
  actions: {
    login(username: string) {
      this.isAuthenticated = true;
      this.username = username;
    },
    logout() {
      this.isAuthenticated = false;
      this.username = '';
      this.profile = null;
    },
    setProfile(profile: UserProfile) {
      this.profile = profile;
    },
    async checkAuth() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/auth-status/', {
          credentials: 'include',
        });
        const data = await response.json();
        this.isAuthenticated = data.isAuthenticated;
        if (data.isAuthenticated) {
          this.username = data.username;
        }
      } catch (error) {
        this.isAuthenticated = false;
        this.username = '';
        this.profile = null;
      }
    },
  },
});
