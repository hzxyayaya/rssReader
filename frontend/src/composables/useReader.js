// 阅读逻辑 Composable
// 封装阅读进度、自动隐藏侧边栏等逻辑

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useEntryStore } from '../stores/entryStore'
import { useUiStore } from '../stores/uiStore'

/**
 * 阅读逻辑 Composable
 * 管理阅读进度、自动隐藏侧边栏等功能
 */
export function useReader() {
    const entryStore = useEntryStore()
    const uiStore = useUiStore()

    // ==================== 状态 ====================

    // 阅读区域元素引用
    const readerRef = ref(null)

    // 阅读进度（0-100）
    const readingProgress = ref(0)

    // 是否正在滚动
    const isScrolling = ref(false)

    // 滚动定时器
    let scrollTimer = null

    // ==================== 计算属性 ====================

    // 当前正在阅读的文章
    const currentArticle = computed(() => entryStore.currentEntry)

    // 是否有文章正在阅读
    const isReading = computed(() => !!currentArticle.value)

    // 阅读字体样式
    const readingStyles = computed(() => uiStore.readingStyles)

    // ==================== 方法 ====================

    /**
     * 更新阅读进度
     * 根据滚动位置计算当前阅读进度
     */
    function updateProgress() {
        if (!readerRef.value) return

        const element = readerRef.value
        const scrollTop = element.scrollTop
        const scrollHeight = element.scrollHeight - element.clientHeight

        if (scrollHeight > 0) {
            readingProgress.value = Math.min(100, Math.round((scrollTop / scrollHeight) * 100))
        } else {
            readingProgress.value = 100 // 内容不足以滚动时，视为已读完
        }
    }

    /**
     * 处理滚动事件
     */
    function handleScroll() {
        updateProgress()

        // 标记正在滚动
        isScrolling.value = true

        // 滚动停止后一段时间，标记滚动结束
        if (scrollTimer) {
            clearTimeout(scrollTimer)
        }

        scrollTimer = setTimeout(() => {
            isScrolling.value = false
        }, 150)
    }

    /**
     * 向下滚动一屏
     */
    function scrollDown() {
        if (!readerRef.value) return

        const element = readerRef.value
        const scrollAmount = element.clientHeight * 0.8 // 滚动 80% 屏幕高度

        element.scrollBy({
            top: scrollAmount,
            behavior: 'smooth'
        })
    }

    /**
     * 向上滚动一屏
     */
    function scrollUp() {
        if (!readerRef.value) return

        const element = readerRef.value
        const scrollAmount = element.clientHeight * 0.8

        element.scrollBy({
            top: -scrollAmount,
            behavior: 'smooth'
        })
    }

    /**
     * 滚动到顶部
     */
    function scrollToTop() {
        if (!readerRef.value) return

        readerRef.value.scrollTo({
            top: 0,
            behavior: 'smooth'
        })
    }

    /**
     * 滚动到底部
     */
    function scrollToBottom() {
        if (!readerRef.value) return

        const element = readerRef.value
        element.scrollTo({
            top: element.scrollHeight,
            behavior: 'smooth'
        })
    }

    /**
     * 设置阅读区域元素引用
     * @param {HTMLElement} el - DOM 元素
     */
    function setReaderRef(el) {
        readerRef.value = el

        if (el) {
            // 添加滚动事件监听
            el.addEventListener('scroll', handleScroll, { passive: true })
            // 初始化进度
            updateProgress()
        }
    }

    /**
     * 清理滚动事件监听
     */
    function cleanup() {
        if (readerRef.value) {
            readerRef.value.removeEventListener('scroll', handleScroll)
        }
        if (scrollTimer) {
            clearTimeout(scrollTimer)
        }
    }

    /**
     * 进入沉浸式阅读模式
     */
    function enterImmersiveMode() {
        uiStore.enterImmersiveMode()
    }

    /**
     * 退出沉浸式阅读模式（退出阅读）
     */
    function exitReading() {
        uiStore.exitImmersiveMode()
        entryStore.clearCurrentEntry()
        readingProgress.value = 0
    }

    /**
     * 切换沉浸式模式
     */
    function toggleImmersiveMode() {
        uiStore.toggleImmersiveMode()
    }

    // 监听当前文章变化，重置进度
    watch(() => entryStore.currentEntryId, () => {
        readingProgress.value = 0
        // 滚动到顶部
        if (readerRef.value) {
            readerRef.value.scrollTop = 0
        }
    })

    return {
        // 状态
        readerRef,
        readingProgress,
        isScrolling,

        // 计算属性
        currentArticle,
        isReading,
        readingStyles,

        // 方法
        setReaderRef,
        updateProgress,
        scrollDown,
        scrollUp,
        scrollToTop,
        scrollToBottom,
        enterImmersiveMode,
        exitReading,
        toggleImmersiveMode,
        cleanup
    }
}
