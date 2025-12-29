<script setup>
/**
 * 根组件
 * 负责初始化主题和渲染路由视图
 */
import { onMounted } from 'vue'
import { useTheme } from './composables/useTheme'
import { useKeyboardNavigation } from './composables/useKeyboardNavigation'

import { useUserStore } from './stores/userStore'

// 初始化主题
const { initTheme } = useTheme()

// 初始化用户状态
const userStore = useUserStore()

// 初始化键盘导航
useKeyboardNavigation()

// 组件挂载时初始化
onMounted(() => {
  initTheme()
  userStore.init() // 恢复登录状态
})
</script>

<template>
  <!-- 路由视图 -->
  <router-view />
</template>
