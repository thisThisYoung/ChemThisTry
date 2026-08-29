# ChemThisTry 部署教程（官网 + 网页版 + 可选后端）

本教程说明如何把 **ChemThisTry 官网（Astro 静态站）** 与 **网页版（Vite SPA）** 打包、上传到 Linux 服务器，并通过 nginx 对外提供 HTTPS 服务。可选接入 **Python 后端容器**，提供分子 3D 优化、结构转 SVG、ASE 晶体导出、曲线拟合等 `/api` 计算能力。

部署全程由仓库内脚本驱动，nginx 配置以 `server/nginx-ctt.conf.example` 为单一来源、用 `sed` 替换占位符 `app.your-domain.com` / `www.your-domain.com`，**不要手工另写一份 nginx 配置**。

> 适用版本：v0.1.4（2026-08）。当前构建未签名、源码门面仓库仅发布二进制，与文档一致。

---

## 1. 部署架构一览

```
                          ┌─────────────────────────────────────┐
   浏览器                 │            nginx (443 / 80)            │
  www.example.com ──────▶│  server A: 官网静态 (website/dist)     │
  app.example.com  ─────▶│  server B: 网页版 SPA (dist-web)        │
                         │  location /api/ ──proxy──▶             │
                         │        127.0.0.1:8000                 │
                         └──────────────┬────────────────────────┘
                                        │
                                 ┌──────▼──────┐
                                 │ ctt-backend │  (Docker, 仅可选计算 API)
                                 │  uvicorn:8000│
                                 └─────────────┘
```

两个站点同一份 nginx 配置（`nginx-ctt.conf.example`，含两个 `server` block），由脚本一次签发、共用一张证书。

| 部分 | 域名示例 | 产物目录 | 是否必须 | 说明 |
|------|----------|----------|----------|------|
| 官网 | `www.example.com` | `website/dist/` | 是（品牌站） | 中英双语落地页，纯静态 |
| 网页版 | `app.example.com` | `dist-web/` | 是（核心应用） | 纯前端 SPA，`base:'./'`，可放任意路径 |
| 后端 | （同源 `/api`） | `server/`（Docker） | 否 | 提供 `/api` 化学计算；不部署则网页版降级为内置 Pyodide 路线（2D/作图可用，拟合/ASE/EPS 等不可用） |

> 网页版与桌面版共享同一份代码；网页版**不启动原生 Python 侧车**，故曲线拟合 / ASE 结构导出 / EPS 矢量导出在缺后端时不可用，其余作图、结构、3D 与画布功能一致。

---

## 2. 前置条件

- 一台 Linux 服务器（Ubuntu 22.04 验证通过，其他发行版命令略作调整）。
- 已备案域名（或同域子路径方案，见 §6 备选）：
  - `app.example.com` → 网页版
  - `www.example.com` → 官网
- 服务器已装 `nginx`、`certbot`（含 `python3-certbot-nginx`）、`docker` + `docker compose`、 `rsync`，并已放行 80 / 443 入站。
- 本机（构建机）Node.js ≥ 18（本工程在 Node 22 验证），npm ≥ 9，且 `ssh` 公钥已加入服务器、本地有 `rsync`。

```bash
# 服务器上安装基础组件（Ubuntu）
sudo apt update
sudo apt install -y nginx rsync
sudo apt install -y certbot python3-certbot-nginx
# Docker 安装略（见 https://docs.docker.com/engine/install/）
```

---

## 3. 构建产物（在构建机执行）

在**项目根目录**：

```bash
# 网页版（Vite SPA，产物 dist-web/，约 34MB，含 KaTeX/Pyodide）
NODE_OPTIONS="--max-old-space-size=8192" npm run build:web

# 官网（Astro 静态站，产物 website/dist/）
cd website && npm install && npm run build && cd ..
```

- 网页版是 SPA，`base:'./'` 相对路径，nginx 需开启 SPA fallback（`try_files $uri $uri/ /index.html`）。
- 官网为 Astro 静态输出，含根 `index.html` 及 `/zh/`、`/en/` 子目录，nginx 用 `try_files $uri $uri/ =404` 即可。

---

## 4. 部署（脚本主线，推荐）

仓库已提供两套脚本，二者共用 `server/nginx-ctt.conf.example` 与占位符替换逻辑，**任选其一**：

### 4.1 本地一键部署（推荐日常使用）

在构建机、项目根目录运行，脚本会：本机构建两站 → rsync 到服务器 → 服务器端起后端 / 写 nginx / 签证书。

```bash
SERVER=user@1.2.3.4 DOMAIN=app.example.com EMAIL=you@example.com \
  ./scripts/deploy-web.sh
```

- `DOMAIN` = 网页版域名（如 `app.example.com`）。
- `WWW_DOMAIN` 可省略，默认 `www.<DOMAIN 去掉首个子域>`（即 `app.example.com` → `www.example.com`）。如需自定义官网域名，显式传 `WWW_DOMAIN=www.foo.com`。
- 可选覆盖目录：`REMOTE_SERVER_DIR`（默认 `/opt/ctt/server`）、`REMOTE_WEB_ROOT`（默认 `/var/www/chemthistry/dist-web`）、`REMOTE_WWW_ROOT`（默认 `/var/www/chemthistry/website/dist`）。

### 4.2 服务器解压后部署

若走发布包（见 §7 的 `ctt-deploy-0.1.3.zip`），在服务器解压后、`deploy-server.sh` 所在目录运行：

```bash
sudo ./deploy-server.sh app.example.com you@example.com
# 或显式指定官网域名：
sudo ./deploy-server.sh app.example.com you@example.com www.example.com
```

脚本会同步 `dist-web/` 与 `website/dist/` 到发布目录、起后端、写并启用 nginx 配置、签证书。

> 两种脚本都做了同一件事：用 `sed` 把 `nginx-ctt.conf.example` 里的 `app.your-domain.com` / `www.your-domain.com` 换成真实域名，复制为 `/etc/nginx/sites-available/ctt.conf` 并软链到 `sites-enabled/`，再用 `certbot --nginx` 一次签发两张域名共用的证书。

---

## 5. nginx 配置说明（源自 `nginx-ctt.conf.example`）

脚本写入的 `/etc/nginx/sites-available/ctt.conf` 由仓库示例生成，包含两个 `server` block，均 `listen 443 ssl`：

```nginx
# ===== 官网：www.example.com（Astro 纯静态）=====
server {
    listen 443 ssl;
    server_name www.example.com;
    root /var/www/chemthistry/website/dist;
    index index.html;
    location / { try_files $uri $uri/ =404; }
    # ssl_certificate* 由 certbot 注入
}

# ===== 网页版：app.example.com（Vite SPA + /api 反代）=====
server {
    listen 443 ssl;
    server_name app.example.com;
    root /var/www/chemthistry/dist-web;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }   # SPA fallback
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 16m;
    }
    # ssl_certificate* 由 certbot 注入
}
```

- 占位符约定：`www.your-domain.com` 与 `app.your-domain.com` 仅用于 `sed` 替换，部署后即被真实域名覆盖。
- 80 → 443 跳转由 `certbot --nginx --redirect` 自动写入，无需手工加。
- Pyodide 多线程需 SharedArrayBuffer 时才加 COOP/COEP 头（默认留空更稳，详见 §9）。

**备选：同域子路径方案**（不想用两个子域时）。把 `website/dist/` 放到 `/var/www/chemthistry/website/dist/`，`dist-web/` 放到 `/var/www/chemthistry/website/dist/app/`，在官网 server block 内加：

```nginx
location /app/ { try_files $uri $uri/ /app/index.html; }
```

`dist-web` 用 `base:'./'` 已兼容子路径；但 API 反代与 Pyodide Worker 路径在子路径下需额外校验，新手建议用上面的双子域方案。

---

## 6. 启用 HTTPS（certbot，脚本自动）

脚本已自动执行，这里给出手工等价命令便于排错：

```bash
sudo certbot --nginx -d app.example.com -d www.example.com \
  --non-interactive --agree-tos --redirect -m you@example.com
```

certbot 会改写对应 `server` block 注入证书路径与 80→443 跳转。证书 90 天自动续期（系统 timer 默认开启）。

---

## 7. 可选：后端 Docker 部署（提供 /api 计算）

仅当需要分子 3D 优化、结构转 SVG、ASE 晶体导出、曲线拟合等能力时部署。镜像内已自带 libcairo/pango/RDKit，宿主机**无需**安装任何系统库。脚本部署时已自动 `docker compose up -d --build`；如需单独操作：

```bash
cd /opt/ctt/server            # 或发布包里的 server/
sudo docker compose up -d --build
```

- 端口只绑 `127.0.0.1:8000`，由 nginx 反代，不对外直露。
- `CORS_ORIGINS`（`docker-compose.yml`）：网页版走同源反代本不需要；但鸿蒙 ArkWeb 页面源为 opaque，访问 `https://app.example.com/api` 算跨域，必须包含前端域名（如 `"https://app.example.com"`）。
- 高负载时取消 `docker-compose.yml` 中 `--workers 4` 注释，开多 worker。

后端 API 一览（已就绪）：

| 方法 | 路径 | 作用 |
|------|------|------|
| GET  | `/api/health`      | 健康检查 |
| POST | `/api/optimize3d`  | 分子构象 3D 优化（RDKit ETKDGv3 + MMFF/UFF） |
| POST | `/api/molToSvg`    | 分子转 SVG（cairosvg） |
| POST | `/api/exportStruct`| 结构导出（ASE，含多格式） |
| POST | `/api/fit`         | 曲线拟合（scipy 模型） |
| POST | `/api/convertVector` | 矢量格式转换 |

> 不部署后端时，网页版在「设置 → 后端服务地址」留空即可，自动降级；相关高级功能按钮在 Web 端会被禁用（已在代码中 gating）。

---

## 8. 验证清单

1. 打开 `https://www.example.com` → 看到中英双语官网，HTTP 自动跳 HTTPS。
2. 打开 `https://app.example.com` → 网页版加载，能新建工程、作图、画结构。
3. （若部署后端）网页版「设置 → 后端服务地址」留空；在结构页点 3D 优化 / 拟合，网络面板出现 `200 /api/...` 请求。
4. `sudo nginx -t` 无报错；`sudo systemctl status nginx` 为 active。
5. `sudo docker compose ps`（若用后端）显示 `ctt-backend` 为 `Up`。

---

## 9. 故障排查

| 现象 | 原因 / 处理 |
|------|-------------|
| 网页版刷新子路由 404 | nginx 缺少 `try_files ... /index.html`；SPA 必须加 fallback（脚本已含） |
| 官网打开 404 / 样式丢失 | `website/dist/` 未同步完整，或 nginx root 指错到 `dist-web`；确认 root 为 `/var/www/chemthistry/website/dist` |
| `/api/*` 返回 502 | 后端未启动或端口不符；`docker compose ps` 确认 `ctt-backend` Up，且 nginx `proxy_pass` 指向 `127.0.0.1:8000` |
| 网页版 3D 优化报错 CORS | `docker-compose.yml` 的 `CORS_ORIGINS` 未包含前端域名；修改后 `docker compose up -d` |
| Pyodide 加载失败 / SharedArrayBuffer 报错 | 默认不启用 COOP/COEP；如确需 Pyodide 多线程，在 nginx 加 `Cross-Origin-Opener-Policy: same-origin` 与 `Cross-Origin-Embedder-Policy: require-corp`，但所有子资源（含 CDN 的 Pyodide）必须带宽松 CORS 头，否则会更难调试——默认**留空更稳** |
| 证书签不下来 | 检查 DNS 是否指向本机、80 端口是否被占用；`sudo certbot renew --dry-run` 排查续期 |
| certbot 只签了一个域名 | 确认两个 `server_name` 占位符都已 `sed` 替换；`grep server_name /etc/nginx/sites-enabled/ctt.conf` 应出现 `app.example.com` 与 `www.example.com` |

---

## 10. 目录速查

```
ChemThisTry/                      # 仓库根
├─ website/                       # 官网（Astro）
│  ├─ src/pages/{index,zh/index,en/index}.astro
│  └─ dist/                       # ← 构建产物（§3），上传到服务器 website/dist
├─ dist-web/                      # 网页版（Vite SPA，§3），上传到服务器 dist-web
├─ server/                        # 可选后端
│  ├─ main.py / chem_ops.py       # FastAPI 应用与化学计算
│  ├─ Dockerfile / docker-compose.yml / requirements.txt
│  └─ nginx-ctt.conf.example      # nginx 参考（官网+网页版+API，脚本单一来源）
├─ scripts/
│  ├─ deploy-web.sh               # 本地一键部署（构建+上传+签证书）
│  └─ deploy-server.sh            # 服务器端部署（解压包内运行）
└─ DEPLOY.md                      # 本教程
```

命令速记：

```bash
# —— 日常：本地一键（推荐）——
SERVER=user@1.2.3.4 DOMAIN=app.example.com EMAIL=you@example.com ./scripts/deploy-web.sh

# —— 走发布包：服务器解压后 ——
sudo ./deploy-server.sh app.example.com you@example.com

# —— 仅重新构建 ——
NODE_OPTIONS="--max-old-space-size=8192" npm run build:web
cd website && npm install && npm run build && cd ..
```

发布包（可选，便于离线分发）示意：

```bash
zip -r ctt-deploy-0.1.4.zip website/dist dist-web server scripts DEPLOY.md
# 服务器：unzip 后进入目录 sudo ./deploy-server.sh app.example.com you@example.com
```

---

## 11. 桌面版从源码构建（Windows / Linux）

本仓库为门面仓库，源码不随 git 发布，桌面安装包以二进制形式分发。若需在 **Windows / Linux** 上自行构建桌面应用，请使用官方源码包（如 `ChemThisTry-src-0.1.4-win-linux.tar.gz`），在**目标 OS 本机**执行以下步骤。

> ⚠️ 原生模块 `better-sqlite3` **不能交叉编译**。必须在 Windows 本机构建 Windows 包、Linux 本机构建 Linux 包；在 macOS 上试图 `dist:win` / `dist:linux` 会被 `electron-builder.js` 直接拒绝（除非已自备目标平台预编译原生二进制并设置 `CTT_ALLOW_CROSSBUILD=1`）。

### 11.1 前置条件
- **Node.js** ≥ 20（工程在 Node 22 验证），npm ≥ 9。
- **原生编译工具链**（用于重编 `better-sqlite3`）：
  - Windows：Python 3 + Visual Studio Build Tools（勾选「使用 C++ 的桌面开发」）。
  - Linux（Debian/Ubuntu）：`sudo apt install python3 make g++`；构建 AppImage 另需 `libfuse2`（`sudo apt install libfuse2`）。
- `.npmrc` 已设 npmmirror 镜像，`npm install` 时 Electron 与 electron-builder 的二进制走国内镜像加速，无需翻墙。

### 11.2 构建步骤

**Windows（必须用 Git Bash 运行）**：
```bash
# 解包
tar -xzf ChemThisTry-src-0.1.4-win-linux.tar.gz -C ~/ctt-build && cd ~/ctt-build
# 安装依赖（会重编 better-sqlite3 原生 .node）
npm install
# 构建并打包（x64 NSIS）
npm run dist:win
# 产物：release/ChemThisTry Setup 0.1.4.exe
```

**Linux（终端）**：
```bash
tar -xzf ChemThisTry-src-0.1.4-win-linux.tar.gz -C ~/ctt-build && cd ~/ctt-build
npm install
npm run dist:linux
# 产物：release/ChemThisTry-0.1.4.AppImage 与 chemthistry_0.1.4_amd64.deb
```

### 11.3 离线构建说明
源码包内已含 `pyodide-dist/`（约 50MB，离线 Python 运行时）。`prebuild` 钩子 `scripts/fetch-pyodide.mjs` 检测到目标文件已存在会**跳过下载**，因此**无外网也能构建**；有外网时脚本会自动补全缺失文件。

### 11.4 其它
- 产物版本号取自 `package.json` 的 `version`（本包为 `0.1.4`）。
- macOS 包可在此 macOS 主机直接用 `npm run dist:mac` 构建（原生模块在本机编译，无交叉问题）。
- 网页版与桌面版共享同一份代码，构建方式见 §3。
