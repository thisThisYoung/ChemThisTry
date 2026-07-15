# ChemThisTry

> A cross-platform scientific graphics workstation that unifies data plotting, chemical-structure drawing, 3D molecular / crystal visualization, and figure compositing — a lightweight alternative to **Origin + ChemDraw + VESTA + Illustrator**. Built with Electron + React + TypeScript, with an optional Python sidecar for curve fitting and 3D conformer optimization.

[![Latest release](https://img.shields.io/github/v/release/thisThisYoung/ChemThisTry?label=release)](https://github.com/thisThisYoung/ChemThisTry/releases/latest)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](#download)

<!-- Screenshot placeholder — replace with a real image:
![ChemThisTry main window](assets/screenshot-main.png)
-->

## What it does

ChemThisTry is a single desktop app that covers the most common scientific-figure workflows without juggling four separate commercial tools:

- **Vector canvas (Canvas)** — build publication-grade schematics, flowcharts, annotations, and compositions on an infinite canvas.
- **Data plotting (GraphViewer)** — scatter / line / bar and more via ECharts, with a spreadsheet-style data sheet, transparent backgrounds, and print-resolution export.
- **Chemical structures (Sketcher)** — draw and edit molecules with a Ketcher-based editor; import/export `.mol` / `.rxn` and SVG.
- **3D molecules & crystals (Moleculer)** — VESTA-style unit cells and coordination polyhedra powered by 3Dmol; open `.cif` / `.mol` / `.sdf` / `.vesta`, expand cells, and switch handedness.
- **Structure ↔ figure linking** — edits to a structure sync live into the linked object on the canvas.
- **Publication-grade export** — SVG / PDF / EPS / vector-PDF / PNG at print resolution, with an optional Python sidecar (RDKit / ASE) for 3D optimization and structure export (PDB/CIF/XYZ/VASP).
- **Multilingual UI** — 简体中文 / 繁體中文 / English / 日本語 / Français / Español / Dansk.

## Download

Pre-built installers for macOS, Windows, and Linux are on the **Releases** page:

👉 **Latest:** https://github.com/thisThisYoung/ChemThisTry/releases/latest
👉 **v0.1.0:** https://github.com/thisThisYoung/ChemThisTry/releases/tag/v0.1.0

| Platform | File |
|----------|------|
| macOS (Apple Silicon) | `ChemThisTry-0.1.0-arm64.dmg`  ·  `ChemThisTry-0.1.0-arm64-mac.zip` |
| macOS (Intel) | `ChemThisTry-0.1.0.dmg`  ·  `ChemThisTry-0.1.0-mac.zip` |
| Windows | `ChemThisTry-0.1.0.exe` |
| Linux (portable) | `ChemThisTry-0.1.0.AppImage` |
| Linux (Debian/Ubuntu) | `ChemThisTry-0.1.0.deb` |

Download the file for your platform and install as usual — no account or build step required. On Apple Silicon Macs use the `-arm64` build; Intel Macs use the file with no arch suffix.

## First launch notes

The binaries are currently distributed **without code-signing / notarization**, so your OS may show a security warning on first open. This is expected and does not mean the file is broken.

### macOS (Gatekeeper)
1. If a dialog says *"ChemThisTry cannot be opened because the developer cannot be verified"*, click **Cancel**.
2. Right-click (or Control-click) the app and choose **Open**, then click **Open** in the dialog — you only need to do this once.
3. If it still refuses, run in Terminal:
   ```bash
   sudo xattr -rd com.apple.quarantine /Applications/ChemThisTry.app
   ```

### Windows (SmartScreen)
1. When SmartScreen shows *"Windows protected your PC"* / *"Unknown publisher"*, click **More info**.
2. Click **Run anyway**.

### Linux
- **AppImage**: `chmod +x ChemThisTry-0.1.0.AppImage`, then run it.
- **.deb**: `sudo dpkg -i ChemThisTry-0.1.0.deb` (resolve dependencies with `sudo apt-get install -f` if needed).

## Python sidecar (3D optimization & advanced export)

Some features — 3D conformer optimization (Sketcher → Moleculer), ASE-based structure export (PDB/CIF/XYZ/VASP), and EPS / vector-PDF export — use a Python sidecar with **RDKit** and **ASE**. The app status bar shows `Python: connected` when it is available. Everything else works without it.

- **macOS / Linux**: the app auto-detects a Python 3.9+ on your `PATH`. Install the deps if missing:
  ```bash
  pip install rdkit-pypi ase scipy cairosvg
  ```
  On Debian/Ubuntu you can instead use `sudo apt install python3-rdkit python3-scipy` (plus `pip install cairosvg`). Point the app at a specific interpreter via the `CHEMTHIS_PYTHON` environment variable if needed.
- **Windows**: the installer does **not** bundle Python. Install Python 3.9+ from python.org (tick *Add Python to PATH*), then:
  ```powershell
  pip install rdkit-pypi ase scipy cairosvg
  ```
  > On Windows the RDKit package is **`rdkit-pypi`**, not `rdkit`. If the sidecar fails with exit code **9009** ("system cannot find the file"), set `CHEMTHIS_PYTHON` to the full path of your `python.exe` and relaunch.

## Status

- This repository is the **release / facade repo** — it distributes the built application and documentation. The full source is not yet publicly available and will be opened under the Apache-2.0 license when ready.
- Builds are **unsigned** for now; signing / notarization is planned. See the first-launch notes above.

## Feedback

Found a bug or have a suggestion? Please open an issue on the **[Issues](https://github.com/thisThisYoung/ChemThisTry/issues)** page.

## License

Released under the [Apache License 2.0](LICENSE).
