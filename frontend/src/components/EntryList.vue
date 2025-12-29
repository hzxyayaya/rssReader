<script setup>
/**
 * 文章列表组件
 * 显示当前订阅源的文章列表，使用虚拟滚动优化性能
 */
import { computed, ref } from 'vue'
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import { useFeedStore } from '../stores/feedStore'
import { useEntryStore } from '../stores/entryStore'
import { useUiStore } from '../stores/uiStore'

// 获取 Store 实例
const feedStore = useFeedStore()
const entryStore = useEntryStore()
const uiStore = useUiStore()

// ==================== 计算属性 ====================

// 当前订阅源
const currentFeed = computed(() => feedStore.currentFeed)

// 当前订阅源标题
const currentFeedTitle = computed(() => {
  if (feedStore.currentFeedId === 'all') {
    return '全部文章'
  }
  return currentFeed.value?.title || '文章列表'
})

// 文章列表（使用排序后的列表，但不在当前会话中重新排序）
const entries = computed(() => entryStore.sortedEntries)

// 当前选中的文章 ID
const currentEntryId = computed(() => entryStore.currentEntryId)

// 已查看的文章 ID 列表（用于显示已读样式）
const viewedEntryIds = computed(() => entryStore.viewedEntryIds)

// 加载状态
const isLoading = computed(() => entryStore.isLoading)

// 文章数量
const entryCount = computed(() => entries.value.length)

// 未读文章数量
const unreadCount = computed(() => entryStore.unreadEntries.length)

/**
 * 检查文章是否显示为已读状态（包括已查看但未正式标记的）
 * @param {Object} entry - 文章对象
 */
function isVisuallyRead(entry) {
  return entry.isRead || viewedEntryIds.value.has(entry.id)
}

// ==================== 方法 ====================

/**
 * 选择文章
 * @param {Object} entry - 文章对象
 */
function selectEntry(entry) {
  entryStore.selectEntry(entry.id)
}

/**
 * 格式化发布时间
 * @param {string} dateStr - ISO 日期字符串
 * @returns {string} 格式化后的时间
 */
function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  // 小于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes <= 0 ? '刚刚' : `${minutes} 分钟前`
  }
  
  // 小于24小时
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours} 小时前`
  }
  
  // 小于7天
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days} 天前`
  }
  
  // 超过7天，显示具体日期
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

function collapseMiddle() {
  uiStore.toggleMiddleColumn()
}
</script>

<template>
  <div class="entry-list">
    <!-- 头部 -->
    <header class="entry-list-header">
      <div class="header-info">
        <h2 class="header-title">{{ currentFeedTitle }}</h2>
        <span class="header-count">
          {{ unreadCount }} 未读 / {{ entryCount }} 篇
        </span>
      </div>
    </header>

    <!-- 文章列表 -->
    <div class="entry-list-content">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="entry-loading">
        <span class="loading-spinner"></span>
        <span>加载中...</span>
      </div>

      <!-- 空状态 -->
      <div v-else-if="entries.length === 0" class="entry-empty">
        <div class="empty-icon">📭</div>
        <p>暂无文章</p>
      </div>

      <!-- 虚拟滚动列表 -->
      <RecycleScroller
        v-else
        class="scroller"
        :items="entries"
        :item-size="80"
        key-field="id"
        v-slot="{ item }"
      >
        <div
          class="entry-item"
          :class="{ 
            'active': item.id === currentEntryId,
            'is-read': isVisuallyRead(item)
          }"
          @click="selectEntry(item)"
        >
          <!-- 未读指示器 -->
          <div class="unread-indicator" v-if="!isVisuallyRead(item)"></div>
          
          <!-- 文章信息 -->
          <div class="entry-content">
            <h3 class="entry-title">{{ item.title }}</h3>

            <div class="entry-meta">
              <span class="entry-source" v-if="feedStore.currentFeedId === 'all'">
                {{ feedStore.feeds.find(f => f.id === item.feedId)?.title }}
              </span>
              <span class="entry-time">{{ formatDate(item.publishedAt) }}</span>
              <span class="entry-favorite" v-if="item.isFavorite">⭐</span>
            </div>
          </div>
        </div>
      </RecycleScroller>
    </div>
  </div>
</template>

<style scoped>
/* 文章列表容器 */
.entry-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--color-bg);
}

/* 头部 */
.entry-list-header {
  padding: 1.25rem 1rem 1rem;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
  background: var(--color-surface);
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.header-title {
  font-size: 1.0625rem;
  font-weight: 650;
  color: var(--color-text);
  margin: 0;
  letter-spacing: -0.01em;
}

.header-count {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

/* 列表内容 */
.entry-list-content {
  flex: 1;
  overflow: hidden;
  background: var(--color-bg);
}

.scroller {
  height: 100%;
}

/* 加载状态 */
.entry-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 0.875rem;
  color: var(--color-text-muted);
  font-size: 0.8125rem;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 空状态 */
.entry-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-muted);
  padding: 2rem;
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  opacity: 0.4;
}

.entry-empty p {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 500;
}

/* 文章项 - Folo.is 风格 */
.entry-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  margin: 0.25rem 0.5rem;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
  gap: 0.875rem;
  height: 80px;
  box-sizing: border-box;
  background: var(--color-surface);
}

.entry-item:hover {
  background-color: var(--color-surface);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.entry-item.active {
  background: var(--color-accent);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.entry-item.active .entry-title,
.entry-item.active .entry-meta,
.entry-item.active .entry-source,
.entry-item.active .entry-time {
  color: #fff !important;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  opacity: 1;
}

.entry-item.is-read:not(.active) {
  background: transparent;
}

.entry-item.is-read .entry-title {
  color: var(--color-text-muted);
  font-weight: 450;
}

/* 未读指示器 */
.unread-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-hover) 100%);
  flex-shrink: 0;
  margin-top: 0.5rem;
  box-shadow: 0 0 0 2px var(--color-accent-light);
}

.entry-item.active .unread-indicator {
  background: white;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

/* 文章内容 */
.entry-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.entry-title {
  font-size: 0.875rem;
  font-weight: 550;
  color: var(--color-text);
  margin: 0;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow: hidden;
  transition: color 0.15s ease;
}

.entry-summary {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.entry-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.entry-source {
  max-width: 100px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-accent);
}

.entry-source::after {
  content: '·';
  margin-left: 0.5rem;
  color: var(--color-text-muted);
}

.entry-time {
  white-space: nowrap;
}

.entry-favorite {
  margin-left: auto;
  font-size: 0.75rem;
}
</style>
