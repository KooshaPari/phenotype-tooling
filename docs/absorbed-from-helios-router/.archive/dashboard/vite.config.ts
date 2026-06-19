import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// @ts-ignore vitest config
export default defineConfig({
  plugins: [react()],
  // @ts-ignore
  test: {
    environment: 'node',
  },
})
