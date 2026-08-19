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
      // Standalone web build flag — always false for the Electron app.
      // JSON.stringify so Vite/esbuild inject a real boolean.
      __CTT_WEB__: JSON.stringify(false),
    },
    optimizeDeps: {
      // Pre-bundle ketcher (lazy-loaded heavy dep) at dev-server startup so its
      // dynamic-import chunk hash stays stable and doesn't break mid-session
      // after a config/package change forces a re-optimize (same fix as web).
      // `ketcher-react`'s entry (`dist/index.js`) does a lazy
      // `import('./index.modern-7545f4b2.js')`; including `ketcher-react` makes
      // Vite pre-bundle that split chunk in the FIRST optimize pass, so the
      // renderer and the on-disk chunk always share one stable hash for the
      // whole session (no second-pass hash flip -> no
      // "Failed to fetch dynamically imported module").
      include: ['ketcher-react', 'ketcher-core', 'ketcher-standalone', 'font-face-observer'],
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
    plugins: [
      react(),
      {
        name: 'ctt-font-face-observer-patch',
        enforce: 'pre',
        // Redirect every `font-face-observer` import/require (Sketcher's import
        // AND ketcher-react's internal require) to our single patch module, so
        // the prototype patch applies to the exact instance Ketcher uses. The
        // patch module itself imports the real package by bare name; we let that
        // resolve normally so Vite pre-bundles it as proper ESM with a `default`
        // export. This avoids the dev-only
        //   "does not provide an export named 'default'"
        // crash that importing the raw CJS src/observer.js produced (build was
        // fine because esbuild synthesized the default export there).
        resolveId(source, importer) {
          if (
            source === 'font-face-observer' &&
            importer &&
            !importer.includes('patches/font-face-observer')
          ) {
            return resolve(__dirname, 'src/patches/font-face-observer.ts')
          }
          return null
        },
      },
    ],
  },
})
