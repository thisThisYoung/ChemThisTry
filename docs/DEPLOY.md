# ChemThisTry — Web Deployment Guide

This document explains how to run the **web version** of ChemThisTry on a server.
The web build reuses the exact same React renderer as the desktop Electron app —
no renderer code was forked. The only difference is that, instead of talking to
the Electron main process, the renderer talks to a small **FastAPI backend**
that runs the same RDKit / cairosvg / scipy / ASE code paths as the desktop
sidecar.

> **Feature parity.** Because the web build compiles the *same* `src/` renderer
> as the desktop app, it automatically includes every renderer-side feature —
> including the recent **Preferences** expansion (graph / export defaults,
> keyboard-shortcut reference, About tab, grouped searchable navigation) and the
> **Help → About** page. The only differences between the two builds are the
> native bridge (Electron main process vs. the FastAPI backend) and project
> storage (`.ctt` SQLite file vs. browser `localStorage`).

```
┌────────────────────┐         HTTP/JSON          ┌──────────────────────────┐
│  Browser (static)  │  chem:* / molecule:*  ───▶  │  FastAPI backend         │
│  dist-web/         │ ◀────────────────────────  │  (RDKit, cairosvg,       │
│  (React + Vite)    │      {ok, ...} / {ok:false} │   scipy, ASE)            │
└────────────────────┘                            └──────────────────────────┘
```

> **Why a backend is required.** The in-browser `@rdkit/rdkit` WASM is
> *MinimalLib* — 2D-only. It cannot do 3D embedding, MMFF/UFF minimization,
> high-fidelity SVG→EPS/PDF (cairosvg), or robust nonlinear fitting (scipy).
> Those run in the backend. Everything else (UI, graphing, Ketcher, 3Dmol,
> Pyodide console) runs in the browser.

---

## 1. Build the web frontend

```bash
# from the project root
npm run build:web     # outputs to dist-web/  (needs NODE_OPTIONS heap on big machines)
```

`build:web` uses `vite.web.config.ts` (independent of `electron.vite.config.ts`).
It produces a pure static bundle in `dist-web/`. **No Electron or native modules
are involved**, so it builds on any machine with Node 18+.

For local development without a production build:

```bash
npm run dev:web       # Vite dev server on http://localhost:5173
```

> If the build runs out of memory, raise the heap (the Electron build already
> does this): `NODE_OPTIONS="--max-old-space-size=8192" npm run build:web`.

---

## 2. Run the backend

The backend lives in `server/`. Two options:

### Option A — Python + uvicorn (any host with Python 3.11+)

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
# or:  python main.py
```

`requirements.txt` pulls `rdkit-pypi`, `cairosvg`, `scipy`, `ase`, plus
FastAPI/uvicorn. `cairosvg` needs the system **libcairo** (and pango); on Debian/
Ubuntu install `libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0`
first. Verify with `GET /api/health` → it reports which capabilities are live.

### Option B — Docker (recommended for servers)

```bash
cd server
docker build -t chemthis-backend .
docker run -d --name ctt-backend -p 8000:8000 \
  -e CORS_ORIGINS="https://your-frontend.example.com" \
  chemthis-backend
```

The Dockerfile is based on `python:3.11-slim` and installs libcairo + pango, so
RDKit / cairosvg / ASE all work out of the box.

### Capability map (what each endpoint does)

| Endpoint             | Backend capability | Frontend channel(s)                |
|----------------------|--------------------|------------------------------------|
| `GET  /api/health`   | probe              | `chem:ping`                        |
| `POST /api/optimize3d` | RDKit             | `molecule:optimize3d`              |
| `POST /api/molToSvg` | RDKit              | `chem:molToSvg`                    |
| `POST /api/exportStruct` | ASE            | `molecule:exportStruct`            |
| `POST /api/fit`      | scipy              | `chem:fit`                         |
| `POST /api/convertVector` | cairosvg      | `chem:convertVector` (EPS/PDF/PNG/TIFF) |

If the backend (or a capability) is unavailable, each call returns
`{ "ok": false, "error": "..." }` and the UI degrades gracefully (e.g. EPS export
is disabled, the curve-fit panel shows the error). The frontend never crashes.

---

## 3. Connect frontend ↔ backend

By default the web bridge calls the backend at a **relative** path (`/api/...`),
so the simplest setup is to serve the static files and proxy `/api` to the
backend on the **same origin** (see nginx/Caddy below). No CORS needed.

To put the frontend and backend on **different origins** (e.g. a CDN for static
assets + a separate API host), set the base URL via the `VITE_API_BASE`
environment variable **at build time**:

```bash
VITE_API_BASE="https://api.your-domain.com" npm run build:web
```

and allow that origin with `CORS_ORIGINS` on the backend.

---

## 4. nginx (static + reverse proxy)

```nginx
server {
    listen 443 ssl;
    server_name app.your-domain.com;

    # static frontend
    root /var/www/chemthistry/dist-web;
    index index.html;

    # SPA: let the client router handle unknown paths
    location / {
        try_files $uri $uri/ /index.html;
    }

    # proxy chemistry/science API to the FastAPI backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # increase for large structure exports
        client_max_body_size 16m;
    }
}
```

Serve over **HTTPS** (Let's Encrypt / certbot). Browsers require a secure context
for many features (clipboard, SharedArrayBuffer, file downloads in some cases).

### Optional: Pyodide / SharedArrayBuffer

The in-app Python console (ConsolePanel) loads Pyodide from a CDN. Pyodide can
use a multi-threaded runtime that needs `SharedArrayBuffer`, which browsers only
expose when the page is served with:

```nginx
add_header Cross-Origin-Opener-Policy same-origin;
add_header Cross-Origin-Embedder-Policy require-corp;
```

If you don't need threads, **omit these headers** — Pyodide then runs
single-threaded, which works without them. Adding COEP also requires that every
sub-resource (including the CDN Pyodide scripts) send permissive CORS headers;
if you see Pyodide load failures, leave COOP/COEP off.

---

## 5. Caddy (alternative)

```caddy
app.your-domain.com {
    root * /var/www/chemthistry/dist-web
    encode gzip
    file_server
    try_files {path} /index.html

    reverse_proxy /api/* 127.0.0.1:8000
}
```

---

## 6. Server sizing

| Scenario                         | CPU      | RAM        | Disk     | Notes |
|----------------------------------|----------|------------|----------|-------|
| **Frontend only** (static)       | 1 vCPU   | 512 MB–1 GB| 5 GB+    | No backend; RDKit/ASE/EPS unavailable. Curve fit via Pyodide if enabled. |
| **+ Backend (recommended)**      | 2 vCPU   | 2–4 GB     | 10 GB+   | Full feature parity with desktop (RDKit, cairosvg, scipy, ASE). |
| **Heavy / shared multi-user**    | 4 vCPU   | 8 GB       | 20 GB+   | Run multiple uvicorn workers (`--workers 4`) behind the proxy. |

The backend is **stateless** (no DB, no session) — it only transforms the JSON
you send it — so it scales horizontally behind a load balancer trivially.

---

## 7. Project storage in the browser

The web build stores projects in the browser's **localStorage** (keyed
`chemthis.project:<timestamp>`), not in a `.ctt` SQLite file. `Save` / `Open` /
`Recent` therefore work per-browser and do not travel to the server. To move a
project between the web and desktop apps, use the JSON export, or open the
`.ctt` in the desktop app (the desktop reader also accepts legacy JSON
envelopes).

---

## 8. Quick local check

```bash
# terminal 1 — backend
cd server && uvicorn main:app --port 8000 --reload

# terminal 2 — frontend (dev)
npm run dev:web          # http://localhost:5173  (Vite proxies nothing;
                          # the bridge calls /api on :8000 via CORS —
                          # set CORS_ORIGINS=http://localhost:5173)

# or serve the production build:
npm run build:web
npx serve dist-web       # then point nginx/caddy at it
```

Open `/api/health` in a browser to confirm the backend capabilities are live.

---

## 9. Mobile & responsive

ChemThisTry's web build is **responsive** and installable as a PWA. The desktop
Electron app stays desktop-optimized (it ignores all of the below), but the same
`src/` renderer automatically switches to a phone layout in the browser.

### How it works
Because most of the layout is set via React **inline styles** (which CSS media
queries cannot override), the switch is driven in JS by a `useResponsiveStore`
(`src/store/responsiveStore.ts`) that listens to `matchMedia('(max-width: 768px)')`
and a touch-capability probe (`ontouchstart` / `navigator.maxTouchPoints` /
`(pointer: coarse)`). When `isMobile` is true:

- **Workspace** (`WorkspaceRoot.tsx`) stacks panes **vertically** and hides the
  drag-to-resize splitter.
- **MainLayout** swaps the desktop `MenuBar` for a `MobileTopBar` (menu /
  console / commands / settings / help buttons, all ≥ 44 px). The
  `ProjectExplorer` becomes a **left drawer** and the `ConsolePanel` a
  **bottom drawer**, opened from the top bar over a dimmed overlay.
- **ViewerFrame** turns its left toolbox and right panel into **drawers** (CSS
  `.viewer-frame.is-mobile` rules in `src/index.css`); the inline width is left
  `undefined` so CSS can size them.
- **Dialogs / modals** (Preferences, Help/About, and the `.pref-*` / `.help-*`
  shells) render **full-screen** under `@media (max-width: 768px)`.
- **Tap targets** (tool buttons, icon buttons, explorer actions, inputs) are
  bumped to ≥ 40–44 px and inputs use `font-size: 16px` to stop iOS zoom;
  toolbars scroll horizontally instead of wrapping.
- **Touch gestures**: `Canvas.tsx` (Fabric 6) intercepts one-finger pan only
  when the touch misses objects (otherwise Fabric handles select/move) and
  two-finger pinch-zoom / pan; `Moleculer.tsx` (3Dmol) gets one-finger rotate
  and two-finger pinch-zoom / pan. Both are gated on `isTouch`.

Heavy authoring (Ketcher structure drawing, Canvas vertex editing, large
spreadsheet edits) stays desktop-oriented; the phone target is *view + light
editing*, not full parity.

### PWA / installable
The web build ships a manifest, service worker, and icon in `src/public/`:

- `src/public/manifest.webmanifest` — name, `display: standalone`, theme
  `#0f172a`, icon `./icon.svg`.
- `src/public/sw.js` — cache `ctt-v1`; navigations are network-first falling
  back to `./index.html`, same-origin static GETs are cache-first, API /
  cross-origin requests pass through uncached.
- `src/public/icon.svg` — 512×512 atom/molecule mark.

Vite copies `src/public/` verbatim to `dist-web/` (root is `src`, so the default
`publicDir` resolves there). `src/pwa.ts` injects `<link rel="manifest">` plus a
theme-color meta and registers the SW **only when `window.__CTT_IS_WEB__` is
true** — i.e. it is a complete no-op inside the Electron app, so the desktop
build never registers a service worker. Serve `dist-web/` over HTTPS and the app
is installable to a phone home screen.
