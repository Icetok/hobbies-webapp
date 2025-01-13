import { createApp } from 'vue'
import { createPinia } from 'pinia';
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';
import { useUserStore } from '@/store/user';


const app = createApp(App)

// Create Pinia instance
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Check authentication state on app load
const userStore = useUserStore();
userStore.checkAuth();

app.mount('#app')
