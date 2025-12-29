// 主题管理 Composable
// 封装主题相关的逻辑

import { computed } from 'vue'
import { useUiStore, THEMES } from '../stores/uiStore'

/**
 * 主题管理 Composable
 * 提供主题切换、初始化等功能
 */
export function useTheme() {
    const uiStore = useUiStore()

    // ==================== 计算属性 ====================

    // 当前主题
    const currentTheme = computed(() => uiStore.theme)

    // 主题 CSS 类名
    const themeClass = computed(() => uiStore.themeClass)

    // 主题显示名称
    const themeDisplayName = computed(() => uiStore.themeDisplayName)

    // 是否为深色主题
    const isDark = computed(() => uiStore.theme === THEMES.DARK)

    // 是否为护眼主题
    const isSepia = computed(() => uiStore.theme === THEMES.SEPIA)

    // ==================== 方法 ====================

    /**
     * 初始化主题
     * 从本地存储恢复用户设置
     */
    function initTheme() {
        uiStore.initFromStorage()
    }

    /**
     * 设置主题
     * @param {string} theme - 主题名称
     */
    function setTheme(theme) {
        uiStore.setTheme(theme)
    }

    /**
     * 循环切换主题
     * 浅色 -> 深色 -> 护眼 -> 浅色
     */
    function cycleTheme() {
        uiStore.cycleTheme()
    }

    /**
     * 设置为浅色主题
     */
    function setLightTheme() {
        uiStore.setTheme(THEMES.LIGHT)
    }

    /**
     * 设置为深色主题
     */
    function setDarkTheme() {
        uiStore.setTheme(THEMES.DARK)
    }

    /**
     * 设置为护眼主题
     */
    function setSepiaTheme() {
        uiStore.setTheme(THEMES.SEPIA)
    }

    return {
        // 常量
        THEMES,

        // 计算属性
        currentTheme,
        themeClass,
        themeDisplayName,
        isDark,
        isSepia,

        // 方法
        initTheme,
        setTheme,
        cycleTheme,
        setLightTheme,
        setDarkTheme,
        setSepiaTheme
    }
}
