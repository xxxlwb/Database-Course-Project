import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',     // listen on all interfaces (needed for cloud server access)
    port: 5173,
    strictPort: true,
    // Allow any Host header (cloud server has bare IP, not a known domain)
    allowedHosts: true,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
