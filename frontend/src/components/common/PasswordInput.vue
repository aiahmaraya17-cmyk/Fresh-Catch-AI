<!--
  PasswordInput.vue
  -----------------
  A password field with a show/hide (eye) toggle. Wraps the standard
  .input-field styling and adds a button that switches the input between
  type="password" and type="text" so users can verify what they typed.

  Usage:
    <PasswordInput v-model="password" placeholder="••••••••" required />
  Any extra attributes (autocomplete, minlength, etc.) fall through to <input>.
-->
<template>
  <div class="password-field">
    <input
      :type="visible ? 'text' : 'password'"
      class="input-field"
      :value="modelValue"
      :placeholder="placeholder"
      v-bind="$attrs"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <button
      type="button"
      class="toggle-btn"
      :aria-label="visible ? 'Hide password' : 'Show password'"
      :title="visible ? 'Hide password' : 'Show password'"
      @click="visible = !visible"
    >
      <!-- Eye (visible) -->
      <svg v-if="visible" width="20" height="20" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
      <!-- Eye off (hidden) -->
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-6.5 0-10-8-10-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c6.5 0 10 8 10 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
        <line x1="2" y1="2" x2="22" y2="22"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineOptions({ inheritAttrs: false });

defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '••••••••' },
});
defineEmits(['update:modelValue']);

const visible = ref(false);
</script>

<style scoped>
.password-field {
  position: relative;
  width: 100%;
}
/* Leave room for the toggle button so long passwords don't sit under it. */
.password-field .input-field {
  width: 100%;
  padding-right: 2.75rem;
}
.toggle-btn {
  position: absolute;
  top: 50%;
  right: 0.6rem;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-muted, #90a4b8);
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;
}
.toggle-btn:hover {
  color: var(--accent-teal, #14b8a6);
  background: rgba(20, 184, 166, 0.1);
}
.toggle-btn:focus-visible {
  outline: 2px solid var(--accent-teal, #14b8a6);
  outline-offset: 1px;
}
</style>
