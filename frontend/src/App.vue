<template>
  <div class="app-layout">
    <Navbar />
    <main class="main-content">
      <router-view />
    </main>
    <Footer />
    <!-- PWA install / update / offline-ready prompt -->
    <PWAPrompt />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import Navbar    from './components/common/Navbar.vue';
import Footer    from './components/common/Footer.vue';
import PWAPrompt from './components/common/PWAPrompt.vue';
import { useAuthStore } from './stores/authStore';

const authStore = useAuthStore();

onMounted(async () => {
  await authStore.initialize();
});
</script>
