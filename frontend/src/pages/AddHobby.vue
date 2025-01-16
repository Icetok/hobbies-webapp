<template>
    <div class="h3">
        <h2>Add Hobby</h2>
        <form @submit.prevent="addHobby">
          <input v-model="formData.hobby" placeholder="Hobby" required />
          <button type="submit">Add Hobby</button>
        </form>
    </div>
  </template>
  
  <script lang="ts">
import { defineComponent } from "vue";
      export default defineComponent({
          data() {
              return {
                  title: "Hobbies",
                  formData: {
                    hobby: ""
                  }
              }
          },
          methods: {
            async addHobby() {
                const response = await fetch('http://127.0.0.1:8000/api/hobbies/', {
                    method: 'POST',
                    headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify(this.formData),
                });

                if (response.ok) {
                    this.formData.hobby = "";
                    alert('Hobby Added Successfully!');
                } else {
                    const errorData = await response.json();
                    alert(`Adding hobby failed: ${JSON.stringify(errorData.errors)}`);
                }
            },
          }
      })
  </script>
  
  <style scoped>
  </style>
  