<template>
  <div class="auth-view container container-narrow">
    <div class="glass-card auth-card">
      <div class="auth-header text-center">
        <h2>Create FreshCatch AI Account</h2>
        <p class="subtitle">Create an account to save scans and manage your FreshCatch profile</p>
      </div>

      <div v-if="errorMessage" class="error-alert">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>Full Name</label>
          <input 
            v-model="name" 
            type="text" 
            class="input-field" 
            placeholder="e.g. Maria Santos" 
            required 
          />
        </div>

        <div class="form-group">
          <label>Email Address</label>
          <input 
            v-model="email" 
            type="email" 
            class="input-field" 
            placeholder="e.g. maria@example.com" 
            required 
          />
        </div>

        <div class="form-group">
          <label>Password (min 6 characters)</label>
          <PasswordInput
            v-model="password"
            placeholder="••••••••"
            autocomplete="new-password"
            required
            minlength="6"
          />
        </div>

        <button type="submit" class="btn btn-primary btn-lg w-full" :disabled="isLoading">
          <span v-if="isLoading">Creating account...</span>
          <span v-else>Register Account</span>
        </button>
      </form>

      <div class="auth-footer text-center">
        <span>Already have an account? </span>
        <router-link to="/login" class="text-cyan font-bold">Sign In</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import PasswordInput from '../../components/common/PasswordInput.vue';

const router = useRouter();
const authStore = useAuthStore();

const name = ref('');
const email = ref('');
const password = ref('');
const isLoading = ref(false);
const errorMessage = ref('');

async function handleRegister() {
  isLoading.value = true;
  errorMessage.value = '';

  const res = await authStore.register(name.value, email.value, password.value);
  isLoading.value = false;

  if (res.success) {
    router.push('/dashboard');
  } else {
    errorMessage.value = res.message || 'Registration failed';
  }
}
</script>

<style scoped>
.auth-view {
  padding: 4rem 1.25rem;
}

.auth-card {
  max-width: 480px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
}

.auth-header h2 {
  font-size: 1.8rem;
  margin-bottom: 0.35rem;
}

.auth-header .subtitle {
  color: var(--text-muted);
  font-size: 0.88rem;
  margin-bottom: 1.5rem;
}

.error-alert {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  margin-bottom: 1.25rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-group label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-white);
  margin-bottom: 0.35rem;
}

.w-full { width: 100%; }

.auth-footer {
  margin-top: 1.5rem;
  font-size: 0.88rem;
  color: var(--text-muted);
}

.text-cyan { color: var(--primary); }
</style>
