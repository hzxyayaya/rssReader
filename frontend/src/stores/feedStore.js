// 订阅源状态管理
// 管理 RSS 订阅源列表、当前选中的订阅源和未读数量

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchFeeds, addCustomFeed, removeFeed, canRemoveFeed, getAllFeeds } from '../api/rss'

export const useFeedStore = defineStore('feed', () => {
    // ==================== 状态 ====================

    // 订阅源列表
    const feeds = ref([])

    // 当前选中的订阅源 ID（null 表示全部）
    const currentFeedId = ref(null)

    // 加载状态
    const isLoading = ref(false)

    // 错误信息
    const error = ref(null)

    // 是否使用真实 RSS 数据
    const useRealData = ref(true)

    // ==================== 计算属性 ====================

    // 当前选中的订阅源
    const currentFeed = computed(() => {
        if (!currentFeedId.value) return null
        return feeds.value.find(feed => feed.id === currentFeedId.value)
    })

    // 总未读数量
    const totalUnreadCount = computed(() => {
        return feeds.value.reduce((sum, feed) => sum + (feed.unreadCount || 0), 0)
    })

    // 带"全部"选项的订阅源列表（用于显示）
    const feedsWithAll = computed(() => {
        return [
            {
                id: 'all',
                title: '全部文章',
                icon: '📚',
                unreadCount: totalUnreadCount.value
            },
            ...feeds.value
        ]
    })

    // ==================== 方法 ====================

    /**
     * 加载订阅源列表
     */
    async function loadFeeds() {
        isLoading.value = true
        error.value = null

        try {
            const data = await fetchFeeds()
            feeds.value = data

            // 默认选中"全部"
            if (!currentFeedId.value) {
                currentFeedId.value = 'all'
            }
        } catch (e) {
            error.value = e.message || '加载订阅源失败'
            console.error('加载订阅源失败:', e)
        } finally {
            isLoading.value = false
        }
    }

    /**
     * 选择订阅源
     * @param {string} feedId - 订阅源 ID
     */
    function selectFeed(feedId) {
        currentFeedId.value = feedId
    }

    /**
     * 更新订阅源的未读数量
     * @param {string} feedId - 订阅源 ID
     * @param {number} count - 未读数量变化（负数表示减少）
     */
    function updateUnreadCount(feedId, count) {
        const feed = feeds.value.find(f => f.id === feedId)
        if (feed) {
            feed.unreadCount = Math.max(0, (feed.unreadCount || 0) + count)
        }
    }

    /**
     * 设置订阅源的未读数量
     * @param {string} feedId - 订阅源 ID
     * @param {number} count - 未读数量
     */
    function setUnreadCount(feedId, count) {
        const feed = feeds.value.find(f => f.id === feedId)
        if (feed) {
            feed.unreadCount = count
        }
    }

    /**
     * 减少指定订阅源的未读数量（标记已读时调用）
     * @param {string} feedId - 订阅源 ID
     */
    function decrementUnreadCount(feedId) {
        updateUnreadCount(feedId, -1)
    }

    /**
     * 添加新订阅源
     * @param {Object} feedData - 订阅源数据
     */
    async function addFeed(feedData) {
        const newFeed = await addCustomFeed(feedData)
        feeds.value.push({
            ...newFeed,
            unreadCount: 0
        })
        return newFeed
    }

    /**
     * 删除订阅源
     * @param {string} feedId - 订阅源 ID
     */
    async function deleteFeed(feedId) {
        await removeFeed(feedId)
        feeds.value = feeds.value.filter(f => f.id !== feedId)

        // 如果删除的是当前选中的订阅源，切换到全部
        if (currentFeedId.value === feedId) {
            currentFeedId.value = 'all'
        }

        return true
    }

    /**
     * 检查订阅源是否可删除
     * @param {string} feedId - 订阅源 ID
     */
    function isRemovable(feedId) {
        return true // All feeds managed by backend can be deleted
    }

    return {
        // 状态
        feeds,
        currentFeedId,
        isLoading,
        error,

        // 计算属性
        currentFeed,
        totalUnreadCount,
        feedsWithAll,

        // 方法
        loadFeeds,
        selectFeed,
        updateUnreadCount,
        setUnreadCount,
        decrementUnreadCount,
        addFeed,
        deleteFeed,
        isRemovable
    }
})
