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
      // Emit a single self-contained IIFE so it executes as a classic script.
      // inlineDynamicImports folds the lazy ketcher / 3dmol chunks into one
      // file, removing the runtime `import()` that also fails under file://.
      output: {
        format: 'iife',
        inlineDynamicImports: true,
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
    // ArkWeb (HarmonyOS Web component) loads this bundle from $rawfile via a
    // file://-like context. `<script type="module">` is blocked there by the
    // opaque-origin CORS rule, and `crossorigin` is also refused. Strip BOTH so
    // the emitted script runs as a classic (non-module) script. Harmless for
    // normal browsers.
    {
      name: 'strip-module-crossorigin-for-arkweb',
      // Only strip in BUILD output. The dev server serves native ESM and must
      // keep `type="module"` — ctx.server is defined there, so we skip.
      transformIndexHtml(html, ctx) {
        if (ctx && ctx.server) return html
        return html
          .replace(/\s+type="module"/g, '')
          .replace(/\s+crossorigin(="")?/g, '')
      },
    },
    // Inline the JS (and CSS) bundle directly into index.html for the BUILD
    // output. Under ArkWeb $rawfile (file://, opaque origin) the Web component
    // serves rawfile sub-resources with a MIME/permission quirk that silently
    // blocks external <script src> (no error event, blank page). An INLINE
    // <script> always executes — no fetch, no MIME, no CORS. This makes the
    // HarmonyOS/rawfile build self-contained. (Dev server keeps normal ESM.)
    {
      name: 'inline-bundle-for-arkweb',
      apply: 'build',
      enforce: 'post',
      generateBundle(_options, bundle) {
        const htmlFile = bundle['index.html']
        if (!htmlFile) return
        let htmlSrc =
          typeof htmlFile.source === 'string' ? htmlFile.source : String(htmlFile.source)
        const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        for (const [name, asset] of Object.entries(bundle)) {
          if (asset.type === 'chunk') {
            const re = new RegExp(
              '<script[^>]*src="([^"]*' + esc(name) + ')"[^>]*></script>',
            )
            if (re.test(htmlSrc)) {
              const code = (asset as { code: string }).code.replace(/<\/script>/gi, '<\\/script>')
              htmlSrc = htmlSrc.replace(re, () => '<script>' + code + '</script>')
              delete bundle[name]
            }
          } else if (asset.type === 'asset' && name.endsWith('.css')) {
            const re = new RegExp('<link[^>]*href="([^"]*' + esc(name) + ')"[^>]*>')
            if (re.test(htmlSrc)) {
              const cssSrc = (asset as { source: string | Uint8Array }).source
              const css = typeof cssSrc === 'string' ? cssSrc : Buffer.from(cssSrc).toString('utf8')
              htmlSrc = htmlSrc.replace(re, () => '<style>' + css + '</style>')
              delete bundle[name]
            }
          }
        }
        htmlFile.source = htmlSrc
      },
    },
  ],
})
