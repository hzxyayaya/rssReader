// 文章状态管理
// 管理文章列表、当前文章、已读状态和收藏状态
// 修改：只有切换到其他文章时才标记为已读

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchNews, fetchArticle, fetchReadStatus, markAsRead as apiMarkAsRead } from '../api/news'
import { useFeedStore } from './feedStore'

export const useEntryStore = defineStore('entry', () => {
    // ==================== 状态 ====================

    // 文章列表
    const entries = ref([])

    // 当前选中的文章 ID
    const currentEntryId = ref(null)

    // 当前订阅源内已查看的文章 ID 列表（用于切换订阅源时批量标记已读）
    const viewedEntryIds = ref(new Set())

    // 加载状态
    const isLoading = ref(false)

    // 错误信息
    const error = ref(null)

    // ==================== 计算属性 ====================

    // 当前选中的文章
    const currentEntry = computed(() => {
        if (!currentEntryId.value) return null
        return entries.value.find(entry => entry.id === currentEntryId.value)
    })

    // 未读文章列表
    const unreadEntries = computed(() => {
        return entries.value.filter(entry => !entry.isRead)
    })

    // 已读文章列表
    const readEntries = computed(() => {
        return entries.value.filter(entry => entry.isRead)
    })

    // 排序后的文章列表（未读优先，然后按时间倒序）
    const sortedEntries = computed(() => {
        return [...entries.value].sort((a, b) => {
            // 未读文章优先
            if (a.isRead !== b.isRead) {
                return a.isRead ? 1 : -1
            }
            // 按发布时间倒序
            return new Date(b.publishedAt) - new Date(a.publishedAt)
        })
    })

    // 当前文章在列表中的索引
    const currentEntryIndex = computed(() => {
        if (!currentEntryId.value) return -1
        return sortedEntries.value.findIndex(entry => entry.id === currentEntryId.value)
    })

    // 是否有上一篇文章
    const hasPreviousEntry = computed(() => {
        return currentEntryIndex.value > 0
    })

    // 是否有下一篇文章
    const hasNextEntry = computed(() => {
        return currentEntryIndex.value < sortedEntries.value.length - 1
    })

    // ==================== 方法 ====================

    /**
     * 加载文章列表
     * @param {string} feedId - 订阅源 ID
     */
    async function loadEntries(feedId) {
        isLoading.value = true
        error.value = null

        const feedStore = useFeedStore()

        try {
            const data = await fetchNews({
                feedId: feedId,
                limit: 100
            })

            // Map backend fields to frontend format
            entries.value = data.map(item => ({
                id: item.id,
                feedId: item.feed_id,
                title: item.title,
                author: item.author || '',
                summary: item.description || '',
                content: item.content || '',
                publishedAt: item.published_at || new Date().toISOString(),
                link: item.url || '',
                isRead: false,
                isFavorite: false
            }))

            // Fetch read status from backend and apply
            try {
                const readIds = await fetchReadStatus()
                const readSet = new Set(readIds)
                entries.value.forEach(entry => {
                    if (readSet.has(entry.id)) {
                        entry.isRead = true
                    }
                })
            } catch (e) {
                console.warn('Failed to fetch read status:', e)
            }

            // 更新未读数量
            if (feedId === 'all') {
                const unreadByFeed = {}
                entries.value.forEach(entry => {
                    if (!entry.isRead) {
                        unreadByFeed[entry.feedId] = (unreadByFeed[entry.feedId] || 0) + 1
                    }
                })
                feedStore.feeds.forEach(feed => {
                    feedStore.setUnreadCount(feed.id, unreadByFeed[feed.id] || 0)
                })
            } else {
                const unreadCount = entries.value.filter(e => !e.isRead).length
                feedStore.setUnreadCount(feedId, unreadCount)
            }
        } catch (e) {
            error.value = e.message || '加载文章失败'
            console.error('加载文章失败:', e)
        } finally {
            isLoading.value = false
        }
    }

    /**
     * 选择文章
     * @param {string} entryId - 文章 ID
     */
    function selectEntry(entryId) {
        // 更新当前选中的文章
        currentEntryId.value = entryId

        // 立即标记为已读
        markAsRead(entryId)

        // 异步加载完整内容
        loadFullContent(entryId)
    }

    /**
     * 加载文章完整内容
     * @param {string} entryId 
     */
    async function loadFullContent(entryId) {
        const entry = entries.value.find(e => e.id === entryId)
        // 如果没有内容或者已经标记为有了完整内容，则跳过
        if (!entry || (entry.content && entry.hasFullContent)) return

        try {
            const data = await fetchArticle(entryId)
            if (data && data.content) {
                entry.content = data.content
                entry.hasFullContent = true
            }
        } catch (e) {
            console.error('加载文章详情失败:', e)
        }
    }

    /**
     * 标记文章为已读
     * @param {string} entryId - 文章 ID
     */
    async function markAsRead(entryId) {
        const entry = entries.value.find(e => e.id === entryId)
        if (!entry || entry.isRead) return

        // 更新本地状态
        entry.isRead = true

        // 更新订阅源的未读数量
        const feedStore = useFeedStore()
        feedStore.decrementUnreadCount(entry.feedId)

        try {
            await apiMarkAsRead(entryId)
        } catch (e) {
            // 回滚
            entry.isRead = false
            feedStore.updateUnreadCount(entry.feedId, 1)
            console.error('标记已读失败:', e)
        }
    }

    /**
     * 切换收藏状态
     * @param {string} entryId - 文章 ID
     */
    function toggleFavorite(entryId) {
        const entry = entries.value.find(e => e.id === entryId)
        if (entry) {
            entry.isFavorite = !entry.isFavorite
        }
    }

    /**
     * 选择上一篇文章
     */
    function selectPreviousEntry() {
        if (!hasPreviousEntry.value) return
        const previousEntry = sortedEntries.value[currentEntryIndex.value - 1]
        selectEntry(previousEntry.id)
    }

    /**
     * 选择下一篇文章
     */
    function selectNextEntry() {
        if (!hasNextEntry.value) return
        const nextEntry = sortedEntries.value[currentEntryIndex.value + 1]
        selectEntry(nextEntry.id)
    }

    /**
     * 切换订阅源时调用
     * 标记所有已查看的文章为已读，并清除状态
     */
    function clearCurrentEntry() {
        // 标记所有已查看的文章为已读
        viewedEntryIds.value.forEach(entryId => {
            markAsRead(entryId)
        })

        // 清除已查看列表
        viewedEntryIds.value.clear()
        // 清除当前选中
        currentEntryId.value = null
    }

    return {
        // 状态
        entries,
        currentEntryId,
        viewedEntryIds,
        isLoading,
        error,

        // 计算属性
        currentEntry,
        unreadEntries,
        readEntries,
        sortedEntries,
        currentEntryIndex,
        hasPreviousEntry,
        hasNextEntry,

        // 方法
        loadEntries,
        selectEntry,
        markAsRead,
        toggleFavorite,
        selectPreviousEntry,
        selectNextEntry,
        clearCurrentEntry
    }
})
