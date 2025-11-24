#!/usr/bin/env python3
"""
Ridder Unified Potential – Smoke Test

Purpose:
- Sanity check that the unified potential + CDM coupling compiles and runs.
- Tie the unified configs ("hero" and "safe") back to the best v2 CDM
  optimization points (beta, sigma_z).

What it does:
1. Look for:
   - unified_cdm_hero.ini
   - unified_cdm_safe.ini
   - phase2/class/class (CLASS binary)
2. Optionally load v2 reference metrics from:
   - cdm_coupling_optimization_results.json
3. For each case:
   - Print the v2 reference (ΔH0, max CMB Δ) if available.
   - Run CLASS with the unified .ini.
   - Report success/failure and basic runtime info.

Run from repo root:
    cd ~/Ridder-Field
    python3 ridder_unified_smoketest.py
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------
# Configuration for the smoketest
# ---------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
CLASS_BIN = REPO_ROOT / "phase2" / "class" / "class"
V2_RESULTS_JSON = REPO_ROOT / "cdm_coupling_optimization_results.json"

# The two key points we care about: "hero" and "safe"
CASES = [
    {
        "label": "hero",
        "ini": REPO_ROOT / "unified_cdm_hero.ini",
        "beta": 0.20,
        "sigma_z": 0.5,
    },
    {
        "label": "safe",
        "ini": REPO_ROOT / "unified_cdm_safe.ini",
        "beta": 0.15,
        "sigma_z": 0.5,
    },
]

# How close beta/sigma_z must be to match a v2 row
BETA_TOL = 1e-6
SIGMA_TOL = 1e-6

# Timeout per CLASS run (seconds)
CLASS_TIMEOUT = 600


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_v2_results(path: Path) -> Optional[List[Dict[str, Any]]]:
    """Load v2 CDM optimization results if present."""
    if not path.exists():
        print(f"[WARN] v2 results JSON not found: {path}")
        return None

    try:
        with path.open("r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"[WARN] Unexpected JSON structure in {path}, expected list of dicts.")
            return None
        return data
    except Exception as e:
        print(f"[WARN] Failed to load {path}: {e}")
        return None


def find_v2_row(
    results: List[Dict[str, Any]],
    beta: float,
    sigma_z: float,
) -> Optional[Dict[str, Any]]:
    """Find the v2 optimization row matching (beta, sigma_z) within tolerances."""
    for row in results:
        try:
            b = float(row.get("beta", row.get("ridder_cdm_beta", 0)))
            s = float(row.get("sigma_z", row.get("ridder_cdm_sigma_z", 0)))
        except Exception:
            continue

        if abs(b - beta) < BETA_TOL and abs(s - sigma_z) < SIGMA_TOL:
            return row

    return None


def run_class(ini_path: Path) -> Tuple[bool, float, str]:
    """
    Run CLASS with the given ini file.

    Returns:
        (success, runtime_seconds, short_message)
    """
    if not ini_path.exists():
        return False, 0.0, f".ini not found: {ini_path}"

    cmd = [str(CLASS_BIN), str(ini_path.name)]
    start = time.time()

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ini_path.parent),
            capture_output=True,
            text=True,
            timeout=CLASS_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, time.time() - start, "timeout expired"

    runtime = time.time() - start

    if proc.returncode != 0:
        # Include a short tail of stderr for debugging
        stderr_tail = "\n".join(proc.stderr.splitlines()[-5:])
        msg = f"non-zero exit code {proc.returncode}\n--- stderr tail ---\n{stderr_tail}"
        return False, runtime, msg

    return True, runtime, "ok"


def format_v2_row(row: Dict[str, Any]) -> str:
    """Pretty-print a v2 reference row (ΔH0, CMB metrics)."""
    def get(key: str, default: Any = None) -> Any:
        return row.get(key, default)

    delta_h0 = get("delta_h0", get("ΔH0"))
    max_cmb = get("max_cmb_diff", get("max_cmb_delta"))
    rms_cmb = get("rms_cmb_diff", get("rms_cmb_delta"))

    parts = []
    if delta_h0 is not None:
        parts.append(f"ΔH₀ ≈ {delta_h0:.4f} km/s/Mpc")
    if max_cmb is not None:
        parts.append(f"Max CMB Δ ≈ {max_cmb:.1f}%")
    if rms_cmb is not None:
        parts.append(f"RMS CMB Δ ≈ {rms_cmb:.1f}%")

    return ", ".join(parts) if parts else "(no numeric fields found)"


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> int:
    print("=" * 82)
    print("RIDDER UNIFIED POTENTIAL – SMOKETEST")
    print("=" * 82)
    print(f"Repo root: {REPO_ROOT}")
    print(f"CLASS bin: {CLASS_BIN}")
    print()

    # Basic checks
    if not CLASS_BIN.exists():
        print(f"[ERROR] CLASS binary not found at {CLASS_BIN}")
        print("        Make sure you ran `make` in phase2/class before this test.")
        return 1

    missing_inis = [c for c in CASES if not c["ini"].exists()]
    if missing_inis:
        print("[ERROR] Missing .ini files for unified configs:")
        for c in missing_inis:
            print(f"  - {c['label']}: {c['ini']}")
        print("Create unified_cdm_hero.ini and unified_cdm_safe.ini first.")
        return 1

    # Load v2 results if available
    v2_results = load_v2_results(V2_RESULTS_JSON)
    if v2_results is None:
        print("[INFO] No v2 optimization results loaded; will skip reference metrics.")
    else:
        print(f"[INFO] Loaded v2 optimization results from {V2_RESULTS_JSON}")
    print()

    # Run each case
    rows = []
    for case in CASES:
        label = case["label"]
        ini = case["ini"]
        beta = case["beta"]
        sigma_z = case["sigma_z"]

        print("-" * 82)
        print(f"[{label.upper()}] Unified config: {ini.name}")
        print(f"  Target v2 CDM params: beta = {beta}, sigma_z = {sigma_z}")

        v2_row = None
        if v2_results is not None:
            v2_row = find_v2_row(v2_results, beta, sigma_z)
            if v2_row is not None:
                print("  v2 reference: " + format_v2_row(v2_row))
            else:
                print("  v2 reference: (no exact match found for beta, sigma_z)")

        print("  → Running CLASS ...")
        ok, runtime, msg = run_class(ini)

        if ok:
            print(f"  ✓ CLASS completed successfully in {runtime:.1f} s")
        else:
            print(f"  ✗ CLASS failed after {runtime:.1f} s")
            print(f"    Reason:\n{msg}")

        rows.append(
            {
                "label": label,
                "ini": ini.name,
                "beta": beta,
                "sigma_z": sigma_z,
                "v2_row": v2_row,
                "success": ok,
                "runtime": runtime,
                "message": msg,
            }
        )

    print("-" * 82)
    print("SUMMARY")
    print("-" * 82)
    for r in rows:
        label = r["label"]
        status = "OK" if r["success"] else "FAIL"
        line = f"{label:5s} | {status:4s} | beta={r['beta']:.2f}, sigma_z={r['sigma_z']:.2f}"
        if r["v2_row"] is not None:
            dv = r["v2_row"].get("delta_h0", r["v2_row"].get("ΔH0"))
            max_cmb = r["v2_row"].get("max_cmb_diff", r["v2_row"].get("max_cmb_delta"))
            if dv is not None and max_cmb is not None:
                line += f" | v2: ΔH₀~{dv:.2f}, Max CMB~{max_cmb:.1f}%"
        print(line)

    print()
    print("Smoketest complete.")
    print("If both HERO and SAFE are OK, unified potential + CDM coupling is at least")
    print("numerically sound. Next steps are to add metric extraction (ΔH₀, CMB) for")
    print("unified runs and compare to the v2 reference values printed above.")
    print("=" * 82)

    return 0


if __name__ == "__main__":
    sys.exit(main())

