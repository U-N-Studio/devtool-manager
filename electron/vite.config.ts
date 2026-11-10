import { defineConfig } from 'vite'
import electron from 'vite-plugin-electron'

export default defineConfig({
  plugins: [
    electron([
      {
        entry: 'main/main.ts',
        vite: { build: { outDir: 'dist-electron', rollupOptions: { external: ['electron'] } } },
        onstart: () => {},
      },
      {
        entry: 'preload/preload.ts',
        vite: { build: { outDir: 'dist-electron', rollupOptions: { external: ['electron'] } } },
      },
    ]),
  ],
})
