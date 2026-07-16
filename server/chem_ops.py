"""Chemistry / vector-export operations for the ChemThisTry web backend.

This module is the web counterpart of ``electron/chem_sidecar.py``. It contains
the same RDKit / cairosvg / scipy / ASE code paths (used by the desktop app's
Python sidecar) but exposes them as plain functions to be called from the
FastAPI layer (``main.py``). Keeping the heavy logic here (instead of importing
the sidecar's stdin/stdout loop) keeps the web backend self-contained and
deployable (e.g. via the included Dockerfile).

Capabilities:
  • RDKit 3D embedding + MMFF/UFF minimization (molecule:optimize3d)
  • RDKit 2D depiction to SVG            (chem:molToSvg)
  • ASE structure-format export          (molecule:exportStruct)
  • scipy nonlinear curve fitting        (chem:fit)
  • cairosvg SVG→PDF/EPS/PNG/TIFF        (chem:convertVector)
"""
from __future__ import annotations

import base64
import json
import os
import tempfile

import numpy as np  # noqa: E402 — kept at top so MODELS lambdas resolve np.*


# ---------------------------------------------------------------------------
# RDKit 3D embedding + force-field minimization
# ---------------------------------------------------------------------------
def optimize(molfile: str):
    """3D-embed a MOL and minimize with MMFF (UFF fallback). Returns (sdf, xyz)."""
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "rdkit not found in the Python environment. Run `pip install rdkit`, "
            "or use the provided Docker image which bundles rdkit-pypi."
        ) from exc

    mol = Chem.MolFromMolBlock(molfile, removeHs=False)
    if mol is None:
        raise ValueError("RDKit could not parse this MOL structure")
    if mol.GetNumAtoms() == 0:
        raise ValueError("Structure contains no atoms")

    mol = Chem.AddHs(mol)  # explicit hydrogens required for a meaningful embed

    params = AllChem.ETKDGv3()
    params.randomSeed = 0xF00D
    if AllChem.EmbedMolecule(mol, params) != 0:
        params.useRandomCoords = True
        if AllChem.EmbedMolecule(mol, params) != 0:
            raise RuntimeError("3D embedding failed (EmbedMolecule)")

    if AllChem.MMFFHasAllMoleculeParams(mol):
        AllChem.MMFFOptimizeMolecule(mol, maxIters=2000)
    else:
        AllChem.UFFOptimizeMolecule(mol, maxIters=2000)

    sdf = Chem.MolToMolBlock(mol)  # 3D coords, with explicit Hs
    xyz = Chem.MolToXYZBlock(mol)
    return sdf, xyz


# ---------------------------------------------------------------------------
# Nonlinear least-squares models (mirrors electron/chem_sidecar.py)
# ---------------------------------------------------------------------------
MODELS = {
    "linear": (lambda x, a, b: a * x + b, ["a", "b"], "y = a·x + b"),
    "poly2": (lambda x, a, b, c: a * x * x + b * x + c, ["a", "b", "c"], "y = a·x² + b·x + c"),
    "poly3": (
        lambda x, a, b, c, d: a * x**3 + b * x**2 + c * x + d,
        ["a", "b", "c", "d"],
        "y = a·x³ + b·x² + c·x + d",
    ),
    "exp": (lambda x, A, k: A * np.exp(k * x), ["A", "k"], "y = A·e^(k·x)"),
    "exp2": (
        lambda x, A1, k1, A2, k2: A1 * np.exp(k1 * x) + A2 * np.exp(k2 * x),
        ["A1", "k1", "A2", "k2"],
        "y = A1·e^(k1·x) + A2·e^(k2·x)",
    ),
    "gaussian": (
        lambda x, A, x0, sigma: A * np.exp(-((x - x0) ** 2) / (2 * sigma**2)),
        ["A", "x0", "sigma"],
        "y = A·e^(−(x−x0)²/(2σ²))",
    ),
    "lorentz": (
        lambda x, A, x0, gamma: A / (1 + ((x - x0) / gamma) ** 2),
        ["A", "x0", "gamma"],
        "y = A / (1 + ((x−x0)/γ)²)",
    ),
    "power": (lambda x, A, k: A * np.power(np.abs(x), k), ["A", "k"], "y = A·x^k"),
    "log": (lambda x, a, b: a + b * np.log(x), ["a", "b"], "y = a + b·ln(x)"),
    "sigmoid": (
        lambda x, L, x0, k: L / (1 + np.exp(-k * (x - x0))),
        ["L", "x0", "k"],
        "y = L / (1 + e^(−k·(x−x0)))",
    ),
    "voigt": (
        lambda x, A, x0, sigma, gamma: _voigt(x, A, x0, sigma, gamma),
        ["A", "x0", "sigma", "gamma"],
        "y = A·Voigt(x−x₀; σ, γ)",
    ),
    "damped": (
        lambda x, A, w, phi, k: A * np.exp(-k * x) * np.cos(w * x + phi),
        ["A", "w", "phi", "k"],
        "y = A·e^(−k·x)·cos(ω·x + φ)",
    ),
    "rational": (
        lambda x, a, b, c, d: (a * x + b) / (c * x + d),
        ["a", "b", "c", "d"],
        "y = (a·x + b)/(c·x + d)",
    ),
    "gauss2": (
        lambda x, A1, x1, s1, A2, x2, s2: (
            A1 * np.exp(-((x - x1) ** 2) / (2 * s1**2))
            + A2 * np.exp(-((x - x2) ** 2) / (2 * s2**2))
        ),
        ["A1", "x1", "s1", "A2", "x2", "s2"],
        "y = A₁·e^(−(x−x₁)²/(2σ₁²)) + A₂·e^(−(x−x₂)²/(2σ₂²))",
    ),
    "hill": (
        lambda x, Vmax, Kh, n: Vmax * (x**n) / (Kh**n + x**n),
        ["Vmax", "Kh", "n"],
        "y = V_max·x^n / (K_h^n + x^n)",
    ),
}


def _voigt(x, A, x0, sigma, gamma):
    from scipy.special import voigt_profile

    return A * voigt_profile(x - x0, sigma, gamma)


def _default_p0(x, y, names):
    if len(x) == 0:
        return [1.0 for _ in names]
    xmin, xmax = float(np.min(x)), float(np.max(x))
    xmid = 0.5 * (xmin + xmax)
    xspan = (xmax - xmin) or 1.0
    ymin, ymax = float(np.min(y)), float(np.max(y))
    yspan = (ymax - ymin) or 1.0
    amp = yspan
    guess = {
        "A": amp, "A1": amp / 2.0, "A2": amp / 2.0,
        "a": yspan / xspan, "b": ymin, "c": 1.0, "d": 1.0,
        "k": 1.0, "k1": 1.0, "k2": -1.0,
        "x0": xmid, "x1": xmin + xspan / 3.0, "x2": xmin + 2.0 * xspan / 3.0,
        "sigma": xspan / 4.0 or 1.0, "s1": xspan / 6.0 or 1.0, "s2": xspan / 6.0 or 1.0,
        "gamma": xspan / 4.0 or 1.0,
        "w": 2.0 * np.pi / xspan,
        "phi": 0.0,
        "L": ymax, "Vmax": ymax, "Kh": xmid, "n": 1.0,
    }
    return [float(guess.get(nm, 1.0)) for nm in names]


def fit(req: dict) -> dict:
    """Nonlinear least-squares fit via scipy.optimize.curve_fit.

    Returns a dict matching the renderer's ``FitResult`` shape (the same object
    the desktop sidecar returns after JSON-decoding its ``data`` field).
    """
    try:
        from scipy.optimize import curve_fit
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "scipy not found in the Python environment. Run `pip install scipy` "
            "or use the provided Docker image."
        ) from exc

    xs_raw = req.get("x", [])
    ys_raw = req.get("y", [])
    if len(xs_raw) < 2 or len(ys_raw) < 2:
        raise ValueError("Fitting needs at least 2 data points")

    x = np.array([float(v) for v in xs_raw], dtype=float)
    y = np.array([float(v) for v in ys_raw], dtype=float)
    if x.shape != y.shape:
        raise ValueError("X and Y data have mismatched lengths")

    model_name = (req.get("model") or "linear").lower()
    custom = req.get("custom")
    fix_req = req.get("fix") or {}
    bounds_req = req.get("bounds") or {}

    if model_name == "custom":
        if not custom or not custom.strip():
            raise ValueError("A custom model requires an expression (custom)")
        p0_in = req.get("p0") or []
        nparams = len(p0_in)
        if nparams == 0:
            raise ValueError("A custom model needs an initial p0 to set the parameter count")
        names = [f"p{i}" for i in range(nparams)]
        try:
            _math = {
                "np": np,
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
                "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
                "exp": np.exp, "log": np.log, "log10": np.log10, "log2": np.log2,
                "sqrt": np.sqrt, "abs": np.abs, "power": np.power,
                "floor": np.floor, "ceil": np.ceil, "sign": np.sign,
                "pi": np.pi, "e": np.e,
            }
            f = eval(  # noqa: S307 - trusted, user-authored math expression only
                "lambda x, " + ", ".join(names) + ": " + custom,
                {"__builtins__": {}, **_math},
            )
        except Exception as exc:
            raise ValueError(f"Failed to parse custom expression: {exc}")
        eq = custom
    else:
        if model_name not in MODELS:
            raise ValueError(f"Unknown fitting model: {model_name}")
        f, names, eq = MODELS[model_name]

    fixed = {}
    for nm, val in (fix_req or {}).items():
        if nm in names and val is not None and str(val).strip() != "":
            try:
                fixed[nm] = float(val)
            except (TypeError, ValueError):
                pass

    free_idx = [i for i, nm in enumerate(names) if nm not in fixed]

    def wrapped(xx, *free_p):
        args = []
        fi = 0
        for nm in names:
            if nm in fixed:
                args.append(fixed[nm])
            else:
                args.append(free_p[fi])
                fi += 1
        return f(xx, *args)

    full = []
    if free_idx:
        p0_in = req.get("p0") or []
        p0_all = [float(v) for v in p0_in] if p0_in else _default_p0(x, y, names)
        p0_free = [p0_all[i] for i in free_idx]

        lower, upper = [], []
        for i in free_idx:
            b = bounds_req.get(names[i])
            if isinstance(b, (list, tuple)) and len(b) == 2 and b[0] is not None and b[1] is not None:
                lower.append(float(b[0]))
                upper.append(float(b[1]))
            else:
                lower.append(-np.inf)
                upper.append(np.inf)

        for j in range(len(p0_free)):
            lo, hi = lower[j], upper[j]
            if np.isfinite(lo) or np.isfinite(hi):
                if not (lo <= p0_free[j] <= hi):
                    if np.isfinite(lo) and np.isfinite(hi):
                        p0_free[j] = 0.5 * (lo + hi)
                    elif np.isfinite(lo):
                        p0_free[j] = lo + max(abs(lo), 1.0) * 1e-3
                    else:
                        p0_free[j] = hi - max(abs(hi), 1.0) * 1e-3

        popt, pcov = curve_fit(
            wrapped, x, y, p0=p0_free,
            bounds=(np.array(lower), np.array(upper)), maxfev=60000,
        )
        fi = 0
        for nm in names:
            if nm in fixed:
                full.append(fixed[nm])
            else:
                full.append(float(popt[fi]))
                fi += 1
    else:
        pcov = np.zeros((0, 0))
        for nm in names:
            full.append(fixed[nm])

    yfit = f(x, *full)
    ss_res = float(np.sum((y - yfit) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    xd = np.linspace(float(np.min(x)), float(np.max(x)), 200)
    yd = f(xd, *full)

    params = {nm: float(v) for nm, v in zip(names, full)}
    errors = {}
    fi = 0
    for nm in names:
        if nm in fixed:
            errors[nm] = 0.0
        else:
            errors[nm] = float(np.sqrt(pcov[fi, fi])) if pcov.shape[0] > fi else 0.0
            fi += 1

    return {
        "model": model_name,
        "name": req.get("name") or model_name,
        "equation": eq,
        "params": params,
        "errors": errors,
        "fixedParams": list(fixed.keys()),
        "r2": float(r2),
        "n": int(len(x)),
        "x": [float(v) for v in xd],
        "y": [float(v) for v in yd],
    }


# ---------------------------------------------------------------------------
# cairosvg vector export
# ---------------------------------------------------------------------------
def convert(svg: str, fmt: str, dpi: int = 300) -> str:
    """Convert an SVG string to pdf/eps/png/tiff bytes; return base64."""
    try:
        import cairosvg
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "cairosvg not found in the Python environment. Run `pip install cairosvg` "
            "(EPS/vector PDF export needs it), or use the provided Docker image."
        ) from exc
    try:
        from PIL import Image
        import io
    except ImportError:  # pragma: no cover
        Image = None  # type: ignore[assignment]

    fmt = (fmt or "pdf").lower()
    data = svg.encode("utf-8")
    if fmt == "pdf":
        out = cairosvg.svg2pdf(bytestring=data, dpi=dpi)
    elif fmt in ("eps", "ps"):
        out = cairosvg.svg2ps(bytestring=data, dpi=dpi)
    elif fmt == "png":
        out = cairosvg.svg2png(bytestring=data, dpi=dpi)
    elif fmt == "tiff":
        if Image is None:
            raise RuntimeError("TIFF export needs Pillow; run `pip install pillow`.")
        png = cairosvg.svg2png(bytestring=data, dpi=dpi)
        im = Image.open(io.BytesIO(png))
        buf = io.BytesIO()
        im.save(buf, "TIFF", compression="tiff_lzw")
        out = buf.getvalue()
    else:
        raise ValueError(f"Unsupported export format: {fmt}")
    return base64.b64encode(out).decode("ascii")


# ---------------------------------------------------------------------------
# RDKit 2D depiction
# ---------------------------------------------------------------------------
def mol_to_svg(molfile: str, size: int = 400) -> str:
    """Depict a 2D MOL structure as SVG using native RDKit's vector drawer."""
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "rdkit not found in the Python environment. Run `pip install rdkit`, "
            "or use the provided Docker image which bundles rdkit-pypi."
        ) from exc
    mol = Chem.MolFromMolBlock(molfile)
    if mol is None:
        raise ValueError("RDKit could not parse this MOL structure")
    if mol.GetNumAtoms() == 0:
        raise ValueError("Structure contains no atoms")
    try:
        d = Draw.MolDraw2DSVG(size, size)
        d.DrawMolecule(mol)
        d.FinishDrawing()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"RDKit structure depiction failed: {exc}")
    return d.GetDrawingText()


# ---------------------------------------------------------------------------
# ASE structure export
# ---------------------------------------------------------------------------
def export_struct(payload: dict) -> str:
    """Write an atomic structure to a text format using ASE.

    ``payload`` = {format, atoms:[[sym,x,y,z],...], cell:[a,b,c,α,β,γ]|null,
    pbc:[bool,bool,bool]}. Returns the formatted structure text.
    """
    try:
        from ase import Atoms
        from ase.io import write as ase_write
        from ase.geometry import cellpar_to_cell
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "ase (Atomic Simulation Environment) not found. Run `pip install ase`, "
            "or use the provided Docker image."
        ) from exc

    atoms_in = payload.get("atoms") or []
    if not atoms_in:
        raise ValueError("No atoms available to export")
    symbols = [a[0] for a in atoms_in]
    positions = [[float(a[1]), float(a[2]), float(a[3])] for a in atoms_in]

    cell = payload.get("cell")
    pbc = payload.get("pbc") or [False, False, False]
    if cell and any(cell):
        cell_matrix = cellpar_to_cell([float(x) for x in cell])
    else:
        cell_matrix = None
        pbc = [False, False, False]

    fmt = (payload.get("format") or "pdb").lower()
    ase_atoms = Atoms(symbols=symbols, positions=positions, cell=cell_matrix, pbc=pbc)

    # ASE 3.x renamed the PDB writer to "proteindatabank".
    ASE_FORMAT_MAP = {
        "pdb": "proteindatabank",
        "cif": "cif",
        "xyz": "xyz",
        "extxyz": "extxyz",
        "vasp": "vasp",
        "gen": "gen",
        "cfg": "cfg",
    }
    ase_fmt = ASE_FORMAT_MAP.get(fmt, fmt)

    # ASE 3.x CIF writer calls fd.detach(), unsupported by a text StringIO, so
    # write to a real temp file and read it back (works for every ASE writer).
    fd, tmppath = tempfile.mkstemp(prefix="chemthis_export_", suffix=".tmp")
    os.close(fd)
    try:
        ase_write(tmppath, ase_atoms, format=ase_fmt)
        with open(tmppath, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"ASE failed to write format {fmt!r}: {exc}")
    finally:
        try:
            os.unlink(tmppath)
        except OSError:
            pass
    return text


# ---------------------------------------------------------------------------
# Capability probe
# ---------------------------------------------------------------------------
def ping() -> dict:
    import sys

    caps = {
        "python": sys.version.split()[0],
        "rdkit": False,
        "cairosvg": False,
        "scipy": False,
        "ase": False,
    }
    for mod, key in (("rdkit", "rdkit"), ("cairosvg", "cairosvg"),
                     ("scipy", "scipy"), ("ase", "ase")):
        try:
            __import__(mod)
            caps[key] = True
        except Exception:
            pass
    return caps
