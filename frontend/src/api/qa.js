import http from './http'

export async function askQuestion({
    question,
    articleId,      // Single article (legacy)
    articleIds,     // Multiple specific articles
    feedIds,        // Filter by subscription sources  
    dateFilter,     // "today", "yesterday", "week", "all"
    sessionId
}) {
    return http.post('/qa/ask', {
        question,
        article_id: articleId,
        article_ids: articleIds,
        feed_ids: feedIds,
        date_filter: dateFilter,
        session_id: sessionId
    })
}

