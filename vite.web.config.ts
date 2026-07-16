/**
 * Standalone Vite config for the **web build** of ChemThisTry.
 *
 * The Electron app is built by `electron-vite` using `electron.vite.config.ts`.
 * This file is a SEPARATE, independent config used only by `npm run dev:web`
 * and `npm run build:web`. It compiles the *renderer* (`src/`) into a pure
 * static bundle (no Electron, no native modules) that can be served from any
 * web server.
 *
 * How the web build stays Electron-compatible with zero renderer changes:
 *   The renderer never imports `electron` directly — it talks to the native
 *   layer solely through `window.electron.ipcRenderer`. In the browser we
 *   install a drop-in "web bridge" (`src/web-bridge.ts`) before React mounts
 *   that implements the same `{ send, invoke, on }` surface and proxies the
 *   chemistry/science channels to a lightweight FastAPI backend (see server/).
 *   See src/bootstrap.ts and docs/DEPLOY.md.
 */
import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // Root is the renderer source directory, same as the electron-vite renderer.
  root: 'src',
  // Relative base so the bundle works from any sub-path or static host.
  base: './',
  resolve: {
    alias: {
      '@renderer': resolve(__dirname, 'src'),
    },
  },
  define: {
    // Some third-party libs (ketcher-react) reference `global` at eval time.
    global: 'globalThis',
  },
  build: {
    // Output to <project>/dist-web so it never collides with the Electron
    // build output (out/) or electron-vite's dist/.
    outDir: resolve(__dirname, 'dist-web'),
    emptyOutDir: true,
    commonjsOptions: {
      transformMixedEsModules: true,
    },
    rollupOptions: {
      // 3dmol (3D molecular viewer) uses `eval` internally for dynamic
      // parsing. esbuild warns about it but does NOT rewrite it, so the
      // minified bundle still works at runtime. Silence only this expected,
      // harmless warning to keep the build log clean.
      onwarn(warning, warn) {
        const msg = warning.message || ''
        if (/use of eval/i.test(msg) && /3dmol/i.test(msg)) return
        warn(warning)
      },
      input: {
        index: resolve(__dirname, 'src/index.html'),
      },
    },
  },
  server: {
    port: 5173,
    // Avoid clashing with the Electron dev server if both are running.
    strictPort: false,
  },
  plugins: [react()],
})
