import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // During `npm run dev`, proxy API calls to the Python advisor server
    // (run.py / app.py default to port 8770) so the dashboard works against
    // real live save data without a separate CORS setup.
    proxy: {
      '/api': 'http://127.0.0.1:8770',
    },
  },
  build: {
    outDir: 'dist',
  },
})
