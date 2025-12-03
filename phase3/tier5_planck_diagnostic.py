#!/usr/bin/env python3
"""
Tier 5: Planck-only chi2 diagnostic

Goal:
    Isolate how much of the Δχ² between ΛCDM and EDE comes from Planck, and
    which Planck blocks (high-l TTTEEE, low-l TT/EE, lensing, etc.) are driving it.

Usage:
    ssh ridderadmin@172.191.4.60 "cd ~/Ridder-Field/phase3 && python3 tier5_planck_diagnostic.py"
"""

import numpy as np
import os
import sys

# Where chains live on the VM, with a local fallback for testing
CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
if not os.path.exists(CHAIN_DIR):
    CHAIN_DIR = "chains"

def load_chain(chain_file):
    """Load chain file, return (cols, col_map, data)."""
    if not os.path.exists(chain_file):
        print(f"   [warn] File not found: {chain_file}")
        return None, None, None

    with open(chain_file, "r") as f:
        header = f.readline().strip()

    if header.startswith("#"):
        header = header[1:]
    cols = header.split()
    col_map = {c.strip(): i for i, c in enumerate(cols)}

    data = np.loadtxt(chain_file)
    if len(data.shape) == 1:
        data = data.reshape(1, -1)

    return cols, col_map, data


def find_best_index(col_map, data):
    """Return index of best-fit sample using chi2 if available, else minuslogpost."""
    if "chi2" in col_map:
        return int(np.argmin(data[:, col_map["chi2"]]))
    elif "minuslogpost" in col_map:
        # chi2 ~ 2 * minuslogpost but we only need the minimum location
        return int(np.argmin(data[:, col_map["minuslogpost"]]))
    else:
        # Fallback: just use the last sample
        return len(data) - 1


def is_planck_chi2(col_name):
    """
    Heuristic to decide if a chi2 column belongs to Planck.

    We treat any chi2 column that mentions 'planck', 'plik', 'lowl',
    'highl', or 'lensing' as Planck-related.
    """
    if not col_name.startswith("chi2"):
        return False
    lower = col_name.lower()
    return (
        "planck" in lower
        or "plik" in lower
        or "lowl" in lower
        or "highl" in lower
        or "lensing" in lower
    )


def extract_planck_breakdown(cols, col_map, data, best_idx):
    """
    Return a dict of {planck_chi2_col: value} for the best-fit sample,
    plus the total Planck chi2 as a separate key 'PLANCK_TOTAL'.
    """
    best = data[best_idx]
    planck_cols = [c for c in cols if is_planck_chi2(c)]

    breakdown = {}
    total_planck = 0.0

    for c in sorted(planck_cols):
        val = float(best[col_map[c]])
        breakdown[c] = val
        total_planck += val

    breakdown["PLANCK_TOTAL"] = total_planck
    return breakdown


def print_single_chain_summary(label, chain_file):
    """
    Print a small summary for a single chain:
    - basic parameters (H0, S8, Omega_m, rs_drag)
    - all Planck chi2 components at the best-fit sample
    """
    print("\n" + "=" * 80)
    print(f"📊 {label}")
    print(f"   File: {os.path.basename(chain_file)}")
    print("=" * 80)

    cols, col_map, data = load_chain(chain_file)
    if cols is None:
        print("   ⚠️ Could not load chain")
        return None

    if len(data) < 5:
        print(f"   ⚠️ Only {len(data)} samples, too early for a stable best-fit")
        return None

    best_idx = find_best_index(col_map, data)
    best = data[best_idx]

    # Basic parameters at best-fit
    print(f"\n   Best-fit sample index: {best_idx} of {len(data)}")

    def maybe_print_param(name, label=None):
        if name in col_map:
            v = best[col_map[name]]
            label = label or name
            print(f"      {label}: {v:.4f}")

    print("\n   Key parameters at best-fit:")
    maybe_print_param("H0")
    maybe_print_param("S8")
    maybe_print_param("sigma8")
    maybe_print_param("Omega_m", label="Omega_m")
    maybe_print_param("rs_drag", label="rs_drag")
    maybe_print_param("rdrag", label="rdrag")

    # Planck chi2 breakdown
    breakdown = extract_planck_breakdown(cols, col_map, data, best_idx)

    if not breakdown or len(breakdown) == 1:
        print("\n   χ² Planck breakdown:")
        print("      (No Planck chi2 components found in header)")
        return breakdown

    print("\n   χ² Planck breakdown (best-fit sample):")
    planck_total = breakdown.pop("PLANCK_TOTAL", 0.0)

    for c in sorted(breakdown.keys()):
        short = c.replace("chi2__", "").replace("chi2_", "")
        print(f"      {short:<40} {breakdown[c]:>10.2f}")

    print(f"      {'PLANCK_TOTAL':<40} {planck_total:>10.2f}")

    # Put PLANCK_TOTAL back for downstream comparisons
    breakdown["PLANCK_TOTAL"] = planck_total
    return breakdown


def compare_world(world_label, lcdm_breakdown, ede_breakdown):
    """
    Compare Planck chi2 between ΛCDM and EDE for a given world.
    Prints per-block ΛCDM, EDE, and Δχ², plus total Δχ² for Planck-only.
    """
    if lcdm_breakdown is None or ede_breakdown is None:
        print(f"\n{world_label}: missing breakdowns, cannot compare")
        return

    print("\n" + "=" * 80)
    print(f"📐 Δχ² (Planck-only): {world_label}")
    print("=" * 80)
    print(f"   {'Component':<40} {'ΛCDM':>10} {'EDE':>10} {'Δχ²':>10}")
    print("   " + "-" * 70)

    keys = set(lcdm_breakdown.keys()) | set(ede_breakdown.keys())
    total_delta = 0.0

    for key in sorted(k for k in keys if k != "PLANCK_TOTAL"):
        lcdm_val = lcdm_breakdown.get(key, 0.0)
        ede_val = ede_breakdown.get(key, 0.0)
        delta = ede_val - lcdm_val
        total_delta += delta

        short = key.replace("chi2__", "").replace("chi2_", "")
        if abs(delta) > 20:
            marker = "⚠️"
        elif abs(delta) > 5:
            marker = "📌"
        else:
            marker = "  "

        print(f"   {marker} {short:<38} {lcdm_val:>10.1f} {ede_val:>10.1f} {delta:>+10.1f}")

    # Use the explicit PLANCK_TOTAL if it exists, else fall back to sum of parts
    lcdm_total = lcdm_breakdown.get("PLANCK_TOTAL", None)
    ede_total = ede_breakdown.get("PLANCK_TOTAL", None)
    if lcdm_total is not None and ede_total is not None:
        total_delta = ede_total - lcdm_total

    print("   " + "-" * 70)
    print(f"   {'PLANCK_TOTAL':<40} {lcdm_total if lcdm_total is not None else 0.0:>10.1f} "
          f"{ede_total if ede_total is not None else 0.0:>10.1f} {total_delta:>+10.1f}")


def main():
    print("=" * 80)
    print("TIER 5: PLANCK χ² DIAGNOSTIC")
    print("=" * 80)
    print("This script isolates Planck chi2 components from Tier 5 chains and compares")
    print("ΛCDM vs EDE in:")
    print("  - World A: DESI Y1 only (geometry first)")
    print("  - World B: DESI Y1 + Pantheon+")
    print("=" * 80)

    # Chain paths
    world_a_lcdm = os.path.join(CHAIN_DIR, "tier5_lcdm_desi_unconstrained.1.txt")
    world_a_ede  = os.path.join(CHAIN_DIR, "tier5_ede_desi_convergence.1.txt")

    world_b_lcdm = os.path.join(CHAIN_DIR, "tier5_lcdm_desi_pantheon_v2.1.txt")
    world_b_ede  = os.path.join(CHAIN_DIR, "tier5_ede_desi_pantheon_convergence.1.txt")

    # Per-chain summaries
    a_lcdm_break = print_single_chain_summary("World A: ΛCDM (DESI only)", world_a_lcdm)
    a_ede_break  = print_single_chain_summary("World A: EDE (DESI only)", world_a_ede)

    b_lcdm_break = print_single_chain_summary("World B: ΛCDM (DESI + Pantheon)", world_b_lcdm)
    b_ede_break  = print_single_chain_summary("World B: EDE (DESI + Pantheon)", world_b_ede)

    # Planck-only comparisons
    compare_world("World A: DESI only", a_lcdm_break, a_ede_break)
    compare_world("World B: DESI + Pantheon", b_lcdm_break, b_ede_break)

    print("\n" + "=" * 80)
    print("INTERPRETATION HINTS")
    print("=" * 80)
    print(
        "If PLANCK_TOTAL Δχ² is large (for example +80 to +120) while DESI Δχ² is small\n"
        "or even slightly negative, then the Planck CMB is the dominant source of tension\n"
        "for EDE. The per-component table will tell you whether that penalty is mostly\n"
        "in high-l TT/TE/EE, low-l polarization, or lensing.\n"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
