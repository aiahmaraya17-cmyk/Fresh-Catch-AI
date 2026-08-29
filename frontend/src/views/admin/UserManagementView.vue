<template>
  <div class="users-admin-view container">
    <div class="page-header">
      <span class="badge badge-cyan">Access Control & RBAC</span>
      <h1>User & Role Management</h1>
      <p class="subtitle">Manage user permissions across Consumer, Vendor, Admin, and Researcher roles</p>
    </div>

    <div class="glass-card table-card">
      <table class="users-table">
        <thead>
          <tr>
            <th>User</th>
            <th>Email</th>
            <th>Current Role</th>
            <th>Joined Date</th>
            <th>Change Role</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>
              <div class="user-row-info">
                <div class="mini-avatar">{{ u.name.charAt(0) }}</div>
                <strong>{{ u.name }}</strong>
              </div>
            </td>
            <td class="text-dim">{{ u.email }}</td>
            <td>
              <span class="badge" :class="getRoleBadge(u.role)">{{ u.role.toUpperCase() }}</span>
            </td>
            <td class="text-dim">{{ formatDate(u.created_at) }}</td>
            <td>
              <select :value="u.role" @change="updateRole(u.id, $event.target.value)" class="input-field select-role">
                <option value="consumer">Consumer</option>
                <option value="vendor">Vendor</option>
                <option value="researcher">Researcher</option>
                <option value="admin">Administrator</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '../../services/api';

const users = ref([]);

function formatDate(dStr) {
  if (!dStr) return '';
  return new Date(dStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function getRoleBadge(role) {
  if (role === 'admin') return 'badge-not-fresh';
  if (role === 'researcher') return 'badge-cyan';
  if (role === 'vendor') return 'badge-moderate';
  return 'badge-fresh';
}

async function loadUsers() {
  try {
    const res = await ApiService.listUsers();
    if (res.success) {
      users.value = res.users || [];
    }
  } catch (e) {
    console.error('Failed to load users:', e);
  }
}

async function updateRole(userId, newRole) {
  try {
    const res = await ApiService.updateUserRole(userId, newRole);
    if (res.success) {
      await loadUsers();
    }
  } catch (e) {
    alert('Failed to update role: ' + e.message);
  }
}

onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.users-admin-view {
  padding: 3rem 1.25rem;
}

.page-header {
  margin-bottom: 2.5rem;
}

.table-card {
  padding: 1.75rem;
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  text-align: left;
}

.users-table th {
  padding: 0.75rem 1rem;
  color: var(--text-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-glass);
}

.users-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  vertical-align: middle;
}

.user-row-info {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.mini-avatar {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--primary), var(--accent-teal));
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 700;
}

.select-role {
  padding: 0.35rem 0.6rem;
  font-size: 0.82rem;
  width: auto;
}
</style>
