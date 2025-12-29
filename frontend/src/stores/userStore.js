import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, fetchUserProfile, logout as apiLogout } from '../api/auth'

export const useUserStore = defineStore('user', () => {
    // ==================== State ====================
    const user = ref(null)
    const token = ref(localStorage.getItem('access_token') || null)
    const isLoading = ref(false)

    // ==================== Computeds ====================
    const isAuthenticated = computed(() => !!token.value)
    const username = computed(() => user.value?.username || 'User')

    // ==================== Actions ====================

    // Login
    async function login(username, password) {
        isLoading.value = true
        try {
            const accessToken = await apiLogin(username, password)
            if (accessToken) {
                token.value = accessToken // apiLogin already sets localStorage, but we sync state
                await fetchUser() // Load profile immediately
                return true
            }
            return false
        } catch (error) {
            throw error
        } finally {
            isLoading.value = false
        }
    }

    // Register
    async function register(username, email, password) {
        isLoading.value = true
        try {
            const res = await apiRegister(username, email, password)
            if (res.access_token) {
                // Auto login after register
                localStorage.setItem('access_token', res.access_token)
                token.value = res.access_token
                await fetchUser()
                return true
            }
            return false
        } catch (error) {
            throw error
        } finally {
            isLoading.value = false
        }
    }

    // Fetch User Profile (Restore Session)
    async function fetchUser() {
        if (!token.value) return

        try {
            const userData = await fetchUserProfile()
            user.value = userData
        } catch (error) {
            console.error('Failed to fetch user profile:', error)
            // If 401, token might be invalid. Logout.
            if (error.status === 401) {
                logout()
            }
        }
    }

    // Logout
    function logout() {
        apiLogout() // Clears localStorage
        token.value = null
        user.value = null
    }

    // Initialize (call this on app start)
    async function init() {
        if (token.value) {
            await fetchUser()
        }
    }

    return {
        user,
        token,
        isLoading,
        isAuthenticated,
        username,
        login,
        register,
        logout,
        fetchUser,
        init
    }
})
