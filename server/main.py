"""ChemThisTry web backend (FastAPI + RDKit / cairosvg / scipy / ASE).

This is the lightweight backend the web build of ChemThisTry talks to. The
renderer's web bridge (src/web-bridge.ts) proxies its chemistry/science IPC
channels here:

  GET  /api/health          → capability probe (rdkit/cairosvg/scipy/ase)
  POST /api/optimize3d      → RDKit 3D embed + MMFF/UFF minimization
  POST /api/molToSvg        → RDKit 2D depiction → SVG
  POST /api/exportStruct    → ASE structure-file export
  POST /api/fit             → scipy nonlinear curve fit
  POST /api/convertVector   → cairosvg SVG→PDF/EPS/PNG/TIFF

Run locally:
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8000

Or with Docker (see Dockerfile / docs/DEPLOY.md).

CORS: controlled by CORS_ORIGINS (comma-separated). Defaults to "*" for quick
local dev; set it to your frontend origin(s) in production.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import chem_ops

app = FastAPI(title="ChemThisTry Web Backend", version="0.1.1")

# ── CORS ─────────────────────────────────────────────────────────────────────
_cors_raw = os.environ.get("CORS_ORIGINS", "*")
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ────────────────────────────────────────────────────────────
class OptimizeRequest(BaseModel):
    molfile: str


class MolToSvgRequest(BaseModel):
    molfile: str
    size: int = 400


class ExportStructRequest(BaseModel):
    format: str
    atoms: list[list[Any]]
    cell: Optional[list[float]] = None
    pbc: Optional[list[bool]] = None


class FitRequest(BaseModel):
    x: list[float]
    y: list[float]
    model: str = "linear"
    p0: Optional[list[float]] = None
    custom: Optional[str] = None
    name: Optional[str] = None
    fix: Optional[dict[str, float]] = None
    bounds: Optional[dict[str, list[float]]] = None


class ConvertVectorRequest(BaseModel):
    svg: str
    format: str = "pdf"
    dpi: int = 300


# ── Helpers ─────────────────────────────────────────────────────────────────
def _err(e: Exception) -> dict:
    return {"ok": False, "error": f"{type(e).__name__}: {e}"}


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health() -> dict:
    caps = chem_ops.ping()
    return {"ok": True, **caps}


@app.post("/api/optimize3d")
async def api_optimize3d(req: OptimizeRequest) -> dict:
    if not req.molfile or not req.molfile.strip():
        return {"ok": False, "error": "empty molfile"}
    try:
        sdf, xyz = chem_ops.optimize(req.molfile)
        return {"ok": True, "sdf": sdf, "xyz": xyz}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/api/molToSvg")
async def api_mol_to_svg(req: MolToSvgRequest) -> dict:
    try:
        svg = chem_ops.mol_to_svg(req.molfile, req.size)
        return {"ok": True, "svg": svg}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/api/exportStruct")
async def api_export_struct(req: ExportStructRequest) -> dict:
    try:
        text = chem_ops.export_struct(
            {
                "format": req.format,
                "atoms": req.atoms,
                "cell": req.cell,
                "pbc": req.pbc,
            }
        )
        return {"ok": True, "text": text}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/api/fit")
async def api_fit(req: FitRequest) -> dict:
    try:
        result = chem_ops.fit(
            {
                "x": req.x,
                "y": req.y,
                "model": req.model,
                "p0": req.p0,
                "custom": req.custom,
                "name": req.name,
                "fix": req.fix,
                "bounds": req.bounds,
            }
        )
        return {"ok": True, **result}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/api/convertVector")
async def api_convert_vector(req: ConvertVectorRequest) -> dict:
    try:
        data = chem_ops.convert(req.svg, req.format, req.dpi)
        return {"ok": True, "base64": data}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.get("/")
async def root() -> dict:
    return {"service": "ChemThisTry Web Backend", "docs": "/docs", "health": "/api/health"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), reload=False)
