import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({ base: '/web/', plugins: [vue()], test: { environment: 'node' } })
