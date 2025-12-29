<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useEntryStore } from '../stores/entryStore'
import { useFeedStore } from '../stores/feedStore'
import { useUiStore } from '../stores/uiStore'
import { askQuestion } from '../api/qa'

const entryStore = useEntryStore()
const feedStore = useFeedStore()
const uiStore = useUiStore()

const messages = ref([])
const input = ref('')
const isLoading = ref(false)
const scrollArea = ref(null)

// Context filter state
const contextMode = ref('current')  // 'current', 'all', 'date', 'feed'
const selectedDateFilter = ref('today')  // 'today', 'yesterday', 'week'
const selectedFeedId = ref(null)

const currentEntryId = computed(() => entryStore.currentEntryId)
const isOpen = computed(() => uiStore.isAiPanelOpen)
const feeds = computed(() => feedStore.feeds)

// Context mode options
const contextModes = [
  { value: 'current', label: '当前文章', icon: '📄' },
  { value: 'all', label: '全部文章', icon: '📚' },
  { value: 'date', label: '按日期', icon: '📅' },
  { value: 'feed', label: '按订阅源', icon: '📰' }
]

const dateOptions = [
  { value: 'today', label: '今天' },
  { value: 'yesterday', label: '昨天' },
  { value: 'week', label: '近一周' }
]

// Get context description for display
const contextDescription = computed(() => {
  switch (contextMode.value) {
    case 'current':
      return entryStore.currentEntry?.title?.slice(0, 20) + '...' || '当前文章'
    case 'all':
      return '全部已向量化文章'
    case 'date':
      return dateOptions.find(d => d.value === selectedDateFilter.value)?.label || '今天'
    case 'feed':
      return feeds.value.find(f => f.id === selectedFeedId.value)?.title || '选择订阅源'
    default:
      return '当前文章'
  }
})

// 清空对话当切换文章或上下文模式
watch([currentEntryId, contextMode], () => {
  messages.value = []
  uiStore.setSessionId(null)
})

// 自动滚动到底部
watch(() => messages.value.length, () => {
  nextTick(() => {
    if (scrollArea.value) {
      scrollArea.value.scrollTop = scrollArea.value.scrollHeight
    }
  })
})

async function sendMessage() {
  if (!input.value.trim() || isLoading.value) return
  
  const question = input.value.trim()
  input.value = ''
  
  // Add User Message
  messages.value.push({
    role: 'user',
    content: question
  })
  
  isLoading.value = true
  
  try {
    // Build request params based on context mode
    const params = {
      question,
      sessionId: uiStore.sessionId
    }
    
    switch (contextMode.value) {
      case 'current':
        params.articleId = currentEntryId.value
        break
      case 'all':
        // No filter - search all
        break
      case 'date':
        params.dateFilter = selectedDateFilter.value
        break
      case 'feed':
        if (selectedFeedId.value) {
          params.feedIds = [selectedFeedId.value]
        }
        break
    }
    
    const res = await askQuestion(params)
    
    // Update Session ID if new
    if (res.session_id && !uiStore.sessionId) {
      uiStore.setSessionId(res.session_id)
    }
    
    // Add AI Message
    messages.value.push({
      role: 'ai',
      content: res.answer,
      citations: res.citations
    })
  } catch (e) {
    messages.value.push({
      role: 'ai',
      content: '抱歉，出现了错误，请稍后再试。',
      isError: true
    })
    console.error(e)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="ai-panel" :class="{ 'is-open': isOpen }">
    <div class="panel-header">
      <h3>🤖 AI 助手</h3>
      <button class="close-btn" @click="uiStore.toggleAiPanel">×</button>
    </div>
    
    <!-- Context Selector -->
    <div class="context-selector">
      <div class="context-label">上下文范围</div>
      <div class="context-modes">
        <button 
          v-for="mode in contextModes" 
          :key="mode.value"
          class="mode-btn"
          :class="{ active: contextMode === mode.value }"
          @click="contextMode = mode.value"
          :title="mode.label"
        >
          <span class="mode-icon">{{ mode.icon }}</span>
          <span class="mode-text">{{ mode.label }}</span>
        </button>
      </div>
      
      <!-- Date sub-selector -->
      <div v-if="contextMode === 'date'" class="sub-selector">
        <select v-model="selectedDateFilter">
          <option v-for="opt in dateOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
      
      <!-- Feed sub-selector -->
      <div v-if="contextMode === 'feed'" class="sub-selector">
        <select v-model="selectedFeedId">
          <option :value="null" disabled>选择订阅源</option>
          <option v-for="feed in feeds" :key="feed.id" :value="feed.id">
            {{ feed.icon }} {{ feed.title }}
          </option>
        </select>
      </div>
      
      <div class="context-info">
        📍 {{ contextDescription }}
      </div>
    </div>
    
    <div class="messages-area" ref="scrollArea">
      <div v-show="messages.length === 0" class="empty-state">
        <p>基于 <strong>{{ contextDescription }}</strong> 提问...</p>
      </div>
      
      <div 
        v-for="(msg, idx) in messages" 
        :key="idx" 
        class="message-bubble"
        :class="msg.role"
      >
        <div class="message-content">{{ msg.content }}</div>
        
        <div v-if="msg.citations && msg.citations.length > 0" class="citations">
          <div class="citation-title">参考来源:</div>
          <div v-for="(cite, cIdx) in msg.citations" :key="cIdx" class="citation-item">
            {{ cite.text }}
          </div>
        </div>
      </div>
      
      <div v-if="isLoading" class="message-bubble ai loading">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
    </div>
    
    <div class="input-area">
      <textarea 
        v-model="input" 
        @keydown.enter.prevent="sendMessage"
        placeholder="输入问题 (Enter 发送)..."
      ></textarea>
      <button @click="sendMessage" :disabled="!input.trim() || isLoading">
        ➤
      </button>
    </div>
  </div>
</template>

<style scoped>
.ai-panel {
  position: fixed;
  top: 0;
  right: -380px;
  width: 380px;
  height: 100vh;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  box-shadow: -2px 0 10px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  transition: right 0.3s ease;
  z-index: 1000;
}

.ai-panel.is-open {
  right: 0;
}

.panel-header {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 1rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--color-text-muted);
}

/* Context Selector */
.context-selector {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg);
}

.context-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.context-modes {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.mode-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.125rem;
  padding: 0.5rem 0.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-btn:hover {
  border-color: var(--color-accent);
}

.mode-btn.active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: white;
}

.mode-icon {
  font-size: 1rem;
}

.mode-text {
  font-size: 0.625rem;
}

.sub-selector {
  margin: 0.5rem 0;
}

.sub-selector select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
}

.context-info {
  font-size: 0.75rem;
  color: var(--color-accent);
  padding: 0.25rem 0.5rem;
  background: color-mix(in srgb, var(--color-accent) 10%, transparent);
  border-radius: 4px;
  text-align: center;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem 1rem;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

.message-bubble {
  max-width: 85%;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.message-bubble.user {
  align-self: flex-end;
  background: var(--color-accent);
  color: white;
}

.message-bubble.ai {
  align-self: flex-start;
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.message-bubble.isError {
  border-color: red;
  color: red;
}

.input-area {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: 0.5rem;
}

textarea {
  flex: 1;
  height: 60px;
  resize: none;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
}

.input-area button {
  padding: 0 1rem;
  background: var(--color-accent);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font-size: 1rem;
}

.input-area button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.citations {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  border-top: 1px dashed var(--color-border);
  padding-top: 0.25rem;
}

.citation-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.citation-item {
  padding: 0.25rem 0;
  border-bottom: 1px dotted var(--color-border);
}

.loading .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #ccc;
  border-radius: 50%;
  margin-right: 3px;
  animation: bounce 1.4s infinite ease-in-out both;
}
.loading .dot:nth-child(1) { animation-delay: -0.32s; }
.loading .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
