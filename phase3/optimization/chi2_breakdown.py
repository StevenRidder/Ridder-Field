#!/usr/bin/env python3
"""
χ² Breakdown Diagnostic

Decomposes the total χ² into contributions from each likelihood component.
This helps identify where EDE is gaining or losing relative to ΛCDM.

Usage:
    python chi2_breakdown.py --ede-chain chains/tier5_ede_shoes_predesi.1.txt \
                              --lcdm-chain chains/tier5_lcdm_shoes_predesi.1.txt
    
    python chi2_breakdown.py --params '{"H0": 70.5, "omega_b": 0.02237, ...}'
"""

import argparse
import numpy as np
import sys
from pathlib import Path
from typing import Dict, Optional
import json

# Try to import cobaya for direct likelihood evaluation
try:
    from cobaya.model import get_model
    from cobaya.run import run
    COBAYA_AVAILABLE = True
except ImportError:
    COBAYA_AVAILABLE = False
    print("Warning: Cobaya not available. Using chain-based analysis only.")


def load_chain(chain_path: Path) -> Dict:
    """Load chain and extract best-fit point."""
    
    # Load parameter names
    paramnames_path = chain_path.with_suffix('.paramnames')
    if paramnames_path.exists():
        with open(paramnames_path) as f:
            param_names = [line.split()[0].strip('*') for line in f if line.strip()]
    else:
        param_names = None
    
    # Load chain data
    data = np.loadtxt(chain_path)
    
    # Find best-fit (minimum -logpost, which is column 1)
    min_idx = np.argmin(data[:, 1])
    best_sample = data[min_idx]
    
    # Parse
    result = {
        'weight': best_sample[0],
        'minuslogpost': best_sample[1],
        'chi2_total': 2 * best_sample[1],
        'n_samples': len(data),
        'raw_data': data
    }
    
    # Add parameter values if we have names
    if param_names and len(param_names) <= len(best_sample) - 2:
        result['params'] = {}
        for i, name in enumerate(param_names):
            result['params'][name] = best_sample[2 + i]
    
    return result


def extract_chi2_from_chain_columns(chain_path: Path) -> Dict[str, float]:
    """
    Extract individual likelihood χ² from chain columns.
    
    Cobaya stores chi2__<likelihood> columns in the chain.
    """
    
    paramnames_path = chain_path.with_suffix('.paramnames')
    
    if not paramnames_path.exists():
        return {}
    
    # Parse param names to find chi2 columns
    chi2_cols = {}
    with open(paramnames_path) as f:
        for i, line in enumerate(f):
            name = line.split()[0].strip('*')
            if name.startswith('chi2__'):
                chi2_cols[name] = i + 2  # +2 for weight and minuslogpost columns
    
    if not chi2_cols:
        return {}
    
    # Load chain and extract chi2 at best-fit
    data = np.loadtxt(chain_path)
    min_idx = np.argmin(data[:, 1])
    
    chi2_breakdown = {}
    for name, col in chi2_cols.items():
        if col < data.shape[1]:
            likelihood_name = name.replace('chi2__', '')
            chi2_breakdown[likelihood_name] = data[min_idx, col]
    
    return chi2_breakdown


def analyze_chain_pair(ede_chain: Path, lcdm_chain: Path) -> Dict:
    """Compare EDE and ΛCDM chains."""
    
    print(f"\n{'='*70}")
    print("χ² BREAKDOWN ANALYSIS")
    print(f"{'='*70}")
    
    # Load chains
    print(f"\nLoading EDE chain: {ede_chain}")
    ede_data = load_chain(ede_chain)
    ede_chi2 = extract_chi2_from_chain_columns(ede_chain)
    
    print(f"Loading ΛCDM chain: {lcdm_chain}")
    lcdm_data = load_chain(lcdm_chain)
    lcdm_chi2 = extract_chi2_from_chain_columns(lcdm_chain)
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n{'Model':<15} {'Total χ²':<12} {'N samples':<12}")
    print("-" * 40)
    print(f"{'ΛCDM':<15} {lcdm_data['chi2_total']:<12.1f} {lcdm_data['n_samples']:<12}")
    print(f"{'EDE':<15} {ede_data['chi2_total']:<12.1f} {ede_data['n_samples']:<12}")
    print("-" * 40)
    print(f"{'Δχ² (EDE-ΛCDM)':<15} {ede_data['chi2_total'] - lcdm_data['chi2_total']:<12.1f}")
    
    # Breakdown by likelihood
    if ede_chi2 and lcdm_chi2:
        print(f"\n{'='*70}")
        print("BREAKDOWN BY LIKELIHOOD")
        print(f"{'='*70}")
        
        print(f"\n{'Likelihood':<35} {'ΛCDM χ²':<12} {'EDE χ²':<12} {'Δχ²':<10}")
        print("-" * 70)
        
        all_likelihoods = set(ede_chi2.keys()) | set(lcdm_chi2.keys())
        
        total_delta = 0
        breakdown = {}
        
        for lik in sorted(all_likelihoods):
            ede_val = ede_chi2.get(lik, np.nan)
            lcdm_val = lcdm_chi2.get(lik, np.nan)
            
            if not np.isnan(ede_val) and not np.isnan(lcdm_val):
                delta = ede_val - lcdm_val
                total_delta += delta
                breakdown[lik] = delta
                
                # Color code
                if delta < -2:
                    indicator = "✓ EDE wins"
                elif delta > 2:
                    indicator = "✗ EDE loses"
                else:
                    indicator = "~"
                
                print(f"{lik:<35} {lcdm_val:<12.1f} {ede_val:<12.1f} {delta:+.1f}  {indicator}")
            else:
                print(f"{lik:<35} {'N/A':<12} {'N/A':<12}")
        
        print("-" * 70)
        print(f"{'TOTAL':<35} {'':<12} {'':<12} {total_delta:+.1f}")
        
        # Analysis
        print(f"\n{'='*70}")
        print("ANALYSIS")
        print(f"{'='*70}")
        
        if breakdown:
            worst = max(breakdown.items(), key=lambda x: x[1])
            best = min(breakdown.items(), key=lambda x: x[1])
            
            print(f"\n🔴 BIGGEST χ² PENALTY:")
            print(f"   {worst[0]}: Δχ² = {worst[1]:+.1f}")
            
            print(f"\n🟢 BIGGEST χ² GAIN:")
            print(f"   {best[0]}: Δχ² = {best[1]:+.1f}")
            
            # Recommendations
            print(f"\n📋 RECOMMENDATIONS:")
            
            if worst[1] > 5:
                print(f"   • Focus optimization on {worst[0]} likelihood")
                print(f"     This component is costing you {worst[1]:.1f} χ² units")
            
            if 'planck_2018_highl_plik' in breakdown and breakdown['planck_2018_highl_plik'] > 3:
                print(f"   • Check high-ℓ CMB residuals - may need tighter ℓ sampling")
            
            if 'bao' in ''.join(breakdown.keys()).lower():
                bao_total = sum(v for k, v in breakdown.items() if 'bao' in k.lower())
                if bao_total > 3:
                    print(f"   • BAO contributing Δχ² = {bao_total:.1f}")
                    print(f"     This is the 'geometry tax' from r_s reduction")
    
    # Parameter comparison
    if 'params' in ede_data and 'params' in lcdm_data:
        print(f"\n{'='*70}")
        print("KEY PARAMETERS AT BEST-FIT")
        print(f"{'='*70}")
        
        key_params = ['H0', 'sigma8', 'S8', 'rs_drag', 'omega_cdm', 'omega_b', 'n_s']
        
        print(f"\n{'Parameter':<15} {'ΛCDM':<15} {'EDE':<15} {'Δ':<10}")
        print("-" * 55)
        
        for param in key_params:
            if param in ede_data['params'] and param in lcdm_data['params']:
                ede_val = ede_data['params'][param]
                lcdm_val = lcdm_data['params'][param]
                delta = ede_val - lcdm_val
                print(f"{param:<15} {lcdm_val:<15.4f} {ede_val:<15.4f} {delta:+.4f}")
    
    return {
        'ede_chi2_total': ede_data['chi2_total'],
        'lcdm_chi2_total': lcdm_data['chi2_total'],
        'delta_chi2': ede_data['chi2_total'] - lcdm_data['chi2_total'],
        'breakdown': breakdown if ede_chi2 and lcdm_chi2 else {}
    }


def main():
    parser = argparse.ArgumentParser(description='χ² breakdown diagnostic')
    parser.add_argument('--ede-chain', type=Path, 
                        help='Path to EDE chain file')
    parser.add_argument('--lcdm-chain', type=Path,
                        help='Path to ΛCDM chain file')
    parser.add_argument('--chains-dir', type=Path, default=Path('chains'),
                        help='Directory containing chains')
    parser.add_argument('--world', type=str, default='shoes_predesi',
                        help='World name (e.g., shoes_predesi, shoes_desi)')
    
    args = parser.parse_args()
    
    # Determine chain paths
    if args.ede_chain and args.lcdm_chain:
        ede_chain = args.ede_chain
        lcdm_chain = args.lcdm_chain
    else:
        # Auto-detect from world name
        chains_dir = Path(__file__).parent.parent / 'chains'
        ede_chain = chains_dir / f'tier5_ede_{args.world}.1.txt'
        lcdm_chain = chains_dir / f'tier5_lcdm_{args.world}.1.txt'
    
    # Check existence
    if not ede_chain.exists():
        print(f"Error: EDE chain not found: {ede_chain}")
        sys.exit(1)
    if not lcdm_chain.exists():
        print(f"Error: ΛCDM chain not found: {lcdm_chain}")
        sys.exit(1)
    
    # Run analysis
    results = analyze_chain_pair(ede_chain, lcdm_chain)
    
    # Save results
    output_path = Path(__file__).parent / f'chi2_breakdown_{args.world}.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
