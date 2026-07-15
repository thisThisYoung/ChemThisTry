# ChemThisTry

> A cross-platform scientific graphics workstation for data plotting, chemical-structure drawing, 3D molecular / crystal visualization, and figure compositing — all in one desktop app, with an optional Python sidecar for curve fitting and 3D conformer optimization.
>
> 跨平台一体化科研绘图工作站：数据作图、化学结构绘制、3D 分子/晶体可视化、图版排版，集于一个桌面应用；可选 Python 侧车提供曲线拟合与 3D 构象优化。

[![Latest release](https://img.shields.io/github/v/release/thisThisYoung/ChemThisTry?label=release)](https://github.com/thisThisYoung/ChemThisTry/releases/latest)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](#download--下载)

*English follows Chinese in each section. 每节中英对照。*

<!-- Screenshot placeholder — replace with a real image:
![ChemThisTry main window](assets/screenshot-main.png)
-->

## Features / 功能速览

ChemThisTry bundles five linked modules on an infinite canvas workspace. Edits flow live between them — change a structure and the linked figure updates automatically.

ChemThisTry 由五个相互联动的模块组成，共享一个无限画布工作区。各模块之间实时联动——修改结构，画布上关联的图形会自动更新。

### 📊 DataViewer — Spreadsheet & data editor / 电子表格与数据编辑
- **EN:** A spreadsheet-style data editor with custom delimiters, formula columns, descriptive statistics, and a plotting console. Serves as the data source for GraphViewer.
- **中文：** 电子表格式数据编辑器，支持自定义分隔符、公式列、描述性统计与绘图控制台，是 GraphViewer 的数据来源。
- **Import / 导入:** `.csv` · `.tsv` · `.tab` · `.txt` · `.dat` · `.prn` (space / comma / tab / custom delimiters, plus clipboard paste)
- **Export / 导出:** `.csv`

### 📈 GraphViewer — Data plotting / 数据作图
- **EN:** Publication-quality plots (scatter, line, bar, and more) via ECharts, driven by DataViewer datasets, with transparent backgrounds and print-resolution output. Curve fitting available through the Python sidecar.
- **中文：** 基于 ECharts 的出版级数据图（散点/折线/柱状等），数据来自 DataViewer 数据集，支持透明背景与出版分辨率导出；曲线拟合由 Python 侧车提供。
- **Export / 导出:** `.png` · `.svg` · `.pdf` · `.eps`

### ⚗️ Sketcher — 2D chemical structures / 化学结构
- **EN:** Draw and edit molecules and reactions with a Ketcher-based editor; type SMILES directly. Send structures to Moleculer (3D) or the Canvas with one click.
- **中文：** 基于 Ketcher 的分子/反应式绘制编辑器，可直接输入 SMILES；一键将结构发送到 Moleculer（3D）或画布。
- **Import / 导入:** `.mol` · `.rxn` · `.sdf` · `.cml` · `.ket` · `.smi` · `.inchi` · SMILES text
- **Export / 导出:** `.png` · `.svg` · `.pdf` · `.eps` → Moleculer / → Canvas

### 🧪 Moleculer — 3D molecules & crystals / 3D 分子与晶体
- **EN:** VESTA-style unit cells and coordination polyhedra powered by 3Dmol.js. Expand supercells, switch handedness, and optimize conformers via the Python sidecar (RDKit).
- **中文：** 基于 3Dmol.js 的 VESTA 风格晶胞与配位多面体，支持超胞扩展、左右手坐标系切换，并可通过 Python 侧车（RDKit）优化构象。
- **Import / 导入:** `.cif` · `.pdb` · `.xyz` · `.mol` · `.mol2` · `.sdf` · `.pqr` · `.vesta` · `.mlcl` · VASP (`POSCAR` / `CONTCAR`)
- **Export structure / 结构导出 (ASE):** `.pdb` · `.cif` · `.xyz` · extended XYZ · VASP · GEN · CFG
- **Export image / 图片导出:** `.png` · `.pdf` · save `.mlcl`

### 🎨 Canvas — Vector figure compositing / 矢量画布排版
- **EN:** Compose schematics, flowcharts, annotations, and multi-panel figures on an infinite canvas. Place plots, structures, and 3D snapshots together, kept live-linked to their source modules.
- **中文：** 在无限画布上排版示意图、流程图、标注与多面板图版；将数据图、结构、3D 快照组合在一起，并与来源模块保持实时联动。
- **Import / 导入:** images (`image/*`)
- **Export / 导出:** `.svg` · `.pdf` · `.eps` · `.png` · `.tiff`

### 🌐 More / 其他
- **Project file / 工程文件:** `.ctt` (SQLite-based project bundle / 基于 SQLite 的工程包)
- **Multilingual UI / 多语言界面:** 简体中文 · 繁體中文 · English · 日本語 · Français · Español · Dansk

## Download / 下载

Pre-built installers for macOS, Windows, and Linux are on the **Releases** page.
macOS / Windows / Linux 的预编译安装包发布在 **Releases** 页面。

👉 **Latest / 最新版:** https://github.com/thisThisYoung/ChemThisTry/releases/latest
👉 **v0.1.0:** https://github.com/thisThisYoung/ChemThisTry/releases/tag/v0.1.0

| Platform / 平台 | File / 文件 |
|-----------------|-------------|
| macOS (Apple Silicon) | `ChemThisTry-0.1.0-arm64.dmg`  ·  `ChemThisTry-0.1.0-arm64-mac.zip` |
| macOS (Intel) | `ChemThisTry-0.1.0.dmg`  ·  `ChemThisTry-0.1.0-mac.zip` |
| Windows | `ChemThisTry-0.1.0.exe` |
| Linux (portable / 便携版) | `ChemThisTry-0.1.0.AppImage` |
| Linux (Debian/Ubuntu) | `ChemThisTry-0.1.0.deb` |

Download the file for your platform and install as usual — no account or build step required. On Apple Silicon Macs use the `-arm64` build; Intel Macs use the file with no arch suffix.

下载对应平台的文件按常规安装即可，无需账号或构建步骤。Apple Silicon（M 系列）Mac 用 `-arm64` 版本；Intel Mac 用无芯片后缀的版本。

## First launch notes / 首次运行

The binaries are currently distributed **without code-signing / notarization**, so your OS may show a security warning on first open. This is expected and does not mean the file is broken.

当前安装包**未签名、未公证**，首次打开时系统可能弹出安全提示，属正常现象，不代表文件损坏。

### macOS (Gatekeeper)
1. If a dialog says *"ChemThisTry cannot be opened because the developer cannot be verified"*, click **Cancel**. / 若提示"无法打开，因为无法验证开发者"，先点**取消**。
2. Right-click (or Control-click) the app and choose **Open**, then click **Open** in the dialog. / 右键（或 Control+点击）应用 → 选**打开** → 弹窗中再点**打开**。
3. If it still refuses, run in Terminal / 若仍被拦截，在终端执行：
   ```bash
   sudo xattr -rd com.apple.quarantine /Applications/ChemThisTry.app
   ```

### Windows (SmartScreen)
1. When SmartScreen shows *"Windows protected your PC"*, click **More info**. / 当出现"Windows 已保护你的电脑"，点**更多信息**。
2. Click **Run anyway**. / 点**仍要运行**。

### Linux
- **AppImage:** `chmod +x ChemThisTry-0.1.0.AppImage`, then run it. / 赋予执行权限后运行。
- **.deb:** `sudo dpkg -i ChemThisTry-0.1.0.deb` (resolve deps with `sudo apt-get install -f` if needed). / 如缺依赖用 `sudo apt-get install -f` 补齐。

## Python sidecar / Python 侧车

Some features — 3D conformer optimization (Sketcher → Moleculer), ASE-based structure export (PDB/CIF/XYZ/VASP), and EPS / vector-PDF export — use a Python sidecar with **RDKit** and **ASE**. The status bar shows `Python: connected` when available. Everything else works without it.

部分功能——3D 构象优化（Sketcher → Moleculer）、基于 ASE 的结构导出（PDB/CIF/XYZ/VASP）、EPS/矢量 PDF 导出——需要带 **RDKit** 与 **ASE** 的 Python 侧车。可用时状态栏显示 `Python: connected`。其余功能无需侧车即可使用。

- **macOS / Linux:** the app auto-detects Python 3.9+ on your `PATH`. Install deps if missing / 应用会自动检测 `PATH` 上的 Python 3.9+，缺依赖时安装：
  ```bash
  pip install rdkit-pypi ase scipy cairosvg
  ```
  On Debian/Ubuntu you can instead use `sudo apt install python3-rdkit python3-scipy` (plus `pip install cairosvg`).
- **Windows:** the installer does **not** bundle Python. Install Python 3.9+ from python.org (tick *Add Python to PATH*), then / 安装包**不含** Python，请从 python.org 安装 Python 3.9+（勾选 *Add Python to PATH*）后执行：
  ```powershell
  pip install rdkit-pypi ase scipy cairosvg
  ```
  > On Windows the RDKit package is **`rdkit-pypi`**, not `rdkit`. If the sidecar fails with exit code **9009**, set `CHEMTHIS_PYTHON` to the full path of your `python.exe` and relaunch. / Windows 上 RDKit 包名是 `rdkit-pypi`；若侧车报 **9009** 错误，把 `CHEMTHIS_PYTHON` 设为 `python.exe` 的完整路径后重启。

## Status / 项目状态

- This repository is the **release / facade repo** — it distributes the built application and documentation. The full source is not yet publicly available and will be opened under Apache-2.0 when ready. / 本仓库为**发布/门面仓库**，分发编译产物与文档；完整源码暂未公开，就绪后将以 Apache-2.0 开源。
- Builds are **unsigned** for now; signing / notarization is planned. / 当前构建**未签名**，签名/公证在计划中。

## Feedback / 反馈

Found a bug or have a suggestion? Please open an issue on the **[Issues](https://github.com/thisThisYoung/ChemThisTry/issues)** page. / 遇到问题或有建议，欢迎在 **[Issues](https://github.com/thisThisYoung/ChemThisTry/issues)** 页面反馈。

## License / 许可证

Released under the [Apache License 2.0](LICENSE). / 采用 [Apache License 2.0](LICENSE) 许可。
