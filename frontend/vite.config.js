import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 构建配置
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8021',
        changeOrigin: true
      }
    }
  }
})
