// UI 状态管理
// 管理主题、字体大小、行高、布局状态等 UI 相关设置

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

// 主题枚举
export const THEMES = {
    LIGHT: 'light',
    DARK: 'dark',
    SEPIA: 'sepia'
}

// 字体大小预设
export const FONT_SIZES = {
    SMALL: 16,
    MEDIUM: 18,
    LARGE: 20,
    XLARGE: 22
}

// 行高预设
export const LINE_HEIGHTS = {
    COMPACT: 1.6,
    NORMAL: 1.8,
    RELAXED: 2.0
}

export const useUiStore = defineStore('ui', () => {
    // ==================== 状态 ====================

    // 当前主题
    const theme = ref(THEMES.LIGHT)

    // 阅读字体大小（像素）
    const fontSize = ref(FONT_SIZES.MEDIUM)

    // 阅读行高
    const lineHeight = ref(LINE_HEIGHTS.NORMAL)

    // 左侧边栏是否折叠
    const isLeftSidebarCollapsed = ref(false)

    // 中间列是否折叠（阅读模式）
    const isMiddleColumnCollapsed = ref(false)

    // 设置面板是否打开
    const isSettingsPanelOpen = ref(false)

    // 是否处于沉浸式阅读模式
    const isImmersiveMode = ref(false)

    // AI 问答面板是否打开
    const isAiPanelOpen = ref(false)

    // 当前 AI 对话会话 ID
    const sessionId = ref(null)

    // ==================== 计算属性 ====================

    // 主题 CSS 类名
    const themeClass = computed(() => {
        return `theme-${theme.value}`
    })

    // 阅读区域的 CSS 样式
    const readingStyles = computed(() => ({
        fontSize: `${fontSize.value}px`,
        lineHeight: lineHeight.value
    }))

    // 主题显示名称
    const themeDisplayName = computed(() => {
        const names = {
            [THEMES.LIGHT]: '浅色',
            [THEMES.DARK]: '深色',
            [THEMES.SEPIA]: '护眼'
        }
        return names[theme.value] || '浅色'
    })

    // ==================== 方法 ====================

    /**
     * 设置主题
     * @param {string} newTheme - 新主题
     */
    function setTheme(newTheme) {
        if (Object.values(THEMES).includes(newTheme)) {
            theme.value = newTheme
            // 保存到本地存储
            localStorage.setItem('rss-reader-theme', newTheme)
            // 更新 document 的类名
            updateDocumentTheme()
        }
    }

    /**
     * 循环切换主题
     */
    function cycleTheme() {
        const themes = Object.values(THEMES)
        const currentIndex = themes.indexOf(theme.value)
        const nextIndex = (currentIndex + 1) % themes.length
        setTheme(themes[nextIndex])
    }

    /**
     * 更新 document 的主题类名
     */
    function updateDocumentTheme() {
        // 移除所有主题类
        document.documentElement.classList.remove('theme-light', 'theme-dark', 'theme-sepia')
        // 添加当前主题类
        document.documentElement.classList.add(`theme-${theme.value}`)
    }

    /**
     * 设置字体大小
     * @param {number} size - 字体大小（像素）
     */
    function setFontSize(size) {
        fontSize.value = size
        // 更新 CSS 变量
        document.documentElement.style.setProperty('--font-size-reading', `${size}px`)
        // 保存到本地存储
        localStorage.setItem('rss-reader-font-size', size.toString())
    }

    /**
     * 设置行高
     * @param {number} height - 行高
     */
    function setLineHeight(height) {
        lineHeight.value = height
        // 更新 CSS 变量
        document.documentElement.style.setProperty('--line-height-reading', height.toString())
        // 保存到本地存储
        localStorage.setItem('rss-reader-line-height', height.toString())
    }

    /**
     * 切换左侧边栏折叠状态
     */
    function toggleLeftSidebar() {
        isLeftSidebarCollapsed.value = !isLeftSidebarCollapsed.value
    }

    /**
     * 切换中间列折叠状态
     */
    function toggleMiddleColumn() {
        isMiddleColumnCollapsed.value = !isMiddleColumnCollapsed.value
    }

    /**
     * 进入沉浸式阅读模式
     */
    function enterImmersiveMode() {
        isImmersiveMode.value = true
        isLeftSidebarCollapsed.value = true
        isMiddleColumnCollapsed.value = true
    }

    /**
     * 退出沉浸式阅读模式
     */
    function exitImmersiveMode() {
        isImmersiveMode.value = false
        isLeftSidebarCollapsed.value = false
        isMiddleColumnCollapsed.value = false
    }

    /**
     * 切换沉浸式阅读模式
     */
    function toggleImmersiveMode() {
        if (isImmersiveMode.value) {
            exitImmersiveMode()
        } else {
            enterImmersiveMode()
        }
    }

    function toggleAiPanel() {
        isAiPanelOpen.value = !isAiPanelOpen.value
    }

    function setSessionId(id) {
        sessionId.value = id
    }

    /**
     * 打开设置面板
     */
    function openSettingsPanel() {
        isSettingsPanelOpen.value = true
    }

    /**
     * 关闭设置面板
     */
    function closeSettingsPanel() {
        isSettingsPanelOpen.value = false
    }

    /**
     * 切换设置面板
     */
    function toggleSettingsPanel() {
        isSettingsPanelOpen.value = !isSettingsPanelOpen.value
    }

    /**
     * 从本地存储初始化设置
     */
    function initFromStorage() {
        // 恢复主题
        const savedTheme = localStorage.getItem('rss-reader-theme')
        if (savedTheme && Object.values(THEMES).includes(savedTheme)) {
            theme.value = savedTheme
        }

        // 恢复字体大小
        const savedFontSize = localStorage.getItem('rss-reader-font-size')
        if (savedFontSize) {
            fontSize.value = parseInt(savedFontSize, 10)
        }

        // 恢复行高
        const savedLineHeight = localStorage.getItem('rss-reader-line-height')
        if (savedLineHeight) {
            lineHeight.value = parseFloat(savedLineHeight)
        }

        // 应用设置
        updateDocumentTheme()
        setFontSize(fontSize.value)
        setLineHeight(lineHeight.value)
    }

    return {
        // 状态
        theme,
        fontSize,
        lineHeight,
        isLeftSidebarCollapsed,
        isMiddleColumnCollapsed,
        isSettingsPanelOpen,
        isImmersiveMode,
        isAiPanelOpen,
        sessionId,

        // 计算属性
        themeClass,
        readingStyles,
        themeDisplayName,

        // 方法
        setTheme,
        cycleTheme,
        setFontSize,
        setLineHeight,
        toggleLeftSidebar,
        toggleMiddleColumn,
        enterImmersiveMode,
        exitImmersiveMode,
        toggleImmersiveMode,
        openSettingsPanel,
        closeSettingsPanel,
        toggleSettingsPanel,
        initFromStorage,
        toggleAiPanel,
        setSessionId
    }
})
