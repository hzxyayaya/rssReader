// 应用入口文件
// 初始化 Vue 3 应用，配置路由和状态管理

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// 创建 Vue 应用实例
const app = createApp(App)

// 创建 Pinia 状态管理实例
const pinia = createPinia()

// 注册插件
app.use(pinia)      // 状态管理
app.use(router)     // 路由

// 挂载应用
app.mount('#app')
