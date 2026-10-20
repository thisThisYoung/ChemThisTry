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
      // Mirror of the Electron renderer alias: the FontFaceObserver patch module
      // (src/patches/font-face-observer.ts) imports the REAL package through this
      // non-colliding specifier. The web build has no redirect plugin, so the
      // patch is never actually loaded here — but defining the alias keeps the
      // shared source graph resolvable if it ever is.
      'font-face-observer-ctt-real': resolve(__dirname, 'node_modules/font-face-observer'),
    },
  },
  define: {
    // Some third-party libs (ketcher-react) reference `global` at eval time.
    global: 'globalThis',
    // Mark this as the standalone web build (browser + Capacitor/iOS app).
    // JSON.stringify so Vite/esbuild inject a real boolean, not the string 'true'.
    __CTT_WEB__: JSON.stringify(true),
    // Ketcher's CJS bundle reads `process.env.NODE_DEBUG` at module-eval time and
    // uses `process.nextTick` / `process.stderr`. Vite only defines
    // `process.env.NODE_ENV`, so bare `process.env.NODE_DEBUG` throws
    // "Cannot read properties of undefined (reading 'NODE_DEBUG')" in the browser.
    // Statically replacing the whole `process.env` object removes every
    // `process.env.*` reference from the bundle; `process.nextTick`/`stderr` are
    // covered separately by the `window.process` shim in src/index.html.
    'process.env': JSON.stringify({ NODE_ENV: 'development' }),
  },
  optimizeDeps: {
    // Pre-bundle the heavy Ketcher packages at dev-server startup. They are
    // only reached via a lazy import (the Sketcher viewer), so without this
    // Vite discovers them mid-session, re-runs the dependency optimizer, and
    // rewrites the chunk hash — the already-loaded page then tries to fetch the
    // stale hash and dev fails with "Failed to fetch dynamically imported
    // module". Forcing them into the initial optimize pass avoids that race.
    include: ['ketcher-react', 'ketcher-core', 'ketcher-standalone'],
  },
  build: {
    // Output to <project>/dist-web so it never collides with the Electron
    // build output (out/) or electron-vite's dist/.
    outDir: resolve(__dirname, 'dist-web'),
    emptyOutDir: true,
    // Classic (non-module) target so the single IIFE bundle runs under
    // file:// / ArkWeb $rawfile, where `<script type="module">` is blocked by
    // the opaque-origin CORS rule and would leave a blank WebView.
    target: 'es2018',
    // No modulepreload links (they are module-only and useless under file://).
    modulePreload: false,
    commonjsOptions: {
      transformMixedEsModules: true,
    },
    rollupOptions: {
      // Emit ES modules with REAL code splitting. The app is already written
      // for this: every heavy viewer (Ketcher / 3Dmol / ECharts / …) is reached
      // through `lazy()` + dynamic `import()` in src/components/workspace/
      // viewerChunks.ts, so Rollup produces one small entry chunk plus separate
      // on-demand viewer chunks. The cold start then only parses/compiles the
      // core (a few MB) instead of the whole ~40 MB single IIFE — this is what
      // makes the HarmonyOS/ArkWeb cold start fast.
      //
      // Previously this was `format: 'iife'` + `inlineDynamicImports: true`,
      // folding everything into ONE classic <script> (the old ~41 MB monolith).
      // Dropping `inlineDynamicImports` gives real code splitting, but ArkWeb
      // STILL cannot fetch ES-module sub-resources from $rawfile (opaque
      // null-origin + `crossorigin` => CORS block => blank WebView), so an
      // onInterceptRequest shim in Index.ets proved unreliable for MODULE
      // sub-resources. The pragmatic fix (harmonyos/sync-web.sh ->
      // scripts/inline-entry-for-arkweb.mjs) inlines ONLY the entry
      // index.js + index.css into index.html, so the cold start makes ZERO
      // external module requests. The heavy viewer chunks stay as on-demand
      // dynamic imports (served lazily; they still need a fetch/intercept path
      // under ArkWeb and are validated separately). Do NOT re-enable
      // inlineDynamicImports — that would also inline the 24 MB Ketcher chunk.
      output: {
        format: 'es',
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name][extname]',
      },
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
  plugins: [
    react(),
    // NOTE: the old `strip-module-crossorigin-for-arkweb` and
    // `inline-bundle-for-arkweb` plugins were removed. They forced a single
    // inlined classic <script> to work around ArkWeb blocking $rawfile sub-
    // resource loads. With real code splitting (format: 'es', no
    // inlineDynamicImports) the build now emits separate chunk files; those are
    // served from rawfile by `onLoadIntercept` in harmonyos/.../Index.ets with
    // the correct MIME + CORS, so neither plugin is needed. Harmless for normal
    // browsers (which serve the chunks as standard ES modules).
  ],
})
