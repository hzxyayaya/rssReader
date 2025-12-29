<template>
  <div class="user-profile">
    <div class="info">
      <div class="username">Hi, {{ username }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()
const username = computed(() => userStore.username)
</script>

<style scoped>
.user-profile {
  display: flex;
  align-items: center;
  padding: 0 0.5rem;
}

.username {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text);
}
</style>
