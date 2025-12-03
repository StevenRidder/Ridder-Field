#!/usr/bin/env python3
"""
UNIFIED GRID SCAN: Find the Pareto Frontier
============================================
Expanded 5x4 grid with goodness scoring to find the best trade-offs.

Grid:
  Lambda_tail ∈ {16, 18, 20, 22, 24} meV
  f_axion ∈ {0.30, 0.35, 0.40, 0.45}

Outputs:
  - Full results table
  - Pareto frontier points
  - Best compromise configuration
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Import the button API
from run_unified_model import run_unified_model, compute_goodness_score

# Grid definition
LAMBDA_TAIL_VALUES = [16e-3, 18e-3, 20e-3, 22e-3, 24e-3]
F_AXION_VALUES = [0.30, 0.35, 0.40, 0.45]

def is_pareto_optimal(point, all_points):
    """
    Check if a point is Pareto optimal.
    A point is Pareto optimal if no other point is strictly better
    in all objectives.
    
    Objectives (all to minimize):
    - negative H0 (want high H0)
    - S8 (want low S8)
    - CMB residual
    - BAO residual
    """
    for other in all_points:
        if other is point:
            continue
        
        # Other dominates if it's better or equal in all and strictly better in at least one
        h0_better = other['H0'] >= point['H0']
        s8_better = other['S8'] <= point['S8']
        cmb_better = other['cmb_rms'] <= point['cmb_rms']
        bao_better = other['bao_avg'] <= point['bao_avg']
        
        strictly_better = (
            other['H0'] > point['H0'] or
            other['S8'] < point['S8'] or
            other['cmb_rms'] < point['cmb_rms'] or
            other['bao_avg'] < point['bao_avg']
        )
        
        if h0_better and s8_better and cmb_better and bao_better and strictly_better:
            return False
    
    return True

def main():
    print("=" * 80)
    print("UNIFIED GRID SCAN: Find the Pareto Frontier")
    print("=" * 80)
    print()
    print(f"Grid: Λ_tail ∈ {[lt*1e3 for lt in LAMBDA_TAIL_VALUES]} meV")
    print(f"      f_axion ∈ {F_AXION_VALUES}")
    print(f"Total points: {len(LAMBDA_TAIL_VALUES) * len(F_AXION_VALUES)}")
    print()
    
    results = []
    
    print("Running grid...")
    print("-" * 90)
    print(f"{'Λ_tail':>6} {'f_ax':>5} {'H0':>7} {'S8':>7} {'f_EDE':>6} {'CMB%':>6} {'BAO%':>6} {'J':>7} {'Status':>8}")
    print("-" * 90)
    
    for i, lt in enumerate(LAMBDA_TAIL_VALUES):
        for j, fa in enumerate(F_AXION_VALUES):
            # Run model (skip LCDM after first run)
            summary = run_unified_model(lt, fa, run_lcdm=(i == 0 and j == 0))
            
            if not summary.get('success', False):
                print(f"{lt*1e3:>6.0f} {fa:>5.2f} {'FAILED':>7}")
                continue
            
            obs = summary['observables']
            scores = summary['scores']
            targets = summary['targets_met']
            
            H0 = obs.get('H0', 0)
            S8 = obs.get('S8', 0)
            f_EDE = obs.get('f_EDE', 0)
            cmb_rms = obs.get('cmb_rms_residual', 0) * 100
            bao_avg = np.mean([abs(v) for v in obs.get('bao_residuals', {}).values()]) * 100
            J = scores['J_total']
            
            # Status
            if targets['H0_above_71'] and targets['S8_below_078']:
                status = "★"
            elif targets['H0_above_71']:
                status = "H0"
            elif targets['S8_below_078']:
                status = "S8"
            else:
                status = "-"
            
            print(f"{lt*1e3:>6.0f} {fa:>5.2f} {H0:>7.2f} {S8:>7.4f} {f_EDE:>6.3f} {cmb_rms:>6.1f} {bao_avg:>6.1f} {J:>7.2f} {status:>8}")
            
            results.append({
                'lambda_tail_meV': lt * 1e3,
                'f_axion': fa,
                'H0': H0,
                'S8': S8,
                'f_EDE': f_EDE,
                'cmb_rms': cmb_rms / 100,
                'bao_avg': bao_avg / 100,
                'J': J,
                'targets_met': targets['H0_above_71'] and targets['S8_below_078'],
            })
    
    print("-" * 90)
    print()
    
    # Find Pareto frontier
    print("### PARETO FRONTIER ###")
    print()
    
    pareto_points = [p for p in results if is_pareto_optimal(p, results)]
    pareto_points.sort(key=lambda p: p['J'])
    
    if pareto_points:
        print(f"{'Λ_tail':>6} {'f_ax':>5} {'H0':>7} {'S8':>7} {'CMB%':>6} {'BAO%':>6} {'J':>7}")
        print("-" * 55)
        for p in pareto_points:
            mark = "★" if p['targets_met'] else ""
            print(f"{p['lambda_tail_meV']:>6.0f} {p['f_axion']:>5.2f} {p['H0']:>7.2f} {p['S8']:>7.4f} "
                  f"{p['cmb_rms']*100:>6.1f} {p['bao_avg']*100:>6.1f} {p['J']:>7.2f} {mark}")
    print()
    
    # Winners (both targets met)
    winners = [p for p in results if p['targets_met']]
    print(f"### WINNERS (H0>71 AND S8<0.78): {len(winners)}/{len(results)} ###")
    if winners:
        winners.sort(key=lambda p: p['J'])
        print()
        print("Best by J score:")
        for i, w in enumerate(winners[:5]):
            print(f"  {i+1}. Λ={w['lambda_tail_meV']:.0f}meV, f={w['f_axion']:.2f} → "
                  f"H0={w['H0']:.2f}, S8={w['S8']:.4f}, J={w['J']:.2f}")
    print()
    
    # Best compromise (lowest J among winners, or lowest J overall if no winners)
    if winners:
        best = min(winners, key=lambda p: p['J'])
        print("### BEST COMPROMISE (lowest J among winners) ###")
    else:
        best = min(results, key=lambda p: p['J'])
        print("### BEST COMPROMISE (lowest J overall - no winners) ###")
    
    print(f"  Λ_tail = {best['lambda_tail_meV']:.0f} meV")
    print(f"  f_axion = {best['f_axion']:.2f}")
    print(f"  H0 = {best['H0']:.2f} km/s/Mpc")
    print(f"  S8 = {best['S8']:.4f}")
    print(f"  f_EDE = {best['f_EDE']:.4f}")
    print(f"  CMB RMS = {best['cmb_rms']*100:.1f}%")
    print(f"  BAO avg = {best['bao_avg']*100:.1f}%")
    print(f"  J = {best['J']:.2f}")
    print()
    
    # Save full results
    output = {
        'timestamp': datetime.now().isoformat(),
        'grid': {
            'lambda_tail_meV': [lt * 1e3 for lt in LAMBDA_TAIL_VALUES],
            'f_axion': F_AXION_VALUES,
        },
        'results': results,
        'pareto_frontier': pareto_points,
        'winners': winners,
        'best_compromise': best,
        'summary': {
            'total_points': len(results),
            'winners': len(winners),
            'pareto_points': len(pareto_points),
        }
    }
    
    output_file = "unified_grid_scan_results.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Full results saved to: {output_file}")

if __name__ == "__main__":
    main()

