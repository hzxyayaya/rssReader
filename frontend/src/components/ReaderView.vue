<script setup>
/**
 * 阅读视图组件
 * 显示文章完整内容，提供沉浸式阅读体验
 * 使用 useReader composable 管理阅读逻辑
 */
import { computed, onUnmounted } from 'vue'
import { useUiStore } from '../stores/uiStore'
import DOMPurify from 'dompurify'
import { useEntryStore } from '../stores/entryStore'
import { useFeedStore } from '../stores/feedStore'
import { useReader } from '../composables/useReader'
import ReadingProgress from './ReadingProgress.vue'
import AiChatPanel from './AiChatPanel.vue'

// 获取 Store 实例
const entryStore = useEntryStore()
const feedStore = useFeedStore()
const uiStore = useUiStore()

// 使用 useReader composable 管理阅读逻辑
const {
  readingProgress,
  readingStyles,
  setReaderRef,
  toggleImmersiveMode,
  cleanup
} = useReader()

// ==================== 计算属性 ====================

// 当前文章
const entry = computed(() => entryStore.currentEntry)

// 文章原文链接
const originalLink = computed(() => entry.value?.link || '')

// 文章来源订阅源
const feedName = computed(() => {
  if (!entry.value) return ''
  const feed = feedStore.feeds.find(f => f.id === entry.value.feedId)
  return feed?.title || ''
})

// 格式化发布时间
const formattedDate = computed(() => {
  if (!entry.value) return ''
  const date = new Date(entry.value.publishedAt)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

// 消毒后的 HTML 内容
const sanitizedContent = computed(() => {
  if (!entry.value?.content) return ''
  
  // 使用 DOMPurify 消毒 HTML 内容
  return DOMPurify.sanitize(entry.value.content, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'hr',
      'ul', 'ol', 'li',
      'blockquote', 'pre', 'code',
      'a', 'strong', 'em', 'b', 'i', 'u', 's', 'del',
      'img', 'figure', 'figcaption',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'div', 'span',
      'video', 'audio', 'source', 'iframe'
    ],
    ALLOWED_ATTR: [
      'href', 'src', 'alt', 'title', 'class', 'target', 'rel',
      'controls', 'autoplay', 'loop', 'muted', 'poster', 'preload',
      'width', 'height', 'type',
      'frameborder', 'allowfullscreen', 'allow', 'loading'
    ],
    ADD_ATTR: ['target'],
    ALLOW_DATA_ATTR: false,
    ADD_TAGS: ['iframe'],
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
  })
})

// 是否沉浸式模式（从 uiStore 获取）
const isImmersive = computed(() => uiStore.isImmersiveMode)

// ==================== 方法 ====================

/**
 * 切换收藏状态
 */
function toggleFavorite() {
  if (entry.value) {
    entryStore.toggleFavorite(entry.value.id)
  }
}

/**
 * 上一篇文章
 */
function previousEntry() {
  entryStore.selectPreviousEntry()
}

/**
 * 下一篇文章
 */
function nextEntry() {
  entryStore.selectNextEntry()
}

/**
 * 打开原文链接
 */
function openOriginal() {
  if (originalLink.value) {
    window.open(originalLink.value, '_blank', 'noopener,noreferrer')
  }
}

// 组件卸载时清理
onUnmounted(() => {
  cleanup()
})
</script>

<template>
  <div class="reader-view" :class="{ 'immersive': isImmersive }">
    <!-- 阅读进度条 -->
    <ReadingProgress :progress="readingProgress" />
    
    <!-- 工具栏 -->
    <header class="reader-toolbar">
      <div class="toolbar-left">
        <!-- 返回/折叠按钮 -->
        <button 
          class="toolbar-btn"
          @click="toggleImmersiveMode"
          :title="isImmersive ? '退出沉浸模式' : '进入沉浸模式'"
        >
          {{ isImmersive ? '◀' : '▶' }}
        </button>
      </div>
      
      <div class="toolbar-right">
        <!-- 收藏按钮 -->
        <button 
          class="toolbar-btn"
          @click="toggleFavorite"
          :class="{ 'active': entry?.isFavorite }"
          title="收藏"
        >
          {{ entry?.isFavorite ? '⭐' : '☆' }}
        </button>

        <!-- AI 问答 -->
        <button 
          class="toolbar-btn"
          @click="uiStore.toggleAiPanel"
          title="AI 问答"
        >
          🤖
        </button>
        
        <!-- 上一篇 -->
        <button 
          class="toolbar-btn"
          @click="previousEntry"
          :disabled="!entryStore.hasPreviousEntry"
          title="上一篇 (K)"
        >
          ←
        </button>
        
        <!-- 下一篇 -->
        <button 
          class="toolbar-btn"
          @click="nextEntry"
          :disabled="!entryStore.hasNextEntry"
          title="下一篇 (J)"
        >
          →
        </button>
      </div>
    </header>
    
    <!-- 阅读区域 -->
    <main 
      :ref="setReaderRef"
      class="reader-scroll-area"
    >
      <article class="reader-article" :style="readingStyles">
        <!-- 文章头部 -->
        <header class="article-header">
          <h1 class="article-title">{{ entry?.title }}</h1>
          <div class="article-meta">
            <span class="article-source">{{ feedName }}</span>
            <span class="meta-separator">·</span>
            <span class="article-author" v-if="entry?.author">{{ entry.author }}</span>
            <span class="meta-separator" v-if="entry?.author">·</span>
            <time class="article-time">{{ formattedDate }}</time>
            <!-- 原文链接放在顶部 -->
            <a 
              v-if="originalLink"
              :href="originalLink"
              target="_blank"
              rel="noopener noreferrer"
              class="header-original-link"
              @click.prevent="openOriginal"
            >
              🔗 查看原文
            </a>
          </div>
        </header>
        
        <!-- 文章内容 -->
        <div 
          class="article-content"
          v-html="sanitizedContent"
        ></div>
        
        <!-- 文章底部 -->
        <footer class="article-footer">
          <div class="article-end-mark">— 全文完 —</div>
          
          <nav class="article-nav">
            <button 
              class="nav-btn prev"
              @click="previousEntry"
              :disabled="!entryStore.hasPreviousEntry"
            >
              ← 上一篇
            </button>
            <button 
              class="nav-btn next"
              @click="nextEntry"
              :disabled="!entryStore.hasNextEntry"
            >
              下一篇 →
            </button>
          </nav>
        </footer>
      </article>
    </main>
    
    <AiChatPanel />
  </div>
</template>

<style scoped>
/* 阅读视图容器 */
.reader-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  background-color: var(--color-surface);
}

/* 工具栏 */
.reader-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-surface);
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 0.5rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  transition: all 0.15s ease;
  gap: 0.25rem;
}

.toolbar-btn:hover:not(:disabled) {
  background-color: var(--color-hover);
  color: var(--color-text);
}

.toolbar-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.toolbar-btn.active {
  color: var(--color-accent);
}

/* 滚动区域 */
.reader-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

/* 文章容器 */
.reader-article {
  max-width: var(--max-width-reading);
  margin: 0 auto;
}

/* 文章头部 */
.article-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.article-title {
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-text);
  margin: 0 0 1rem 0;
}

.article-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.meta-separator {
  color: var(--color-border);
}

.article-source {
  color: var(--color-accent);
}

/* 顶部原文链接 */
.header-original-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background-color: var(--color-accent);
  border-radius: 4px;
  color: white;
  text-decoration: none;
  font-size: 0.8125rem;
  font-weight: 500;
  margin-left: 0.5rem;
  transition: all 0.15s ease;
}

.header-original-link:hover {
  opacity: 0.9;
}

/* 文章底部 */
.article-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.article-end-mark {
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}



.article-nav {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.nav-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text);
  transition: all 0.15s ease;
}

.nav-btn:hover:not(:disabled) {
  background-color: var(--color-hover);
  border-color: var(--color-accent);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.nav-btn.prev {
  text-align: left;
}

.nav-btn.next {
  text-align: right;
}

/* 沉浸式模式 */
.reader-view.immersive .reader-toolbar {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.reader-view.immersive:hover .reader-toolbar {
  opacity: 1;
}

.reader-view.immersive .reader-scroll-area {
  padding: 3rem;
}

.reader-view.immersive .reader-article {
  max-width: 70ch;
}
</style>
