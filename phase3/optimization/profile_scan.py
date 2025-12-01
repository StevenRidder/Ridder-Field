#!/usr/bin/env python3
"""
Profile Likelihood Scan for Ridder Field Fixed Parameters

Scans over n_ridder and sigma_ln_a to find optimal values.
These are "fixed by theory" but we want to verify the data agree.

Usage:
    python profile_scan.py --param n_ridder --range 2.5 3.5 --steps 5
    python profile_scan.py --param sigma_ln_a --range 0.4 1.0 --steps 7
    python profile_scan.py --all  # Run both scans
"""

import argparse
import numpy as np
import subprocess
import yaml
import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Base config template
BASE_CONFIG = """
theory:
  classy:
    extra_args:
      output: tCl, pCl, lCl, mPk
      l_max_scalars: 3000
      lensing: true
      gauge: newtonian
      recombination: recfast
      non_linear: none
      # OPTIMIZED tolerances
      tol_background_integration: 1e-4
      tol_perturb_integration: 1e-8
      k_per_decade_for_pk: 20
      k_per_decade_for_bao: 200
      # Fixed Ridder shape parameters
      n_ridder: {n_ridder}
      theta_i_ridder: 1.0
      beta_ridder: 0.0
      f_axion_ridder: 1.0e+27

likelihood:
  planck_2018_lowl.TT:
  planck_2018_lowl.EE:
  planck_2018_highl_plik.TTTEEE:
  planck_2018_lensing.clik:
  bao.sixdf_2011_bao:
  bao.sdss_dr7_mgs:
  bao.sdss_dr12_consensus_bao:
  sn.pantheonplus:
  shoes_h0:
    external: "lambda H0: -0.5*((H0 - 73.04)/1.04)**2"
    output_params: [chi2__shoes_h0]

params:
  logA:
    prior: {{min: 2.5, max: 3.5}}
    ref: 3.044
    proposal: 0.01
    drop: true
  A_s:
    value: "lambda logA: 1e-10*np.exp(logA)"
    latex: A_s
  n_s:
    prior: {{min: 0.92, max: 1.0}}
    ref: 0.9649
    proposal: 0.004
    latex: n_s
  H0:
    prior: {{min: 60, max: 80}}
    ref: 70.5
    proposal: 0.5
    latex: H_0
  omega_b:
    prior: {{min: 0.019, max: 0.025}}
    ref: 0.02237
    proposal: 0.0002
    latex: \\Omega_b h^2
  omega_cdm:
    prior: {{min: 0.09, max: 0.14}}
    ref: 0.117
    proposal: 0.003
    latex: \\Omega_c h^2
  tau_reio:
    prior: {{min: 0.01, max: 0.1}}
    ref: 0.0544
    proposal: 0.006
    latex: \\tau_{{reio}}
  Lambda_EDE_ridder:
    prior: {{min: 0.1, max: 3.0}}
    ref: 1.0
    proposal: 0.2
    latex: \\Lambda_{{EDE}}
  Omega_m:
    latex: \\Omega_m
  sigma8:
    latex: \\sigma_8
  S8:
    derived: "lambda sigma8, Omega_m: sigma8*np.sqrt(Omega_m/0.3)"
    latex: S_8
  rs_drag:
    derived: true
    latex: r_s

sampler:
  mcmc:
    max_samples: 500
    Rminus1_stop: 0.1
    burn_in: 20
    learn_proposal: true
    max_tries: 10000
    proposal_scale: 2.0

output: chains/profile_{param_name}_{value:.2f}
resume: false
"""


def create_config(param_name: str, value: float, output_dir: Path) -> Path:
    """Create a YAML config for a specific parameter value."""
    
    config_content = BASE_CONFIG.format(
        n_ridder=value if param_name == 'n_ridder' else 3.0,
        param_name=param_name,
        value=value
    )
    
    config_path = output_dir / f"profile_{param_name}_{value:.2f}.yaml"
    config_path.write_text(config_content)
    return config_path


def run_profile_point(config_path: Path, timeout: int = 7200) -> dict:
    """Run a single profile point and extract results."""
    
    print(f"  Running: {config_path.name}")
    
    try:
        result = subprocess.run(
            ['cobaya-run', str(config_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Extract chain output path
        chain_base = config_path.stem
        chain_file = config_path.parent.parent / 'chains' / f"{chain_base}.1.txt"
        
        if chain_file.exists():
            # Load chain and find minimum chi2
            data = np.loadtxt(chain_file)
            min_idx = np.argmin(data[:, 1])  # Column 1 is usually minuslogpost
            min_chi2 = 2 * data[min_idx, 1]  # Convert to chi2
            
            # Get H0, S8 at minimum
            # Need to check column mapping from .paramnames file
            return {
                'chi2': min_chi2,
                'n_samples': len(data),
                'success': True
            }
        else:
            return {'chi2': np.nan, 'success': False, 'error': 'No chain file'}
            
    except subprocess.TimeoutExpired:
        return {'chi2': np.nan, 'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'chi2': np.nan, 'success': False, 'error': str(e)}


def run_profile_scan(param_name: str, values: np.ndarray, output_dir: Path) -> dict:
    """Run a full profile scan over a parameter."""
    
    print(f"\n{'='*60}")
    print(f"PROFILE SCAN: {param_name}")
    print(f"Values: {values}")
    print(f"{'='*60}\n")
    
    results = []
    
    for val in values:
        config_path = create_config(param_name, val, output_dir)
        result = run_profile_point(config_path)
        result['value'] = val
        results.append(result)
        
        status = "✓" if result['success'] else "✗"
        chi2_str = f"{result['chi2']:.1f}" if result['success'] else "N/A"
        print(f"  {param_name} = {val:.2f}: χ² = {chi2_str} {status}")
    
    return {
        'param': param_name,
        'values': values,
        'results': results
    }


def plot_profile(scan_results: dict, output_path: Path):
    """Plot the profile likelihood."""
    
    param = scan_results['param']
    values = np.array([r['value'] for r in scan_results['results']])
    chi2 = np.array([r['chi2'] for r in scan_results['results']])
    
    # Find minimum
    valid = ~np.isnan(chi2)
    if not np.any(valid):
        print("No valid results to plot!")
        return
    
    min_idx = np.argmin(chi2[valid])
    min_val = values[valid][min_idx]
    min_chi2 = chi2[valid][min_idx]
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(values[valid], chi2[valid] - min_chi2, 'bo-', markersize=10, linewidth=2)
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    plt.axhline(1, color='r', linestyle='--', alpha=0.5, label='1σ')
    plt.axhline(4, color='orange', linestyle='--', alpha=0.5, label='2σ')
    
    plt.axvline(min_val, color='green', linestyle=':', alpha=0.7, 
                label=f'Best: {param} = {min_val:.2f}')
    
    # Mark current default
    if param == 'n_ridder':
        plt.axvline(3.0, color='purple', linestyle='--', alpha=0.7, label='Current: 3.0')
    elif param == 'sigma_ln_a':
        plt.axvline(0.8, color='purple', linestyle='--', alpha=0.7, label='Current: 0.8')
    
    plt.xlabel(f'{param}', fontsize=14)
    plt.ylabel('Δχ² from minimum', fontsize=14)
    plt.title(f'Profile Likelihood: {param}', fontsize=16)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n  Plot saved: {output_path}")
    print(f"  OPTIMAL VALUE: {param} = {min_val:.3f} (Δχ² = 0)")
    
    # Calculate improvement vs default
    if param == 'n_ridder':
        default_idx = np.argmin(np.abs(values - 3.0))
        if valid[default_idx]:
            improvement = chi2[default_idx] - min_chi2
            print(f"  IMPROVEMENT vs default (3.0): Δχ² = -{improvement:.1f}")
    elif param == 'sigma_ln_a':
        default_idx = np.argmin(np.abs(values - 0.8))
        if valid[default_idx]:
            improvement = chi2[default_idx] - min_chi2
            print(f"  IMPROVEMENT vs default (0.8): Δχ² = -{improvement:.1f}")


def main():
    parser = argparse.ArgumentParser(description='Profile likelihood scan for Ridder field parameters')
    parser.add_argument('--param', choices=['n_ridder', 'sigma_ln_a'], 
                        help='Parameter to scan')
    parser.add_argument('--range', nargs=2, type=float, default=[2.5, 3.5],
                        help='Min and max values for scan')
    parser.add_argument('--steps', type=int, default=5,
                        help='Number of steps in scan')
    parser.add_argument('--all', action='store_true',
                        help='Run both n_ridder and sigma_ln_a scans')
    parser.add_argument('--output-dir', type=Path, default=Path('optimization/configs'),
                        help='Output directory for configs')
    parser.add_argument('--dry-run', action='store_true',
                        help='Just create configs, don\'t run')
    
    args = parser.parse_args()
    
    # Setup output directory
    output_dir = Path(__file__).parent / 'configs'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plots_dir = Path(__file__).parent / 'plots'
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    if args.all:
        # Run both scans
        scans = [
            ('n_ridder', np.linspace(2.5, 3.5, 5)),
            ('sigma_ln_a', np.linspace(0.4, 1.0, 7))
        ]
    elif args.param:
        scans = [(args.param, np.linspace(args.range[0], args.range[1], args.steps))]
    else:
        parser.print_help()
        sys.exit(1)
    
    all_results = {}
    
    for param_name, values in scans:
        if args.dry_run:
            print(f"\n[DRY RUN] Would scan {param_name} over: {values}")
            for val in values:
                config_path = create_config(param_name, val, output_dir)
                print(f"  Created: {config_path}")
        else:
            results = run_profile_scan(param_name, values, output_dir)
            all_results[param_name] = results
            
            # Plot results
            plot_path = plots_dir / f"profile_{param_name}.png"
            plot_profile(results, plot_path)
    
    # Summary
    if not args.dry_run and all_results:
        print("\n" + "="*60)
        print("PROFILE SCAN SUMMARY")
        print("="*60)
        
        for param, results in all_results.items():
            valid_results = [r for r in results['results'] if r['success']]
            if valid_results:
                best = min(valid_results, key=lambda x: x['chi2'])
                print(f"\n{param}:")
                print(f"  Optimal value: {best['value']:.3f}")
                print(f"  Best χ²: {best['chi2']:.1f}")


if __name__ == '__main__':
    main()
