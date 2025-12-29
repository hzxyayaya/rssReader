// 路由配置
// 定义应用的路由规则

import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import Login from '../views/Login.vue'
import { isAuthenticated } from '../api/auth'

// 路由配置
const routes = [
    {
        path: '/',
        name: 'home',
        component: AppLayout,
        meta: {
            title: 'RSS 阅读器',
            requiresAuth: true
        }
    },
    {
        path: '/login',
        name: 'login',
        component: Login,
        meta: {
            title: '登录'
        }
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('../views/Register.vue'),
        meta: {
            title: '注册'
        }
    }
]

// 创建路由实例
const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    document.title = to.meta.title || 'RSS 阅读器'

    if (to.meta.requiresAuth && !isAuthenticated()) {
        next('/login')
    } else if (to.path === '/login' && isAuthenticated()) {
        next('/')
    } else {
        next()
    }
})

export default router
