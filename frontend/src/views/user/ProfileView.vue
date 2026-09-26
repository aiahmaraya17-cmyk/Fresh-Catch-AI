<template>
  <div class="profile-view container container-narrow">
    <div class="page-header">
      <h1>User Profile & Settings</h1>
      <p class="subtitle">Manage account details, language, and role preferences</p>
    </div>

    <div class="glass-card profile-card">
      <div class="user-header">
        <div class="user-avatar-lg">
          {{ authStore.userName.charAt(0) }}
        </div>
        <div class="user-main-info">
          <h2>{{ authStore.userName }}</h2>
          <span class="user-email">{{ authStore.user?.email }}</span>
          <div class="role-badge-wrap">
            <span class="badge badge-cyan">{{ authStore.userRole.toUpperCase() }}</span>
          </div>
        </div>
      </div>

      <!-- Success Notification -->
      <div v-if="successMsg" class="success-alert">
        {{ successMsg }}
      </div>

      <!-- Form -->
      <form @submit.prevent="handleUpdate" class="profile-form">
        <div class="form-group">
          <label>Display Name</label>
          <input v-model="name" type="text" class="input-field" required />
        </div>

        <div class="form-group">
          <label>Application Language</label>
          <select v-model="lang" @change="changeLang" class="input-field">
            <option value="en">English (Default)</option>
            <option value="tl">Filipino / Tagalog (Lokal na Wika)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Update Password (Optional)</label>
          <PasswordInput
            v-model="password"
            placeholder="Leave blank to keep current password"
            autocomplete="new-password"
          />
        </div>

        <button type="submit" class="btn btn-primary btn-lg" :disabled="isLoading">
          <span v-if="isLoading">Saving Changes...</span>
          <span v-else>Save Changes</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../../stores/authStore';
import ApiService from '../../services/api';
import PasswordInput from '../../components/common/PasswordInput.vue';

const authStore = useAuthStore();
const name = ref(authStore.userName);
const lang = ref(authStore.language);
const password = ref('');
const isLoading = ref(false);
const successMsg = ref('');

function changeLang() {
  authStore.setLanguage(lang.value);
}

async function handleUpdate() {
  isLoading.value = true;
  successMsg.value = '';
  try {
    const res = await ApiService.updateProfile({
      name: name.value,
      password: password.value || undefined
    });
    if (res.success) {
      authStore.user = res.user;
      successMsg.value = 'Profile updated successfully!';
      password.value = '';
    }
  } catch (err) {
    console.error('Update error:', err);
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  if (authStore.user) {
    name.value = authStore.user.name;
    lang.value = authStore.language;
  }
});
</script>

<style scoped>
.profile-view {
  padding: 3.5rem 1.25rem;
}

.page-header {
  margin-bottom: 2rem;
}

.profile-card {
  padding: 2.5rem;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding-bottom: 1.75rem;
  border-bottom: 1px solid var(--border-glass);
  margin-bottom: 1.75rem;
}

.user-avatar-lg {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--primary), var(--accent-teal));
  color: #fff;
  font-size: 1.8rem;
  font-weight: 800;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-main-info h2 {
  font-size: 1.4rem;
  margin-bottom: 0.2rem;
}

.user-email {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.role-badge-wrap {
  margin-top: 0.4rem;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-white);
  margin-bottom: 0.35rem;
}

.success-alert {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #a7f3d0;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  margin-bottom: 1.25rem;
}
</style>
