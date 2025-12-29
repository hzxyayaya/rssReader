<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2 class="login-title">创建账号</h2>
        <p class="login-subtitle">加入我们，开始您的智能阅读之旅</p>
      </div>
      
      <form class="login-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            id="username" 
            name="username" 
            type="text" 
            required 
            v-model="username" 
            placeholder="请输入用户名"
          >
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            id="email" 
            name="email" 
            type="email" 
            required 
            v-model="email" 
            placeholder="请输入邮箱"
          >
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password" 
            name="password" 
            type="password" 
            required 
            v-model="password" 
            placeholder="设置密码"
          >
        </div>

        <div v-if="errorMsg" class="error-message">
          {{ errorMsg }}
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? '注册中...' : '立即注册' }}
        </button>

        <div class="form-footer">
          <router-link to="/login" class="link">
            已有账号？去登录
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/auth'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
    isLoading.value = true
    errorMsg.value = ''
    try {
        await register(username.value, email.value, password.value)
        // 注册成功后跳转登录
        router.push('/login')
    } catch (e) {
        if (e.detail) {
             errorMsg.value = e.detail
        } else {
            errorMsg.value = '注册失败，请稍后重试'
        }
    } finally {
        isLoading.value = false
    }
}
</script>

<style scoped>
/* 复用 Login.vue 的样式，保持一致性 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg);
  color: var(--color-text);
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 2.5rem;
  transition: all 0.3s ease;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.5rem;
  letter-spacing: -0.025em;
}

.login-subtitle {
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.form-group input {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  transition: all 0.2s ease;
}

.form-group input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-light);
  outline: none;
}

.submit-btn {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background-color: var(--color-accent);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-top: 1rem;
}

.submit-btn:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  text-align: center;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm);
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.9rem;
}

.link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}
</style>
