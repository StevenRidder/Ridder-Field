#!/usr/bin/env python3
"""
Concrete validation of unified Ridder potential against v2 CDM-coupled benchmarks.

This script:
  - Runs CLASS for two unified configs:
        - unified_cdm_hero.ini   (beta=0.20, sigma_z=0.5)
        - unified_cdm_safe.ini   (beta=0.15, sigma_z=0.5)
  - Forces background output with a temporary root name
  - Extracts r_s from the background file (last sound horizon value)
  - Computes H0_eff and ΔH0 using the same scaling logic as v2
  - Loads v2 reference metrics from cdm_coupling_optimization_results.json
  - Compares unified vs v2 and reports agreement

Assumptions:
  - Repo root: this script lives in /home/.../Ridder-Field
  - CLASS binary: phase2/class/class
  - v2 results JSON: cdm_coupling_optimization_results.json
  - unified .ini configs in repo root: unified_cdm_hero.ini, unified_cdm_safe.ini
  - CLASS writes background file as: <root>_background.dat
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

# ---------------------------------------------------------------------------
# Constants: baseline ΛCDM values used in v2
# ---------------------------------------------------------------------------

# Planck-like baseline H0 used in your v2 analysis (in km/s/Mpc)
H0_LCDM = 67.36

# Baseline sound horizon r_s^ΛCDM inferred from your v2 output:
# r_s(model) = 142.722749 Mpc with Δr_s/r_s = -2.962%
# => r_s_LCDM ≈ 147.079 Mpc
RS_LCDM = 147.07923596941404


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CaseSpec:
    key: str
    label: str
    ini_filename: str
    beta: float
    sigma_z: float


@dataclass
class V2Reference:
    beta: float
    sigma_z: float
    delta_h0: float
    max_cmb_diff: Optional[float]
    rms_cmb_diff: Optional[float]


@dataclass
class UnifiedMetrics:
    rs: float
    delta_rs_over_rs: float
    h0_eff: float
    delta_h0: float


@dataclass
class ComparisonResult:
    case: CaseSpec
    v2: Optional[V2Reference]
    unified: UnifiedMetrics


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def find_repo_root() -> str:
    """Return absolute path to repo root (directory containing this script)."""
    here = os.path.abspath(os.path.dirname(__file__))
    return here


def ensure_class_binary(repo_root: str) -> str:
    """Return path to CLASS binary and assert it exists."""
    class_bin = os.path.join(repo_root, "phase2", "class", "class")
    if not os.path.exists(class_bin):
        print(f"[ERROR] CLASS binary not found at: {class_bin}", file=sys.stderr)
        sys.exit(1)
    return class_bin


def load_v2_results(repo_root: str) -> Optional[list]:
    """Load v2 optimization results JSON if present."""
    path = os.path.join(repo_root, "cdm_coupling_optimization_results.json")
    if not os.path.exists(path):
        print(f"[WARN] v2 results JSON not found at: {path}")
        print("       Unified metrics will be computed but not compared.")
        return None

    with open(path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"[WARN] Unexpected JSON structure in {path}. Expected a list.")
        return None

    return data


def match_v2_reference(
    results: list,
    beta_target: float,
    sigma_target: float,
    tol: float = 1e-6
) -> Optional[V2Reference]:
    """Find the v2 entry with given (beta, sigma_z)."""
    for row in results:
        try:
            beta = float(row.get("beta"))
            sigma_z = float(row.get("sigma_z"))
        except (TypeError, ValueError):
            continue

        if abs(beta - beta_target) < tol and abs(sigma_z - sigma_target) < tol:
            delta_h0 = float(row.get("delta_h0"))
            max_cmb_raw = row.get("max_cmb_diff")
            rms_cmb_raw = row.get("rms_cmb_diff")

            max_cmb = float(max_cmb_raw) if max_cmb_raw is not None else None
            rms_cmb = float(rms_cmb_raw) if rms_cmb_raw is not None else None

            return V2Reference(
                beta=beta,
                sigma_z=sigma_z,
                delta_h0=delta_h0,
                max_cmb_diff=max_cmb,
                rms_cmb_diff=rms_cmb,
            )

    return None


def build_temp_ini(
    repo_root: str,
    base_ini: str,
    tag: str,
    root_override: str,
) -> str:
    """
    Create a temporary .ini that:
      - includes all lines from base_ini (except existing root = lines)
      - appends a new root = ... (override)
      - forces write_background = yes
    Returns the path to the new .ini file.
    """
    src_path = os.path.join(repo_root, base_ini)
    if not os.path.exists(src_path):
        print(f"[ERROR] Base ini not found: {src_path}", file=sys.stderr)
        sys.exit(1)

    tmp_ini = os.path.join(repo_root, f"unified_metrics_{tag}.ini")

    with open(src_path, "r") as f_in, open(tmp_ini, "w") as f_out:
        for line in f_in:
            # Skip existing root = and write background = lines to avoid duplicate parameter error
            stripped = line.strip()
            if stripped.startswith("root =") or stripped.startswith("root="):
                continue
            if stripped.startswith("write background") or stripped.startswith("write_background"):
                continue
            f_out.write(line)

        f_out.write("\n")
        f_out.write("# --- Overrides by test_unified_cdm_metrics.py ---\n")
        f_out.write(f"root = {root_override}\n")
        f_out.write("write background = yes\n")

    return tmp_ini


def run_class(class_bin: str, ini_path: str) -> None:
    """Run CLASS with given ini file and raise if it fails."""
    cmd = [class_bin, ini_path]
    print(f"  → Running CLASS: {' '.join(cmd)}")
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if proc.returncode != 0:
        print("  ❌ CLASS failed!")
        print("  --- Output ---")
        print(proc.stdout)
        sys.exit(1)
    else:
        print("  ✓ CLASS completed successfully")


def parse_background_rs(background_path: str) -> float:
    """
    Parse the background output file and return the final comoving sound
    horizon value (r_s, column 8 in CLASS background output).
    """
    if not os.path.exists(background_path):
        print(f"[ERROR] Background file not found: {background_path}", file=sys.stderr)
        sys.exit(1)

    # Column 8 is comov.snd.hrz. (r_s) in CLASS background output
    # We want the last value (today, a=1, z=0)
    rs_column_index = 7  # 0-based index for column 8
    
    last_rs = None
    with open(background_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            try:
                # Get r_s from column 8
                rs_val = float(parts[rs_column_index])
                last_rs = rs_val
            except (ValueError, IndexError):
                continue

    if last_rs is None:
        print(f"[ERROR] Could not parse r_s from {background_path}", file=sys.stderr)
        sys.exit(1)

    return last_rs


def compute_metrics_from_rs(rs_model: float) -> UnifiedMetrics:
    """
    Given r_s(model), compute Δr_s/r_s, H0_eff, and ΔH0 using same logic as v2:
      H0_eff = H0_LCDM * (r_s_LCDM / r_s_model)
      ΔH0 = H0_eff - H0_LCDM
    """
    delta_rs_over_rs = (rs_model - RS_LCDM) / RS_LCDM
    h0_eff = H0_LCDM * (RS_LCDM / rs_model)
    delta_h0 = h0_eff - H0_LCDM

    return UnifiedMetrics(
        rs=rs_model,
        delta_rs_over_rs=delta_rs_over_rs,
        h0_eff=h0_eff,
        delta_h0=delta_h0,
    )


def run_case(
    case: CaseSpec,
    repo_root: str,
    class_bin: str,
    v2_results: Optional[list],
) -> ComparisonResult:
    """Run unified CLASS for a case and compare to v2 reference."""
    print("-" * 82)
    print(f"[{case.key.upper()}] Unified config: {case.ini_filename}")
    print(f"  Target v2 CDM params: beta = {case.beta:.3f}, sigma_z = {case.sigma_z:.3f}")

    v2_ref = None
    if v2_results is not None:
        v2_ref = match_v2_reference(v2_results, case.beta, case.sigma_z)
        if v2_ref is None:
            print("  [WARN] No matching v2 reference found in cdm_coupling_optimization_results.json")
        else:
            print(f"  v2 reference: ΔH₀ ≈ {v2_ref.delta_h0:.4f} km/s/Mpc, "
                  f"Max CMB Δ ≈ {v2_ref.max_cmb_diff or float('nan'):.1f}%, "
                  f"RMS CMB Δ ≈ {v2_ref.rms_cmb_diff or float('nan'):.1f}%")

    # Build temp ini with overridden root and background write
    root_tag = f"unified_metrics_{case.key}"
    tmp_ini = build_temp_ini(
        repo_root=repo_root,
        base_ini=case.ini_filename,
        tag=case.key,
        root_override=root_tag,
    )

    # Run CLASS
    run_class(class_bin, tmp_ini)

    # Background file path: CLASS may add 00 suffix, so check both
    background_path = os.path.join(repo_root, f"{root_tag}_background.dat")
    if not os.path.exists(background_path):
        # Try with 00 suffix that CLASS sometimes adds
        background_path = os.path.join(repo_root, f"{root_tag}00_background.dat")
    
    rs_model = parse_background_rs(background_path)

    unified_metrics = compute_metrics_from_rs(rs_model)

    print(f"  r_s(model)   = {unified_metrics.rs:.6f} Mpc")
    print(f"  Δr_s/r_s     = {100.0 * unified_metrics.delta_rs_over_rs:.3f}%")
    print(f"  H₀^eff(model) = {unified_metrics.h0_eff:.4f} km/s/Mpc")
    print(f"  ΔH₀(model)    = {unified_metrics.delta_h0:.4f} km/s/Mpc")

    # Compare to v2 if available
    if v2_ref is not None:
        diff = unified_metrics.delta_h0 - v2_ref.delta_h0
        rel = diff / v2_ref.delta_h0 if v2_ref.delta_h0 != 0.0 else float("nan")
        print(f"  ΔH₀(unified) - ΔH₀(v2) = {diff:+.4f} km/s/Mpc "
              f"({100.0 * rel:.2f}% difference)")

        # Simple acceptance criterion
        abs_tol = 0.10      # km/s/Mpc
        rel_tol = 0.05      # 5%
        if abs(diff) <= abs_tol or abs(rel) <= rel_tol:
            print("  → ✅ Unified matches v2 ΔH₀ within tolerance.")
        else:
            print("  → ⚠️ Unified ΔH₀ deviates from v2 by more than tolerance.")

    return ComparisonResult(case=case, v2=v2_ref, unified=unified_metrics)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 82)
    print("RIDDER UNIFIED POTENTIAL – CDM METRICS VALIDATION")
    print("=" * 82)

    repo_root = find_repo_root()
    print(f"Repo root: {repo_root}")
    class_bin = ensure_class_binary(repo_root)
    print(f"CLASS bin: {class_bin}\n")

    v2_results = load_v2_results(repo_root)

    cases = [
        CaseSpec(
            key="hero",
            label="Hero CDM config",
            ini_filename="unified_cdm_hero.ini",
            beta=0.20,
            sigma_z=0.50,
        ),
        CaseSpec(
            key="safe",
            label="Safe CDM config",
            ini_filename="unified_cdm_safe.ini",
            beta=0.15,
            sigma_z=0.50,
        ),
    ]

    results: Dict[str, ComparisonResult] = {}

    for case in cases:
        res = run_case(case, repo_root, class_bin, v2_results)
        results[case.key] = res

    print("-" * 82)
    print("SUMMARY")
    print("-" * 82)
    for key, res in results.items():
        v2_str = "N/A"
        if res.v2 is not None:
            v2_str = f"{res.v2.delta_h0:+.4f} km/s/Mpc"
        print(f"{key:5s} | ΔH₀ (unified) = {res.unified.delta_h0:+.4f} km/s/Mpc, "
              f"ΔH₀ (v2) = {v2_str}")

    print("\nValidation complete.")
    print("If unified ΔH₀ matches v2 within ~5%, unified CDM coupling is metrically")
    print("aligned with the original v2 implementation and is safe for MCMC.\n")


if __name__ == "__main__":
    main()
