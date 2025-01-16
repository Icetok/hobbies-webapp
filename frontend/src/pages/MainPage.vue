<template>
  <div v-if="isAuthenticated">
    <h2>User Profile</h2>
    <div v-if="loading">Loading...</div>

    <div v-else>
      <p><strong>Name:</strong> {{ userProfile.name }}</p>
      <p><strong>Email:</strong> {{ userProfile.email }}</p>
      <p><strong>Date of Birth:</strong> {{ formattedDateOfBirth }}</p>

      <div v-if="userProfile.hobbies.length > 0">
        <strong>Hobbies:</strong>
        <ul>
          <li v-for="hobby in userProfile.hobbies" :key="hobby.id">{{ hobby.name }}</li>
        </ul>
      </div>
      <div v-else>
        <p>No hobbies found.</p>
      </div>

      <button @click="openEditModal">Edit Profile</button>
    </div>

    <!-- Modal for editing profile -->
    <div v-if="isEditModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeEditModal">&times;</span>
        <h3>Edit Profile</h3>
        <form @submit.prevent="submitEditProfile">
          <div>
            <label for="name">Name:</label>
            <input type="text" id="name" v-model="editedProfile.name" required />
          </div>

          <div>
            <label for="email">Email:</label>
            <input type="email" id="email" v-model="editedProfile.email" required />
          </div>

          <div>
            <label for="dob">Date of Birth:</label>
            <input type="date" id="dob" v-model="editedProfile.date_of_birth" required />
          </div>

          <!-- Available Hobbies -->
          <div>
            <label for="hobbies">Hobbies:</label>
            <select id="hobbies" v-model="editedProfile.hobbies" multiple>
              <option v-for="hobby in availableHobbies" :key="hobby.id" :value="hobby.id">
                {{ hobby.name }}
              </option>
            </select>
            <small>Select multiple hobbies by holding down Ctrl (Windows) or Command (Mac).</small>
          </div>

          <!-- Change Password Section -->
          <hr />
          <h4>Change Password</h4>
          <div>
            <label for="current-password">Current Password:</label>
            <input
              type="password"
              id="current-password"
              v-model="passwordData.current_password"
              placeholder="Enter current password"
            />
          </div>
          <div>
            <label for="new-password">New Password:</label>
            <input
              type="password"
              id="new-password"
              v-model="passwordData.new_password"
              placeholder="Enter new password"
            />
          </div>
          <div>
            <label for="confirm-password">Confirm Password:</label>
            <input
              type="password"
              id="confirm-password"
              v-model="passwordData.confirm_password"
              placeholder="Confirm new password"
            />
          </div>

          <div>
            <button type="button" @click="submitChangePassword">Change Password</button>
          </div>

          <div>
            <button type="submit">Save Changes</button>
            <button type="button" @click="closeEditModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <div v-else>
    <p>Please log in to view your profile.</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";

export default defineComponent({
  setup() {
    const userStore = useUserStore();
    const router = useRouter();

    // Ref for managing modal state
    const isEditModalOpen = ref(false);
    const availableHobbies = ref([]); // Store available hobbies

    return {
      userStore,
      router,
      isEditModalOpen,
      availableHobbies,
    };
  },
  computed: {
    isAuthenticated() {
      return this.userStore.isAuthenticated;
    },
    userProfile() {
      return this.userStore.profile;
    },
    formattedDateOfBirth() {
      if (!this.userProfile?.date_of_birth) return "";
      const date = new Date(this.userProfile.date_of_birth);
      return date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    },
  },
  data() {
    return {
      loading: true,
      editedProfile: {
        name: "",
        email: "",
        date_of_birth: "",
        hobbies: [],
      },
      passwordData: {
        current_password: "",
        new_password: "",
        confirm_password: "",
      },
    };
  },
  mounted() {
    if (!this.isAuthenticated) {
      this.router.push("/login");
    } else {
      this.loadProfile();
      this.loadAvailableHobbies(); // Load available hobbies
      this.loading = false;
    }
  },
  methods: {
    async loadProfile() {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/user-profile/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          credentials: "include",
        });

        const data = await response.json();
        if (response.ok) {
          this.userStore.setProfile(data);
          this.editedProfile = {
            name: data.name,
            email: data.email,
            date_of_birth: data.date_of_birth,
            hobbies: data.hobbies.map((hobby) => hobby.id), // Populate hobby IDs
          };
        } else {
          console.error("Fetching profile failed:", data.error);
        }
      } catch (error) {
        console.error("Fetching profile error:", error);
      }
    },
    async loadAvailableHobbies() {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/hobbies/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          credentials: "include",
        });

        const data = await response.json();
        if (response.ok) {
          this.availableHobbies = data.hobbies || data; // Set the available hobbies
        } else {
          console.error("Fetching available hobbies failed:", data.error);
        }
      } catch (error) {
        console.error("Fetching hobbies error:", error);
      }
    },
    openEditModal() {
      this.isEditModalOpen = true; // Open the modal
    },
    closeEditModal() {
      this.isEditModalOpen = false; // Close the modal
    },
    async submitEditProfile() {
      try {
        const updatedData = { ...this.editedProfile };

        const response = await fetch("http://127.0.0.1:8000/api/update-profile/", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.userStore.token}`, // Add token if needed
          },
          body: JSON.stringify(updatedData),
          credentials: "include",
        });

        const data = await response.json();
        if (response.ok) {
          this.userStore.setProfile(data); // Update the store with the new data
          this.closeEditModal(); // Close the modal after successful update
        } else {
          console.error("Error updating profile:", data.error);
        }
      } catch (error) {
        console.error("Error updating profile:", error);
      }
    },
    async submitChangePassword() {
      if (
        !this.passwordData.current_password ||
        !this.passwordData.new_password ||
        !this.passwordData.confirm_password
      ) {
        alert("Please fill in all password fields.");
        return;
      }

      if (this.passwordData.new_password !== this.passwordData.confirm_password) {
        alert("New password and confirmation do not match.");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/api/change-password/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json", 
          },
          body: JSON.stringify({
            current_password: this.passwordData.current_password,
            new_password: this.passwordData.new_password,
          }),
          credentials: "include",
        });

        const data = await response.json();
        if (response.ok) {
          alert("Password successfully changed!");
          this.passwordData = {
            current_password: "",
            new_password: "",
            confirm_password: "",
          }; // Reset the fields
        } else {
          console.error("Error changing password:", data.error);
          alert(data.error || "Failed to change password.");
        }
      } catch (error) {
        console.error("Error changing password:", error);
        alert("An error occurred while changing your password.");
      }
    },
  },
});
</script>

<style scoped>
/* Modal styles */
.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 5px;
  width: 500px;
  text-align: left;
  max-width: 100%;
}

/* Close button */
.close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 24px;
  cursor: pointer;
}

/* Button styles */
button {
  margin-top: 10px;
  padding: 10px;
}

/* Dropdown styling */
select {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fff;
  font-size: 14px;
  cursor: pointer;
  height: auto;
  min-height: 120px; /* Adjust the height for multi-selection */
  box-sizing: border-box; /* Ensure padding doesn't affect width */
}

select option {
  padding: 10px;
}

select:hover {
  border-color: #007bff;
}

small {
  display: block;
  margin-top: 10px;
  font-size: 12px;
  color: #888;
}
</style>