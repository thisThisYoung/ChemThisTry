# ChemThisTry

跨平台一体化科研绘图工作站，集数据作图、化学结构绘制、3D 分子/晶体可视化与图版排版于一体，并提供可选 Python 侧车用于曲线拟合与 3D 构象优化。A cross-platform scientific graphics workstation unifying data plotting, chemical-structure drawing, 3D molecular / crystal visualization, and figure compositing — with an optional Python sidecar for curve fitting and 3D conformer optimization.

[![Latest release](https://img.shields.io/github/v/release/thisThisYoung/ChemThisTry?label=release)](https://github.com/thisThisYoung/ChemThisTry/releases/latest)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](#下载-download)

<!-- Screenshot placeholder — replace with a real image:
![ChemThisTry main window](assets/screenshot-main.png)
-->

## 功能速览 Features

ChemThisTry 由五个相互联动的模块组成，共享一个无限画布工作区；各模块之间实时联动——修改结构，画布上关联的图形会自动更新。ChemThisTry bundles five linked modules on an infinite-canvas workspace, with live updates between them — edit a structure and the linked figure updates automatically.

### 📊 DataViewer — 电子表格与数据编辑 Spreadsheet & data editor
电子表格式数据编辑器，支持自定义分隔符、公式列、描述统计与绘图控制台，是 GraphViewer 的数据来源。A spreadsheet-style data editor with custom delimiters, formula columns, descriptive statistics, and a plotting console — the data source for GraphViewer.
- 导入 Import: `.csv` · `.tsv` · `.tab` · `.txt` · `.dat` · `.prn`（空格 / 逗号 / 制表符 / 自定义分隔符，支持剪贴板粘贴）(space / comma / tab / custom delimiters, plus clipboard paste)
- 导出 Export: `.csv`

### 📈 GraphViewer — 数据作图 Data plotting
基于 ECharts 的出版级数据图（散点 / 折线 / 柱状等），数据来自 DataViewer 数据集，支持透明背景与出版分辨率导出；曲线拟合由 Python 侧车提供。Publication-quality plots (scatter, line, bar, and more) via ECharts, driven by DataViewer datasets, with transparent backgrounds and print-resolution output; curve fitting is available through the Python sidecar.
- 导出 Export: `.png` · `.svg` · `.pdf` · `.eps`

### ⚗️ Sketcher — 化学结构 2D chemical structures
基于 Ketcher 的分子 / 反应式绘制编辑器，可直接输入 SMILES；一键将结构发送到 Moleculer（3D）或画布。Draw and edit molecules and reactions with a Ketcher-based editor; type SMILES directly and send structures to Moleculer (3D) or the Canvas with one click.
- 导入 Import: `.mol` · `.rxn` · `.sdf` · `.cml` · `.ket` · `.smi` · `.inchi` · SMILES 文本 (SMILES text)
- 导出 Export: `.png` · `.svg` · `.pdf` · `.eps` → Moleculer / → Canvas

### 🧪 Moleculer — 3D 分子与晶体 3D molecules & crystals
基于 3Dmol.js 的 VESTA 风格晶胞与配位多面体，支持超胞扩展、左右手坐标系切换，并可通过 Python 侧车（RDKit）优化构象。VESTA-style unit cells and coordination polyhedra powered by 3Dmol.js, with supercell expansion, handedness switching, and conformer optimization via the Python sidecar (RDKit).
- 导入 Import: `.cif` · `.pdb` · `.xyz` · `.mol` · `.mol2` · `.sdf` · `.pqr` · `.vesta` · `.mlcl` · VASP（`POSCAR` / `CONTCAR`）
- 结构导出 Export structure (ASE): `.pdb` · `.cif` · `.xyz` · extended XYZ · VASP · GEN · CFG
- 图片导出 Export image: `.png` · `.pdf` · 保存 `.mlcl` (save `.mlcl`)

### 🎨 Canvas — 矢量画布排版 Vector figure compositing
在无限画布上排版示意图、流程图、标注与多面板图版；将数据图、结构、3D 快照组合在一起，并与来源模块保持实时联动。Compose schematics, flowcharts, annotations, and multi-panel figures on an infinite canvas, placing plots, structures, and 3D snapshots together while keeping them live-linked to their source modules.
- 导入 Import: 图片 images (`image/*`)
- 导出 Export: `.svg` · `.pdf` · `.eps` · `.png` · `.tiff`

### 🌐 其他 More
- 工程文件 Project file: `.ctt`（基于 SQLite 的工程包 / SQLite-based project bundle）
- 多语言界面 Multilingual UI: 简体中文 · 繁體中文 · English · 日本語 · Français · Español · Dansk
- 首选项 Preferences: 左侧分组导航 + 内容区的主从式设置面板，涵盖外观 / 主题、图表默认、导出默认、快捷键一览、AI 助手、插件；支持顶部搜索定位与分区 / 全局「恢复默认」。A master-detail settings panel (grouped left-side navigation + content area) covering appearance / theme, graph defaults, export defaults, a keyboard-shortcut reference, the AI assistant, and plugins — with a search box and per-section / global "Reset to defaults". On mobile (phone web), the AI / Plugins / Shortcuts tabs are hidden to reduce clutter, leaving only General / Graph / Export / About.
- 帮助中心 Help center: 内置的分节文档（快速上手、各模块指南、疑难排查）与「关于」页（版本号、官网 / 源码链接、许可证、技术栈）。Built-in sectioned documentation (getting started, per-module guides, troubleshooting) plus an About page (version, website / source links, license, tech stack).

## 下载 Download

macOS / Windows / Linux 的预编译安装包发布在 Releases 页面。Pre-built installers for macOS, Windows, and Linux are published on the Releases page.

👉 最新版 Latest: https://github.com/thisThisYoung/ChemThisTry/releases/latest

👉 v0.1.1: https://github.com/thisThisYoung/ChemThisTry/releases/tag/v0.1.1

| 平台 Platform | 文件 File |
|---------------|-----------|
| macOS（Apple Silicon） | `ChemThisTry-0.1.1-arm64.dmg`  ·  `ChemThisTry-0.1.1-arm64-mac.zip` |
| macOS（Intel） | `ChemThisTry-0.1.1.dmg`  ·  `ChemThisTry-0.1.1-mac.zip` |
| Windows | `ChemThisTry-0.1.1.exe` |
| Linux（便携版 portable） | `ChemThisTry-0.1.1.AppImage` |
| Linux（Debian/Ubuntu） | `ChemThisTry-0.1.1.deb` |

下载对应平台的文件按常规安装即可，无需账号或构建步骤。Apple Silicon（M 系列）Mac 用 `-arm64` 版本；Intel Mac 用无芯片后缀的版本。Download the file for your platform and install as usual — no account or build step required. On Apple Silicon Macs use the `-arm64` build; Intel Macs use the file with no arch suffix.

## 首次运行 First launch

当前安装包未签名、未公证，首次打开时系统可能弹出安全提示，属正常现象，不代表文件损坏。The binaries are currently distributed without code-signing / notarization, so your OS may show a security warning on first open — this is expected and does not mean the file is broken.

### macOS（Gatekeeper）
1. 若提示"无法打开，因为无法验证开发者"，先点取消。If a dialog says "ChemThisTry cannot be opened because the developer cannot be verified", click Cancel.
2. 右键（或 Control+点击）应用 → 选打开 → 弹窗中再点打开。Right-click (or Control-click) the app and choose Open, then click Open in the dialog.
3. 若仍被拦截，在终端执行：If it still refuses, run in Terminal:
   ```bash
   sudo xattr -rd com.apple.quarantine /Applications/ChemThisTry.app
   ```

### Windows（SmartScreen）
1. 当出现"Windows 已保护你的电脑"，点更多信息。When SmartScreen shows "Windows protected your PC", click More info.
2. 点仍要运行。Click Run anyway.

### Linux
- **AppImage:** 赋予执行权限后运行。chmod +x then run: `chmod +x ChemThisTry-0.1.1.AppImage`
- **.deb:** 如缺依赖用 `sudo apt-get install -f` 补齐。Install with `sudo dpkg -i ChemThisTry-0.1.1.deb` (resolve deps via `sudo apt-get install -f` if needed).

## Python 侧车 Python sidecar

部分功能——3D 构象优化（Sketcher → Moleculer）、基于 ASE 的结构导出（PDB/CIF/XYZ/VASP）、EPS / 矢量 PDF 导出——需要带 RDKit 与 ASE 的 Python 侧车；可用时状态栏显示 `Python: connected`，其余功能无需侧车即可使用。Some features — 3D conformer optimization (Sketcher → Moleculer), ASE-based structure export (PDB/CIF/XYZ/VASP), and EPS / vector-PDF export — use a Python sidecar with RDKit and ASE; the status bar shows `Python: connected` when available, and everything else works without it.

- **macOS / Linux:** 应用会自动检测 PATH 上的 Python 3.9+，缺依赖时安装：The app auto-detects Python 3.9+ on your PATH; install deps if missing:
  ```bash
  pip install rdkit-pypi ase scipy cairosvg
  ```
  在 Debian/Ubuntu 上也可用 `sudo apt install python3-rdkit python3-scipy`（另加 `pip install cairosvg`）。On Debian/Ubuntu you can instead use `sudo apt install python3-rdkit python3-scipy` (plus `pip install cairosvg`).
- **Windows:** 安装包不含 Python，请从 python.org 安装 Python 3.9+（勾选 Add Python to PATH）后执行：The installer does not bundle Python — install Python 3.9+ from python.org (tick Add Python to PATH), then:
  ```powershell
  pip install rdkit-pypi ase scipy cairosvg
  ```
  > Windows 上 RDKit 包名是 `rdkit-pypi`，不是 `rdkit`；若侧车报 9009 错误，把 `CHEMTHIS_PYTHON` 设为 `python.exe` 的完整路径后重启。On Windows the RDKit package is `rdkit-pypi`, not `rdkit`; if the sidecar fails with exit code 9009, set `CHEMTHIS_PYTHON` to the full path of your `python.exe` and relaunch.

## Web 版与移动端预览 (Web build & mobile preview)

除了桌面安装包，ChemThisTry 还可构建为纯前端 Web 应用，便于在手机浏览器里直接预览、无需安装。The app can also be built as a static web app for quick preview on a phone browser — no install required.

- **构建 Web 版 Build the web build:**
  ```bash
  npm run build:web        # 产物位于 dist-web/
  npx vite preview --config vite.web.config.ts --host --port 4173
  ```
- **手机预览 Preview on phone:** 让手机与电脑处于同一局域网，浏览器打开 `http://<电脑局域网IP>:4173`（例如 `http://192.168.1.20:4173`）；也可部署到 CloudStudio 等静态托管获得公网链接。Connect the phone to the same LAN and open `http://<computer-LAN-IP>:4173`.
- **移动端体验 Mobile experience:** 手机端自动跳过欢迎页、直接载入示例工程；左侧工具箱可上下滚动、顶部工具栏可左右滑动；右上角「文档」按钮可再次点击关闭帮助面板；首选项仅保留 通用 / 图表 / 导出 / 关于 四个分区（AI / 插件 / 快捷键 在移动端隐藏，避免冗余）。On mobile the welcome screen is skipped (the example project loads directly), the left toolbox scrolls vertically, the top toolbar scrolls horizontally, the top-right "document" button toggles the help panel, and Preferences shows only General / Graph / Export / About.

> Web 版与桌面版共享同一份代码；Web 版不启动原生 Python 侧车，故曲线拟合 / ASE 结构导出 / EPS 矢量导出 在 Web 端不可用，其余作图、结构、3D 与画布功能一致。The web build shares the same codebase but does not launch the native Python sidecar, so curve fitting, ASE structure export, and EPS export are unavailable on web.

## 项目状态 Status

- 本仓库为发布 / 门面仓库，分发编译产物与文档；完整源码暂未公开，就绪后将以 Apache-2.0 开源。This repository is the release / facade repo — it distributes the built application and documentation; the full source is not yet public and will be opened under Apache-2.0 when ready.
- 当前构建未签名，签名 / 公证在计划中。Builds are currently unsigned; signing / notarization is planned.

## 反馈 Feedback

遇到问题或有建议，欢迎在 Issues 页面反馈。Found a bug or have a suggestion? Please open an issue on the [Issues](https://github.com/thisThisYoung/ChemThisTry/issues) page.

## 许可证 License

采用 Apache License 2.0 许可。Released under the [Apache License 2.0](LICENSE).
