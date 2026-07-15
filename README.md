# ChemThisTry

> ChemThisTry is a cross-platform scientific graphics workstation unifying data plotting, chemical structure drawing, 3D molecular visualization, and figure compositing — a lightweight alternative to Origin + ChemDraw + VESTA + Illustrator. Built with Electron + React + TypeScript; a Python sidecar handles curve fitting and conformer optimization.

<!-- Screenshot placeholder — replace with a real image:
![ChemThisTry main window](assets/screenshot-main.png)
-->

## What it does

ChemThisTry is a single desktop app that covers the most common scientific-figure workflows without juggling four separate commercial tools:

- **Data plotting** — scatter, line, bar, and more, with fine-grained styling and a spreadsheet-style data sheet.
- **Chemical structures** — draw and edit molecules with a Ketcher-based sketcher; export to SVG/MOL.
- **3D molecular visualization** — view structures and crystals (CIF/MOL/SDF), build polyhedra, and expand unit cells with a 3Dmol-powered viewer.
- **Figure compositing** — arrange plots, structures, and 3D snapshots on an infinite canvas, with linked live updates between viewers.
- **Publication-grade export** — SVG, EPS, PDF, and PNG at print resolution, driven by an optional Python sidecar (rdkit / Pyodide) for curve fitting and conformer optimization.

## Download

Pre-built installers for macOS, Windows, and Linux are published on the **Releases** page:

👉 **https://github.com/chemthistry/ChemThisTry/releases**

| Platform | File |
|----------|------|
| macOS (Apple Silicon) | `ChemThisTry-*.arm64.dmg` |
| macOS (Intel) | `ChemThisTry-*.x64.dmg` |
| Windows | `ChemThisTry Setup *.exe` |
| Linux | `ChemThisTry-*.AppImage` / `*.deb` |

Download the file for your platform and install as usual. No account or build step required.

## First launch notes

The binaries are currently distributed **without code-signing / notarization**, so your OS may show a security warning on first open. This is expected and does not mean the file is broken.

### macOS
1. If a dialog says *"ChemThisTry cannot be opened because the developer cannot be verified"*, click **Cancel**.
2. Open **System Settings → Privacy & Security**.
3. Scroll down to the *"ChemThisTry was blocked from opening"* message and click **Open Anyway**.
4. Confirm with your password / Touch ID.

Alternatively, right-click (or Control-click) the app and choose **Open**, then click **Open** in the dialog. You only need to do this once.

### Windows
1. When SmartScreen shows *"Windows protected your PC"* / *"Unknown publisher"*, click **More info**.
2. Click **Run anyway**.

### Linux
- **AppImage**: `chmod +x ChemThisTry-*.AppImage` then run it.
- **.deb**: install with `sudo dpkg -i ChemThisTry-*.deb` (resolve dependencies with `sudo apt-get install -f` if needed).

## Python sidecar (3D optimization & advanced export)

Some features — 3D conformer optimization (Sketcher → Moleculer), ASE-based structure export (PDB/CIF/XYZ/VASP), and EPS/vector-PDF export — use a Python sidecar with **RDKit** and **ASE**. The app status bar shows `Python: connected` when it is available.

- **macOS / Linux**: the app auto-detects a Python 3.9+ on your `PATH` (macOS also uses the project's managed venv). On Linux the runtime is **not** bundled, so install it yourself if missing — `pip install rdkit-pypi ase scipy cairosvg`, or on Debian/Ubuntu more simply `sudo apt install python3-rdkit python3-scipy` (plus `pip install cairosvg`). If needed, point the app at a specific interpreter via the `CHEMTHIS_PYTHON` environment variable.
- **Windows**: the installer does **not** bundle Python. Install Python 3.9+ from python.org (tick *Add Python to PATH*), then in a terminal run:
  ```powershell
  pip install rdkit-pypi ase scipy cairosvg
  ```
  > On Windows the RDKit package is **`rdkit-pypi`**, not `rdkit`. If the sidecar fails with exit code **9009** ("system cannot find the file"), set `CHEMTHIS_PYTHON` to the full path of your `python.exe` and relaunch.
- **Builders**: to ship a Windows installer that needs no user Python, run `node scripts/bundle-python-win.mjs` on a Windows build host (populates `resources/python`) before `npm run dist:win`. electron-builder then bundles it automatically.

## Status

- **Source code** is not yet publicly available. This repository currently hosts the built application and documentation. Source will be opened under the Apache-2.0 license when ready.
- Builds are **unsigned** for now; signing/notarization is planned. See the launch notes above.

## License

Released under the [Apache License 2.0](LICENSE).
