# 在 Windows 上构建安装包

本文件说明如何把 ChemThisTry 从开发机（macOS / Linux）拷贝到 **Windows 构建机**，编译并打包出可分发、自带 Python 运行时的 NSIS 安装包（`.exe`）。

> 目标产物：`release/ChemThisTry Setup x.x.x.exe`，安装后**无需用户自备 Python**，且 EPS / 矢量 PDF / TIFF 导出开箱可用（cairo 原生依赖已随包内置）。

---

## 0. 重要前提：拷的是本机源码，不是 GitHub

公开的 GitHub 仓库是「门面仓库」，只含 `README.md` / `LICENSE` / `docs/`，**不含 `src/` `electron/` `scripts/` 等源码**（被根目录 `.gitignore` 排除）。

所以请**直接拷贝本机的项目目录**，不要 `git clone` 公开仓库（那样什么源码都没有）。

---

## 1. 从开发机拷贝（排除可重新生成的目录）

以下目录要么平台相关需重装、要么是构建产物，**不要拷**，可省约 7.9 GB：

| 目录 | 原因 |
|------|------|
| `node_modules/` | 原生模块（better-sqlite3）必须 Windows 重装 |
| `release/` | 以往构建产物 |
| `out/` `dist/` | 构建输出，自动重生（由 electron-vite / electron-builder 重新生成） |
| `pyodide-dist/` | 由 `fetch-pyodide` 脚本下载 |
| `.workbuddy/` | 项目记忆，构建不需要 |
| `.git/` | 可选，不拷也行 |

> ⚠️ **`build/` 必须带上，切勿排除。** 它是 electron-builder 的资源目录（应用图标 `build/icon.ico` / `build/icon.icns`、`build/entitlements.mac.plist`），**不是**构建产物。若排除它，Windows 打包出的安装包会退回默认 Electron 图标（窗口 / 任务栏 / 开始菜单全是 atom），macOS 构建也会缺签名文件。下面的 rsync / zip 命令已默认包含 `build/`。

### macOS 源机（推荐 rsync）

```bash
rsync -a --exclude=node_modules --exclude=out --exclude=dist \
  --exclude=release --exclude=pyodide-dist \
  --exclude=.workbuddy --exclude=.git \
  /path/to/ChemThisTry/ /Volumes/你的U盘/ChemThisTry/
```

### 或打成 zip

```bash
cd /path/to/ChemThisTry
zip -r ~/Desktop/ChemThisTry-win.zip . \
  -x 'node_modules/*' 'out/*' 'dist/*' \
     'release/*' 'pyodide-dist/*' '.workbuddy/*' '.git/*'
```

拷到 Windows 后解压到任意位置，例如 `D:\ChemThisTry`。

---

## 2. Windows 构建机 prerequisites

1. **Node.js 22.x** — 从 https://nodejs.org 安装，勾选 *Add to PATH*。
2. **PowerShell** — Windows 10/11 自带，打包脚本用它解压。
3. **磁盘 ≥ 10 GB 空闲** — node_modules ~2 GB + resources/python ~0.6 GB + 构建中间产物。
4. **联网** — 打包脚本需从 python.org / msys2 / pypi 下载；`npm install` 需装 electron 及依赖。
5. （兜底，通常不需要）若 `npm install` 时 better-sqlite3 报 node-gyp / prebuild 错误：
   安装 **Visual Studio Build Tools 2022**（勾选 *使用 C++ 的桌面开发*）+ **Python 3.11**（加入 PATH），再重跑 `npm install`。

> 说明：打包脚本会**自行下载 embeddable Python** 给侧车用，不需要你在 Windows 上预装 Python；上面的 Python 仅用于兜底编译 better-sqlite3。

---

## 3. 构建步骤（Windows PowerShell）

```powershell
cd D:\ChemThisTry

# 1. 安装依赖
npm install

# 2. 生成自带 Python 运行时（联网，约 10–20 分钟）
node scripts/bundle-python-win.mjs
#    成功标志：打印 "cairosvg+rdkit+scipy+ase+PIL OK"，且 resources\python 已生成

# 3. 打包 Windows 安装包
#    （内部自动执行 electron-vite build + electron-builder，并把 resources\python 打进安装包）
npm run dist:win
```

产物位于 **`release/`** 目录：`ChemThisTry Setup x.x.x.exe`。

---

## 4. 常见问题

### 4.1 `ELECTRON_MIRROR` 镜像

`package.json` 里 `dist:win` 写死了国内镜像：

```
ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
```

- Windows 机**在国内**：保持不动即可。
- Windows 机**在国外**：该镜像可能连不上，反而变慢/失败。把 `dist:win` 里 `ELECTRON_MIRROR=...` 这一段删除后再跑。

### 4.2 脚本只能在 Windows 运行

`scripts/bundle-python-win.mjs` 开头检测 `process.platform !== 'win32'` 会直接 `exit(1)`。
因此**拷贝阶段在 macOS 跳过这步**，到 Windows 再执行。正确顺序：`npm install → bundle → dist:win`。

### 4.3 better-sqlite3 编译失败

报错含 `node-gyp` / `prebuild` / `MSBuild` → 见第 2 节第 5 条，安装 VS Build Tools + Python 3.11 后重跑 `npm install`。

### 4.4 只想出小安装包、让用户自己装 Python

跳过第 3 步的 `node scripts/bundle-python-win.mjs`，直接 `npm run dist:win`。
安装包更小，但用户机需自备 Python（且 `pip install rdkit-pypi cairosvg scipy`），否则侧车 import 失败（会有清晰报错，非致命）。

---

## 5. 架构说明（为何只能 x64）

- `rdkit-pypi` 仅有 amd64 wheel。
- MSYS2 的 cairo DLL 仅 amd64。
- Windows 目标已在 `electron-builder.js` 中设为 `x64 only`（已去除 `arm64`）。

arm64 Windows 暂无法自带可用的内置 Python。

---

## 6. 排错：Anaconda / conda 干扰 npm

**症状**：`npm install` 在 `better-sqlite3` 的 install 脚本处崩溃，报
`Cannot find module 'D:\anaconda3\Library\e\<项目路径>\node_modules\prebuild-install\bin.js'`
（路径被拧成 `D:\anaconda3\Library\` + `e\...`，drive 字母被当成相对目录）。

**原因**：conda 把 npm 的 `prefix` 设成了 `D:\anaconda3\Library`，而项目在另一块盘（如 `E:\`）。npm 在 Windows 上跨盘拼模块路径时会拼坏，导致找不到 `prebuild-install` / `node-gyp`。**这不是 ketcher 的 EBADENGINE 警告造成的**（那只是一条警告，Node 22 可正常运行 ketcher 3.15.0）。

**解决**：
1. 关闭当前终端，开一个**没有 conda** 的 PowerShell / cmd（不要 Anaconda Prompt，不要 `conda activate` 过的 shell）。
2. 确认用的是 nodejs.org 的 Node：
   ```powershell
   where.exe node          # 应指向 C:\Program Files\nodejs\
   node -v                 # v22.23.1
   npm config get prefix   # 不能是 D:\anaconda3\...，应为 C:\Users\<你>\AppData\Roaming\npm
   ```
   若仍指向 anaconda，连跑几次 `conda deactivate` 或从 PATH 移除 `D:\anaconda3\...` 相关条目。
3. 清理并重装：
   ```powershell
   cd <项目目录>
   Remove-Item -Recurse -Force node_modules
   npm install
   ```
4. 若 `prebuild-install` 因 GitHub 网络不通而退到 `node-gyp rebuild`，按第 2 节第 5 条装 VS Build Tools 2022 + Python 3.11 后重装。

**后续必做**：`npm install` 把 better-sqlite3 编成了系统 Node 22 的 ABI，但应用运行在 Electron（不同 ABI）。在 `npm run dist:win` 之前先跑一次 `npm run rebuild:native`（`electron-rebuild -f -w better-sqlite3`）重新编译为匹配 Electron 的版本，否则启动可能报「module was compiled against a different version of Node.js」。

