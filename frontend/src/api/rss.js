import http from './http'

// 获取所有订阅源
export async function fetchFeeds(useRealData = true) {
    // ignore useRealData as we use backend
    return http.get('/feeds/')
}

// 添加订阅源
export async function addCustomFeed(feedData) {
    return http.post('/feeds/', feedData)
}

// 删除订阅源
export async function removeFeed(feedId) {
    return http.delete(`/feeds/${feedId}`) // ID path usually no slash at end or specific
}

// 兼容性保留
export function canRemoveFeed(feedId) {
    return true
}

export function getAllFeeds() {
    return [] // Deprecated call usage
}

// Compatibility mocks or minimal implementation for store
export async function fetchEntries(feedId) {
    // This should now be handled by news.js, but keeping for store compatibility
    // However, entryStore should assume news API.
    // Return empty here to force store update
    return []
}

export async function markAsRead(entryId) {
    // Backend doesn't have mark read yet? 
    // Plan didn't specifying Read status syncing to backend, but usually needed.
    // For now keep local or mocked.
    return true
}
