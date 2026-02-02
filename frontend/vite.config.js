import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('error', (err) => console.warn('Proxy error:', err.message));
          proxy.on('proxyReq', (proxyReq) => proxyReq.setHeader('Connection', 'keep-alive'));
        },
      },
      '/customers': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
