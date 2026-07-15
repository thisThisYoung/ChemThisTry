import { resolve } from 'node:path'
import { mkdirSync, copyFileSync, existsSync } from 'node:fs'
import { defineConfig, externalizeDepsPlugin } from 'electron-vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  main: {
    plugins: [
      externalizeDepsPlugin(),
      // Copy the Python RDKit sidecar next to the built main process so the
      // production app can spawn it. (Dev mode runs main from electron/ and
      // finds chem_sidecar.py there automatically.)
      {
        name: 'copy-chem-sidecar',
        closeBundle() {
          const src = resolve(__dirname, 'electron/chem_sidecar.py')
          const dst = resolve(__dirname, 'out/main/chem_sidecar.py')
          if (!existsSync(src)) return
          mkdirSync(resolve(__dirname, 'out/main'), { recursive: true })
          copyFileSync(src, dst)
        },
      },
    ],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'electron/main.ts'),
        },
      },
    },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'electron/preload.ts'),
        },
      },
    },
  },
  renderer: {
    root: 'src',
    resolve: {
      alias: {
        '@renderer': resolve('src'),
      },
    },
    define: {
      global: 'globalThis',
    },
    build: {
      commonjsOptions: {
        transformMixedEsModules: true,
      },
      rollupOptions: {
        // 3dmol (third-party 3D molecular viewer) uses `eval` internally for
        // dynamic parsing. esbuild warns about it, but it is harmless: esbuild
        // does not rewrite `eval`, so the minified bundle still works at runtime.
        // Silence only this specific, expected warning to keep the build log clean.
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
    plugins: [react()],
  },
})
