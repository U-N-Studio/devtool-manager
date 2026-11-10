import { defineConfig } from 'vite'
import electron from 'vite-plugin-electron'

export default defineConfig({
  plugins: [
    electron([
      {
        entry: 'main/main.ts',
        vite: {
          build: {
            outDir: 'dist-electron',
            lib: { entry: 'main/main.ts', formats: ['cjs'], fileName: () => 'main.js' },
            rollupOptions: { external: ['electron'] },
          },
        },
      },
      {
        entry: 'preload/preload.ts',
        vite: {
          build: {
            outDir: 'dist-electron',
            lib: { entry: 'preload/preload.ts', formats: ['cjs'], fileName: () => 'preload.js' },
            rollupOptions: { external: ['electron'] },
          },
        },
      },
    ]),
  ],
})
