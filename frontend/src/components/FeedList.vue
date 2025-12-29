<script setup>
/**
 * 订阅源列表组件
 * 显示所有订阅源，支持切换和高亮当前选中
 */
import { computed } from 'vue'
import { useFeedStore } from '../stores/feedStore'
import { useUiStore } from '../stores/uiStore'
import UserProfile from './UserProfile.vue'

// 获取 Store 实例
const feedStore = useFeedStore()
const uiStore = useUiStore()

// ==================== 计算属性 ====================

// 订阅源列表（包含"全部"选项）
const feeds = computed(() => feedStore.feedsWithAll)

// 当前选中的订阅源 ID
const currentFeedId = computed(() => feedStore.currentFeedId)

// 加载状态
const isLoading = computed(() => feedStore.isLoading)

// ==================== 方法 ====================

/**
 * 选择订阅源
 * @param {string} feedId - 订阅源 ID
 */
function selectFeed(feedId) {
  feedStore.selectFeed(feedId)
}

/**
 * 打开设置面板
 */
function openSettings() {
  uiStore.openSettingsPanel()
}
</script>

<template>
  <div class="feed-list">
    <!-- 头部 -->
    <header class="feed-list-header">
      <div class="logo-container">
        <img src="/icon.png" alt="Logo" class="app-logo" />
        <h1 class="feed-list-title">订阅源</h1>
      </div>
      <div class="flex-grow"></div> <!-- Spacer -->
      <UserProfile /> <!-- Added UserProfile -->
      <button 
        class="settings-btn"
        @click="openSettings"
        title="设置"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      </button>
    </header>

    <!-- 订阅源列表 -->
    <nav class="feed-list-content">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="feed-loading">
        <span class="loading-dot"></span>
        <span class="loading-dot"></span>
        <span class="loading-dot"></span>
      </div>

      <!-- 订阅源项 -->
      <ul v-else class="feed-items">
        <li
          v-for="feed in feeds"
          :key="feed.id"
          class="feed-item"
          :class="{ 'active': feed.id === currentFeedId }"
          @click="selectFeed(feed.id)"
        >
          <!-- 图标 -->
          <span class="feed-icon">{{ feed.icon }}</span>
          
          <!-- 名称 -->
          <span class="feed-name">{{ feed.title }}</span>
          
          <!-- 未读数量 -->
          <span 
            v-if="feed.unreadCount > 0"
            class="feed-unread-count"
          >
            {{ feed.unreadCount > 99 ? '99+' : feed.unreadCount }}
          </span>
        </li>
      </ul>
    </nav>

    <!-- 底部 -->
    <footer class="feed-list-footer">
      <div class="keyboard-hints">
        <span class="hint">
          <kbd>j</kbd>/<kbd>k</kbd> 切换
        </span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 订阅源列表容器 */
.feed-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--color-surface);
}

/* 头部 */
.feed-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1rem 1rem;
  border-bottom: 1px solid var(--color-border-light);
}

.flex-grow {
    flex-grow: 1;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.app-logo {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.feed-list-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 0;
}

.settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-muted);
  transition: all 0.15s ease;
}

.settings-btn:hover {
  background-color: var(--color-hover);
  color: var(--color-accent);
}

/* 列表内容 */
.feed-list-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.625rem 0.5rem;
}

.feed-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 2rem;
}

.loading-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  animation: loading-bounce 1.4s ease-in-out infinite both;
}

.loading-dot:nth-child(1) { animation-delay: -0.32s; }
.loading-dot:nth-child(2) { animation-delay: -0.16s; }
.loading-dot:nth-child(3) { animation-delay: 0; }

@keyframes loading-bounce {
  0%, 80%, 100% { 
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1);
    opacity: 1;
  }
}

.feed-items {
  list-style: none;
  margin: 0;
  padding: 0;
}

/* 订阅源项 - Folo.is 风格 */
.feed-item {
  display: flex;
  align-items: center;
  padding: 0.6875rem 0.875rem;
  margin: 0.125rem 0;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
  gap: 0.75rem;
}

.feed-item:hover {
  background-color: var(--color-hover);
}

.feed-item.active {
  background-color: var(--color-accent-light);
}

.feed-item.active .feed-icon {
  transform: scale(1.05);
}

.feed-item.active .feed-name {
  color: var(--color-accent);
  font-weight: 600;
}

.feed-item.active .feed-unread-count {
  background-color: var(--color-accent);
  color: white;
}

.feed-icon {
  font-size: 1.125rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
  transition: transform 0.15s ease;
}

.feed-name {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s ease;
}

.feed-unread-count {
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.1875rem 0.5rem;
  background-color: var(--color-bg);
  color: var(--color-text-secondary);
  border-radius: 10px;
  flex-shrink: 0;
  min-width: 20px;
  text-align: center;
  transition: all 0.15s ease;
}

/* 底部 */
.feed-list-footer {
  padding: 0.875rem 1rem;
  border-top: 1px solid var(--color-border-light);
}

.keyboard-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 0.625rem;
}

.hint {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.hint kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 0.3em;
  font-family: inherit;
  font-size: 0.75em;
  font-weight: 500;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 4px;
}
</style>
