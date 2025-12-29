<script setup>
/**
 * 阅读进度条组件
 * 显示在阅读视图顶部，实时显示阅读进度
 */
import { computed } from 'vue'

// ==================== Props ====================
const props = defineProps({
  // 阅读进度（0-100）
  progress: {
    type: Number,
    default: 0
  }
})

// ==================== 计算属性 ====================

// 进度条宽度样式
const progressStyle = computed(() => ({
  width: `${props.progress}%`
}))

// 是否显示进度条（进度大于0时显示）
const isVisible = computed(() => props.progress > 0)
</script>

<template>
  <div 
    class="reading-progress"
    :class="{ 'visible': isVisible }"
  >
    <div 
      class="progress-bar"
      :style="progressStyle"
    ></div>
  </div>
</template>

<style scoped>
/* 进度条容器 */
.reading-progress {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: transparent;
  z-index: 100;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.reading-progress.visible {
  opacity: 1;
}

/* 进度条 */
.progress-bar {
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--color-accent),
    color-mix(in srgb, var(--color-accent) 80%, white)
  );
  border-radius: 0 3px 3px 0;
  transition: width 0.1s ease-out;
}
</style>
