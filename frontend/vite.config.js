import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Enable minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs in production
        drop_debugger: true,
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    // Manual chunk splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['zustand', 'axios'],
          // Admin pages
          'admin': [
            './src/pages/admin/AdminDashboard.jsx',
            './src/pages/admin/AdminAnalyticsPage.jsx',
            './src/pages/admin/AdminPanelPage.jsx',
            './src/pages/admin/FailureLogsPage.jsx',
            './src/pages/admin/FounderDashboard.jsx',
            './src/pages/admin/AdminDisputesPage.jsx',
          ],
          // Freelancer pages
          'freelancer': [
            './src/pages/freelancer/FreelancerDashboard.jsx',
            './src/pages/freelancer/LeadsPage.jsx',
            './src/pages/freelancer/MyLeadsPage.jsx',
            './src/pages/freelancer/DiscoverLeadsPage.jsx',
          ],
          // Business owner pages
          'business': [
            './src/pages/business-owner/BusinessOwnerDashboard.jsx',
            './src/pages/business-owner/BusinessOwnerOnboarding.jsx',
          ],
        },
      },
    },
    // Source maps for production debugging (optional)
    sourcemap: false,
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'zustand', 'axios'],
  },
})
