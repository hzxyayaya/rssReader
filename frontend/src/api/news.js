import http from './http'

export async function fetchNews({ skip = 0, limit = null, feedId = null } = {}) {
    const params = { skip }
    if (limit !== null && limit !== undefined) {
        params.limit = limit
    }
    if (feedId && feedId !== 'all') {
        params.feed_id = feedId
    }

    return http.get('/news/', { params })
}

export async function fetchArticle(id) {
    return http.get(`/news/${id}`)
}

export async function markAsRead(id) {
    return http.post(`/news/${id}/read`)
}

export async function fetchReadStatus() {
    return http.get('/news/read-status')
}

