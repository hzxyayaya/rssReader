<script setup>
/**
 * 应用布局组件
 * 实现三栏布局：订阅源列表 | 文章列表 | 阅读视图
 */
import { onMounted, computed, watch } from 'vue'
import { useFeedStore } from '../stores/feedStore'
import { useEntryStore } from '../stores/entryStore'
import { useUiStore } from '../stores/uiStore'
import FeedList from './FeedList.vue'
import EntryList from './EntryList.vue'
import ReaderView from './ReaderView.vue'
import SettingsPanel from './SettingsPanel.vue'

// 获取 Store 实例
const feedStore = useFeedStore()
const entryStore = useEntryStore()
const uiStore = useUiStore()

// ==================== 计算属性 ====================

// 左侧边栏是否折叠
const isLeftCollapsed = computed(() => uiStore.isLeftSidebarCollapsed)

// 中间列是否折叠
const isMiddleCollapsed = computed(() => uiStore.isMiddleColumnCollapsed)

// 是否处于沉浸式阅读模式
const isImmersive = computed(() => uiStore.isImmersiveMode)

// 是否有选中的文章
const hasCurrentEntry = computed(() => !!entryStore.currentEntry)

// ==================== 生命周期 ====================

// 组件挂载时加载数据
onMounted(async () => {
  // 加载订阅源列表
  await feedStore.loadFeeds()
  // 加载全部文章
  await entryStore.loadEntries('all')
})

// ==================== 监听器 ====================

// 监听当前订阅源变化，加载对应文章
watch(() => feedStore.currentFeedId, async (feedId, oldFeedId) => {
  if (feedId) {
    // 切换订阅源时，先标记当前文章为已读
    if (oldFeedId && entryStore.currentEntryId) {
      entryStore.clearCurrentEntry()
    }
    // 然后加载新订阅源的文章
    await entryStore.loadEntries(feedId)
  }
})
</script>

<template>
  <div class="app-layout">
    <!-- 左侧栏：订阅源列表 -->
    <aside 
      class="sidebar-left"
      :class="{ 'collapsed': isLeftCollapsed }"
    >
      <FeedList />
    </aside>

    <!-- 中间栏：文章列表 -->
    <main 
      class="content-middle"
      :class="{ 'collapsed': isMiddleCollapsed }"
    >
      <EntryList />
    </main>

    <!-- 右侧栏：阅读视图 -->
    <article 
      class="content-right"
      :class="{ 
        'expanded': isMiddleCollapsed,
        'full-width': isImmersive
      }"
    >
      <ReaderView v-if="hasCurrentEntry" />
      
      <!-- 空状态提示 -->
      <div v-else class="empty-state">
        <div class="empty-state-icon">📖</div>
        <h2 class="empty-state-title">选择一篇文章开始阅读</h2>
        <p class="empty-state-desc">
          使用 <kbd>j</kbd> / <kbd>k</kbd> 切换文章<br>
          按 <kbd>f</kbd> 进入沉浸式阅读<br>
          按 <kbd>t</kbd> 切换主题
        </p>
      </div>
    </article>

    <!-- 设置面板（使用 Teleport） -->
    <SettingsPanel />
  </div>
</template>

<style scoped>
/* 三栏布局容器 */
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--color-bg);
}

/* 左侧栏 - 订阅源列表 */
.sidebar-left {
  width: 240px;
  min-width: 240px;
  height: 100%;
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  transition: width 0.3s ease, min-width 0.3s ease, opacity 0.3s ease;
  overflow: hidden;
}

.sidebar-left.collapsed {
  width: 0;
  min-width: 0;
  opacity: 0;
  border-right: none;
}

/* 中间栏 - 文章列表 */
.content-middle {
  width: 360px;
  min-width: 360px;
  height: 100%;
  background-color: var(--color-bg);
  border-right: 1px solid var(--color-border);
  transition: width 0.3s ease, min-width 0.3s ease, opacity 0.3s ease;
  overflow: hidden;
}

.content-middle.collapsed {
  width: 0;
  min-width: 0;
  opacity: 0;
  border-right: none;
}

/* 右侧栏 - 阅读视图 */
.content-right {
  flex: 1;
  height: 100%;
  background-color: var(--color-surface);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.content-right.expanded {
  /* 中间栏折叠时，阅读区域扩展 */
  flex: 1;
}

.content-right.full-width {
  /* 沉浸式模式，占据全部宽度 */
  flex: 1;
  max-width: 100%;
}

/* 空状态提示 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  color: var(--color-text-muted);
  text-align: center;
}

.empty-state-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-state-title {
  font-size: 1.25rem;
  font-weight: 500;
  color: var(--color-text);
  margin: 0 0 1rem 0;
}

.empty-state-desc {
  font-size: 0.875rem;
  line-height: 2;
  margin: 0;
}

.empty-state-desc kbd {
  display: inline-block;
  padding: 0.2em 0.5em;
  font-family: inherit;
  font-size: 0.8em;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  margin: 0 0.2em;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar-left {
    width: 200px;
    min-width: 200px;
  }
  
  .content-middle {
    width: 300px;
    min-width: 300px;
  }
}

@media (max-width: 900px) {
  .sidebar-left {
    width: 180px;
    min-width: 180px;
  }
  
  .content-middle {
    width: 260px;
    min-width: 260px;
  }
}
</style>
