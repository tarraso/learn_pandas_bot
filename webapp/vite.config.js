import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],

  // Base path for assets
  base: '/',

  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: mode !== 'production',
    minify: mode === 'production' ? 'esbuild' : false,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'monaco': ['@monaco-editor/react'],
        }
      }
    }
  },

  // Development server configuration
  server: {
    port: 3000,
    allowedHosts: [
      process.env.NGROK_URL?.replace('https://', '').replace('http://', '') || 'localhost',
      '.ngrok-free.app',
      'localhost'
    ],
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://94.72.140.27:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      }
    }
  },

  // Environment variables prefix
  envPrefix: 'VITE_',
}))
