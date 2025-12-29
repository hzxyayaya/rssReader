// 键盘导航 Composable
// 实现键盘快捷键功能

import { onMounted, onUnmounted } from 'vue'
import { useEntryStore } from '../stores/entryStore'
import { useUiStore } from '../stores/uiStore'

/**
 * 键盘导航 Composable
 * 支持以下快捷键：
 * - j: 下一篇文章
 * - k: 上一篇文章
 * - space: 向下滚动
 * - esc: 退出阅读模式
 * - t: 切换主题
 * - f: 进入/退出沉浸式模式
 */
export function useKeyboardNavigation() {
    const entryStore = useEntryStore()
    const uiStore = useUiStore()

    // 阅读区域元素（用于滚动）
    let readerElement = null

    /**
     * 设置阅读区域元素
     * @param {HTMLElement} el - DOM 元素
     */
    function setReaderElement(el) {
        readerElement = el
    }

    /**
     * 向下滚动阅读区域
     */
    function scrollDown() {
        if (!readerElement) {
            // 尝试查找阅读区域元素
            readerElement = document.querySelector('.reader-scroll-area')
        }

        if (readerElement) {
            const scrollAmount = readerElement.clientHeight * 0.7
            readerElement.scrollBy({
                top: scrollAmount,
                behavior: 'smooth'
            })
        }
    }

    /**
     * 向上滚动阅读区域
     */
    function scrollUp() {
        if (!readerElement) {
            readerElement = document.querySelector('.reader-scroll-area')
        }

        if (readerElement) {
            const scrollAmount = readerElement.clientHeight * 0.7
            readerElement.scrollBy({
                top: -scrollAmount,
                behavior: 'smooth'
            })
        }
    }

    /**
     * 键盘事件处理函数
     * @param {KeyboardEvent} event - 键盘事件
     */
    function handleKeyDown(event) {
        // 忽略在输入框中的按键
        const target = event.target
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
            return
        }

        // 处理快捷键
        switch (event.key.toLowerCase()) {
            case 'j':
                // 下一篇文章
                event.preventDefault()
                entryStore.selectNextEntry()
                break

            case 'k':
                // 上一篇文章
                event.preventDefault()
                entryStore.selectPreviousEntry()
                break

            case ' ':
                // 空格键：向下滚动
                // 只有在有当前文章时才处理
                if (entryStore.currentEntry) {
                    event.preventDefault()
                    if (event.shiftKey) {
                        scrollUp()
                    } else {
                        scrollDown()
                    }
                }
                break

            case 'escape':
                // ESC: 退出阅读模式
                event.preventDefault()
                if (uiStore.isSettingsPanelOpen) {
                    // 先关闭设置面板
                    uiStore.closeSettingsPanel()
                } else if (uiStore.isImmersiveMode) {
                    // 退出沉浸式模式
                    uiStore.exitImmersiveMode()
                } else if (entryStore.currentEntry) {
                    // 清除当前文章
                    entryStore.clearCurrentEntry()
                }
                break

            case 't':
                // 切换主题
                event.preventDefault()
                uiStore.cycleTheme()
                break

            case 'f':
                // 进入/退出沉浸式模式
                if (entryStore.currentEntry) {
                    event.preventDefault()
                    uiStore.toggleImmersiveMode()
                }
                break

            case ',':
                // 打开设置面板
                event.preventDefault()
                uiStore.toggleSettingsPanel()
                break

            case 'arrowdown':
                // 下箭头：小幅向下滚动
                if (entryStore.currentEntry) {
                    event.preventDefault()
                    if (readerElement) {
                        readerElement.scrollBy({ top: 100, behavior: 'smooth' })
                    }
                }
                break

            case 'arrowup':
                // 上箭头：小幅向上滚动
                if (entryStore.currentEntry) {
                    event.preventDefault()
                    if (readerElement) {
                        readerElement.scrollBy({ top: -100, behavior: 'smooth' })
                    }
                }
                break
        }
    }

    // 组件挂载时添加事件监听
    onMounted(() => {
        window.addEventListener('keydown', handleKeyDown)
    })

    // 组件卸载时移除事件监听
    onUnmounted(() => {
        window.removeEventListener('keydown', handleKeyDown)
    })

    return {
        setReaderElement,
        scrollDown,
        scrollUp
    }
}
