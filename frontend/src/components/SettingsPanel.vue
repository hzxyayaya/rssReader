<script setup>
/**
 * 设置面板组件
 * 使用 Teleport 渲染到 body
 * 包含主题设置、字体设置、添加/管理订阅源
 */
import { ref, computed } from 'vue'
import { useUiStore, THEMES, FONT_SIZES, LINE_HEIGHTS } from '../stores/uiStore'
import { useFeedStore } from '../stores/feedStore'


// 获取 Store 实例
const uiStore = useUiStore()
const feedStore = useFeedStore()

// ==================== 状态 ====================

// 当前标签页
const activeTab = ref('appearance')

// 新订阅源表单
const newFeed = ref({
  title: '',
  url: '',
  icon: '📰'
})

// 添加订阅源的加载状态
const isAddingFeed = ref(false)

// 错误信息
const addError = ref('')

// ==================== 计算属性 ====================

// 面板是否打开
const isOpen = computed(() => uiStore.isSettingsPanelOpen)

// 当前主题
const currentTheme = computed(() => uiStore.theme)

// 当前字体大小
const currentFontSize = computed(() => uiStore.fontSize)

// 当前行高
const currentLineHeight = computed(() => uiStore.lineHeight)

// 订阅源列表
const feeds = computed(() => feedStore.feeds)

// 主题选项
const themeOptions = [
  { value: THEMES.LIGHT, label: '浅色', icon: '☀️' },
  { value: THEMES.DARK, label: '深色', icon: '🌙' },
  { value: THEMES.SEPIA, label: '护眼', icon: '📜' }
]

// 字体大小选项
const fontSizeOptions = [
  { value: FONT_SIZES.SMALL, label: '小' },
  { value: FONT_SIZES.MEDIUM, label: '中' },
  { value: FONT_SIZES.LARGE, label: '大' },
  { value: FONT_SIZES.XLARGE, label: '特大' }
]

// 行高选项
const lineHeightOptions = [
  { value: LINE_HEIGHTS.COMPACT, label: '紧凑' },
  { value: LINE_HEIGHTS.NORMAL, label: '适中' },
  { value: LINE_HEIGHTS.RELAXED, label: '宽松' }
]

// 图标选项
const iconOptions = ['📰', '📱', '💻', '🎮', '🎬', '📚', '🔧', '🚀', '💡', '🌐']

// ==================== 方法 ====================

/**
 * 关闭面板
 */
function closePanel() {
  uiStore.closeSettingsPanel()
  // 重置表单
  newFeed.value = { title: '', url: '', icon: '📰' }
  addError.value = ''
}

/**
 * 设置主题
 */
function setTheme(theme) {
  uiStore.setTheme(theme)
}

/**
 * 设置字体大小
 */
function setFontSize(size) {
  uiStore.setFontSize(size)
}

/**
 * 设置行高
 */
function setLineHeight(height) {
  uiStore.setLineHeight(height)
}

/**
 * 添加订阅源
 */
async function addFeed() {
  if (!newFeed.value.title.trim() || !newFeed.value.url.trim()) {
    addError.value = '请填写订阅源名称和地址'
    return
  }
  
  // 简单的 URL 验证
  try {
    new URL(newFeed.value.url)
  } catch {
    addError.value = '请输入有效的 URL 地址'
    return
  }
  
  isAddingFeed.value = true
  addError.value = ''
  
  try {
    await feedStore.addFeed({
      title: newFeed.value.title.trim(),
      url: newFeed.value.url.trim(),
      icon: newFeed.value.icon,
      description: ''
    })
    
    // 重置表单
    newFeed.value = { title: '', url: '', icon: '📰' }
    
    // 切换到订阅源管理标签
    activeTab.value = 'feeds'
  } catch (e) {
    addError.value = e.message || '添加失败，请重试'
  } finally {
    isAddingFeed.value = false
  }
}

/**
 * 删除订阅源
 */
function deleteFeed(feedId) {
  if (confirm('确定要删除这个订阅源吗？')) {
    feedStore.deleteFeed(feedId)
  }
}

/**
 * 检查订阅源是否可删除
 */
function canDelete(feedId) {
  return feedStore.isRemovable(feedId)
}

/**
 * 点击遮罩关闭面板
 */
function handleOverlayClick(event) {
  if (event.target === event.currentTarget) {
    closePanel()
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="panel">
      <div 
        v-if="isOpen"
        class="settings-overlay"
        @click="handleOverlayClick"
      >
        <div class="settings-panel">
          <!-- 面板头部 -->
          <header class="panel-header">
            <h2 class="panel-title">设置</h2>
            <button 
              class="close-btn"
              @click="closePanel"
              title="关闭 (ESC)"
            >
              ✕
            </button>
          </header>
          
          <!-- 标签页导航 -->
          <nav class="panel-tabs">
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'appearance' }"
              @click="activeTab = 'appearance'"
            >
              外观
            </button>
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'feeds' }"
              @click="activeTab = 'feeds'"
            >
              订阅源
            </button>
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'shortcuts' }"
              @click="activeTab = 'shortcuts'"
            >
              快捷键
            </button>
          </nav>
          
          <div class="panel-content">
            <!-- 外观设置 -->
            <div v-show="activeTab === 'appearance'">
              <!-- 主题设置 -->
              <section class="setting-section">
                <h3 class="section-title">主题</h3>
                <div class="theme-options">
                  <button
                    v-for="option in themeOptions"
                    :key="option.value"
                    class="theme-btn"
                    :class="{ 'active': currentTheme === option.value }"
                    @click="setTheme(option.value)"
                  >
                    <span class="theme-icon">{{ option.icon }}</span>
                    <span class="theme-label">{{ option.label }}</span>
                  </button>
                </div>
              </section>
              
              <!-- 字体大小设置 -->
              <section class="setting-section">
                <h3 class="section-title">字体大小</h3>
                <div class="size-options">
                  <button
                    v-for="option in fontSizeOptions"
                    :key="option.value"
                    class="size-btn"
                    :class="{ 'active': currentFontSize === option.value }"
                    @click="setFontSize(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
                <p class="setting-value">当前：{{ currentFontSize }}px</p>
              </section>
              
              <!-- 行高设置 -->
              <section class="setting-section">
                <h3 class="section-title">行高</h3>
                <div class="size-options">
                  <button
                    v-for="option in lineHeightOptions"
                    :key="option.value"
                    class="size-btn"
                    :class="{ 'active': currentLineHeight === option.value }"
                    @click="setLineHeight(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
                <p class="setting-value">当前：{{ currentLineHeight }}</p>
              </section>
            </div>
            
            <!-- 订阅源管理 -->
            <div v-show="activeTab === 'feeds'">
              <!-- 添加订阅源 -->
              <section class="setting-section">
                <h3 class="section-title">添加订阅源</h3>
                
                <div v-if="addError" class="error-message">
                  {{ addError }}
                </div>
                
                <div class="add-feed-form">
                  <div class="form-row">
                    <label>图标</label>
                    <div class="icon-picker">
                      <button 
                        v-for="icon in iconOptions" 
                        :key="icon"
                        class="icon-option"
                        :class="{ active: newFeed.icon === icon }"
                        @click="newFeed.icon = icon"
                      >
                        {{ icon }}
                      </button>
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <label>名称</label>
                    <input 
                      v-model="newFeed.title"
                      type="text"
                      placeholder="例如：少数派"
                      class="form-input"
                    />
                  </div>
                  
                  <div class="form-row">
                    <label>RSS 地址</label>
                    <input 
                      v-model="newFeed.url"
                      type="url"
                      placeholder="https://example.com/feed"
                      class="form-input"
                    />
                  </div>
                  
                  <button 
                    class="add-btn"
                    @click="addFeed"
                    :disabled="isAddingFeed"
                  >
                    {{ isAddingFeed ? '添加中...' : '添加订阅源' }}
                  </button>
                </div>
              </section>
              
              <!-- 订阅源列表 -->
              <section class="setting-section">
                <h3 class="section-title">已订阅 ({{ feeds.length }})</h3>
                <ul class="feed-list">
                  <li 
                    v-for="feed in feeds" 
                    :key="feed.id"
                    class="feed-item"
                  >
                    <span class="feed-icon">{{ feed.icon }}</span>
                    <span class="feed-name">{{ feed.title }}</span>
                    <button 
                      v-if="canDelete(feed.id)"
                      class="delete-btn"
                      @click="deleteFeed(feed.id)"
                      title="删除"
                    >
                      🗑️
                    </button>
                    <span v-else class="default-badge">默认</span>
                  </li>
                </ul>
              </section>
            </div>
            
            <!-- 快捷键说明 -->
            <div v-show="activeTab === 'shortcuts'">
              <section class="setting-section">
                <h3 class="section-title">键盘快捷键</h3>
                <ul class="shortcuts-list">
                  <li>
                    <kbd>J</kbd> / <kbd>K</kbd>
                    <span>下一篇 / 上一篇</span>
                  </li>
                  <li>
                    <kbd>Space</kbd>
                    <span>向下滚动</span>
                  </li>
                  <li>
                    <kbd>F</kbd>
                    <span>沉浸式模式</span>
                  </li>
                  <li>
                    <kbd>T</kbd>
                    <span>切换主题</span>
                  </li>
                  <li>
                    <kbd>ESC</kbd>
                    <span>退出阅读 / 关闭面板</span>
                  </li>
                  <li>
                    <kbd>,</kbd>
                    <span>打开设置</span>
                  </li>
                </ul>
              </section>
              
              <section class="setting-section">
                <h3 class="section-title">阅读提示</h3>
                <p class="tip-text">
                  • 切换到其他文章时，当前文章会自动标记为已读<br>
                  • 点击底部链接可跳转到原文网站<br>
                  • 未读文章会优先显示在列表顶部
                </p>
              </section>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* 遮罩层 */
.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

/* 设置面板 */
.settings-panel {
  width: 450px;
  max-width: 90vw;
  max-height: 85vh;
  background-color: var(--color-surface);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 面板头部 */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.panel-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  color: var(--color-text-muted);
  transition: all 0.15s ease;
}

.close-btn:hover {
  background-color: var(--color-hover);
  color: var(--color-text);
}

/* 标签页导航 */
.panel-tabs {
  display: flex;
  padding: 0 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.tab-btn {
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--color-text);
}

.tab-btn.active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

/* 面板内容 */
.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
}

/* 设置区块 */
.setting-section {
  margin-bottom: 1.5rem;
}

.setting-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.75rem 0;
}

/* 主题选项 */
.theme-options {
  display: flex;
  gap: 0.75rem;
}

.theme-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: var(--color-bg);
  border: 2px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.theme-btn:hover {
  border-color: var(--color-accent);
}

.theme-btn.active {
  border-color: var(--color-accent);
  background-color: color-mix(in srgb, var(--color-accent) 10%, var(--color-bg));
}

.theme-icon {
  font-size: 1.5rem;
}

.theme-label {
  font-size: 0.875rem;
  color: var(--color-text);
}

/* 大小选项 */
.size-options {
  display: flex;
  gap: 0.5rem;
}

.size-btn {
  flex: 1;
  padding: 0.625rem 1rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text);
  transition: all 0.15s ease;
}

.size-btn:hover {
  border-color: var(--color-accent);
}

.size-btn.active {
  background-color: var(--color-accent);
  border-color: var(--color-accent);
  color: white;
}

.setting-value {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin: 0.5rem 0 0 0;
}

/* 添加订阅源表单 */
.add-feed-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-row label {
  font-size: 0.8125rem;
  color: var(--color-text);
}

.form-input {
  padding: 0.625rem 0.875rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.875rem;
  color: var(--color-text);
  outline: none;
  transition: border-color 0.15s ease;
}

.form-input:focus {
  border-color: var(--color-accent);
}

.form-input::placeholder {
  color: var(--color-text-muted);
}

.icon-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.icon-option {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.125rem;
  transition: all 0.15s ease;
}

.icon-option:hover {
  border-color: var(--color-accent);
}

.icon-option.active {
  background: var(--color-accent);
  border-color: var(--color-accent);
}

.add-btn {
  padding: 0.75rem;
  background-color: var(--color-accent);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.add-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  padding: 0.625rem;
  background-color: #fee2e2;
  border-radius: 6px;
  color: #dc2626;
  font-size: 0.8125rem;
  margin-bottom: 0.75rem;
}

/* 订阅源列表 */
.feed-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.feed-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem;
  border-bottom: 1px solid var(--color-border);
}

.feed-item:last-child {
  border-bottom: none;
}

.feed-icon {
  font-size: 1.125rem;
}

.feed-name {
  flex: 1;
  font-size: 0.875rem;
  color: var(--color-text);
}

.delete-btn {
  padding: 0.25rem 0.5rem;
  background: transparent;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.15s ease;
}

.delete-btn:hover {
  opacity: 1;
}

.default-badge {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  padding: 0.125rem 0.5rem;
  background: var(--color-bg);
  border-radius: 4px;
}

/* 快捷键列表 */
.shortcuts-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.shortcuts-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
  font-size: 0.875rem;
  border-bottom: 1px solid var(--color-border);
}

.shortcuts-list li:last-child {
  border-bottom: none;
}

.shortcuts-list span {
  color: var(--color-text-muted);
}

.shortcuts-list kbd {
  display: inline-block;
  padding: 0.15em 0.4em;
  font-family: inherit;
  font-size: 0.85em;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 3px;
  margin: 0 0.15em;
}

.tip-text {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  line-height: 1.8;
  margin: 0;
}

/* 动画 */
.panel-enter-active,
.panel-leave-active {
  transition: opacity 0.2s ease;
}

.panel-enter-active .settings-panel,
.panel-leave-active .settings-panel {
  transition: transform 0.2s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
}

.panel-enter-from .settings-panel {
  transform: scale(0.95);
}

.panel-leave-to .settings-panel {
  transform: scale(0.95);
}
</style>
