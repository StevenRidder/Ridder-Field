#!/usr/bin/env python3
"""
Parameter Grid Scanner for V2

Tool 2 from V2_INCREMENTAL_PLAN.md

Purpose: Find V2 parameters that produce observable EDE effects.
Tests: Lambda_EDE, theta_i, beta ranges to find optimal values.

Usage:
    python3 parameter_grid_scan.py --quick  # Fast scan (5 points)
    python3 parameter_grid_scan.py --full   # Full scan (25 points)
"""

import argparse
import numpy as np
import pandas as pd
from single_point_chi2 import test_single_point
import matplotlib.pyplot as plt
from pathlib import Path

def grid_scan(Lambda_range, theta_i_range, beta_range, output_dir='../v2_grid_scan_results'):
    """
    Scan parameter space and save results.
    
    Parameters:
    -----------
    Lambda_range : list
        Values of Lambda_EDE to test
    theta_i_range : list
        Values of theta_i to test
    beta_range : list
        Values of beta to test
    output_dir : str
        Directory to save results
    
    Returns:
    --------
    DataFrame : Results with (Lambda_EDE, theta_i, beta, chi2, H0, success)
    """
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = []
    total_tests = len(Lambda_range) * len(theta_i_range) * len(beta_range)
    test_num = 0
    
    print("="*70)
    print("V2 PARAMETER GRID SCAN")
    print("="*70)
    print(f"Lambda_EDE: {Lambda_range}")
    print(f"theta_i:    {theta_i_range}")
    print(f"beta:       {beta_range}")
    print(f"Total tests: {total_tests}")
    print("="*70)
    print("")
    
    for Lambda in Lambda_range:
        for theta_i in theta_i_range:
            for beta in beta_range:
                test_num += 1
                print(f"Test {test_num}/{total_tests}: Lambda={Lambda:.2f}, theta_i={theta_i:.2f}, beta={beta:.3f}")
                
                result = test_single_point(
                    Lambda_EDE=Lambda,
                    theta_i=theta_i,
                    beta=beta,
                    verbose=False
                )
                
                if result['success']:
                    print(f"  ✓ χ² = {result['chi2']:.1f}, H₀ = {result['H0']:.2f}")
                    results.append({
                        'Lambda_EDE': Lambda,
                        'theta_i': theta_i,
                        'beta': beta,
                        'chi2': result['chi2'],
                        'H0': result['H0'],
                        'success': True
                    })
                else:
                    print(f"  ✗ FAILED")
                    results.append({
                        'Lambda_EDE': Lambda,
                        'theta_i': theta_i,
                        'beta': beta,
                        'chi2': np.inf,
                        'H0': np.nan,
                        'success': False
                    })
    
    df = pd.DataFrame(results)
    
    # Save results
    csv_path = f"{output_dir}/grid_scan_results.csv"
    df.to_csv(csv_path, index=False)
    print("")
    print(f"✓ Results saved to {csv_path}")
    
    return df


def plot_results(df, output_dir='../v2_grid_scan_results'):
    """
    Generate plots from grid scan results.
    """
    
    # Get LCDM baseline (Lambda=0, beta=0)
    lcdm_chi2 = df[(df['Lambda_EDE'] == 0) & (df['beta'] == 0)]['chi2'].iloc[0]
    
    # Compute Delta chi2
    df['delta_chi2'] = df['chi2'] - lcdm_chi2
    
    # Filter successful runs
    df_success = df[df['success'] == True].copy()
    
    if len(df_success) == 0:
        print("⚠️ No successful runs to plot")
        return
    
    # Plot 1: Chi2 vs Lambda_EDE (for each beta)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for beta in df_success['beta'].unique():
        df_beta = df_success[df_success['beta'] == beta]
        axes[0].plot(df_beta['Lambda_EDE'], df_beta['chi2'], 'o-', label=f'β={beta:.3f}')
    
    axes[0].axhline(lcdm_chi2, color='k', linestyle='--', label='ΛCDM')
    axes[0].axhline(lcdm_chi2 + 10, color='r', linestyle=':', label='Δχ²=10 threshold')
    axes[0].set_xlabel('Lambda_EDE')
    axes[0].set_ylabel('χ²')
    axes[0].set_title('χ² vs Lambda_EDE')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: H0 vs Lambda_EDE
    for beta in df_success['beta'].unique():
        df_beta = df_success[df_success['beta'] == beta]
        axes[1].plot(df_beta['Lambda_EDE'], df_beta['H0'], 'o-', label=f'β={beta:.3f}')
    
    axes[1].axhline(67.36, color='k', linestyle='--', label='Planck baseline')
    axes[1].axhline(73.04, color='r', linestyle=':', label='SH0ES')
    axes[1].set_xlabel('Lambda_EDE')
    axes[1].set_ylabel('H₀ (km/s/Mpc)')
    axes[1].set_title('H₀ vs Lambda_EDE')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = f"{output_dir}/grid_scan_chi2_H0.png"
    plt.savefig(plot_path, dpi=150)
    print(f"✓ Plot saved to {plot_path}")
    
    # Plot 3: Heatmap of Delta chi2 (Lambda vs theta_i)
    if len(df_success['theta_i'].unique()) > 1:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Pivot for heatmap
        pivot = df_success.pivot_table(
            values='delta_chi2',
            index='theta_i',
            columns='Lambda_EDE',
            aggfunc='mean'
        )
        
        im = ax.imshow(pivot.values, cmap='RdYlGn_r', aspect='auto', vmin=-10, vmax=50)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f'{x:.2f}' for x in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([f'{y:.2f}' for y in pivot.index])
        ax.set_xlabel('Lambda_EDE')
        ax.set_ylabel('theta_i')
        ax.set_title('Δχ² Heatmap (relative to ΛCDM)')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Δχ²')
        
        # Add text annotations
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                text = ax.text(j, i, f'{pivot.values[i, j]:.1f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        plt.tight_layout()
        heatmap_path = f"{output_dir}/grid_scan_heatmap.png"
        plt.savefig(heatmap_path, dpi=150)
        print(f"✓ Heatmap saved to {heatmap_path}")
    
    plt.close('all')


def summarize_results(df):
    """
    Print summary of grid scan results.
    """
    
    # Get LCDM baseline
    lcdm = df[(df['Lambda_EDE'] == 0) & (df['beta'] == 0)].iloc[0]
    lcdm_chi2 = lcdm['chi2']
    lcdm_H0 = lcdm['H0']
    
    df_success = df[df['success'] == True].copy()
    df_success['delta_chi2'] = df_success['chi2'] - lcdm_chi2
    df_success['delta_H0'] = df_success['H0'] - lcdm_H0
    
    print("")
    print("="*70)
    print("GRID SCAN SUMMARY")
    print("="*70)
    print(f"ΛCDM Baseline: χ² = {lcdm_chi2:.2f}, H₀ = {lcdm_H0:.2f} km/s/Mpc")
    print("")
    
    # Find best fits
    print("TOP 5 BEST FITS (lowest χ²):")
    top5 = df_success.nsmallest(5, 'chi2')
    for i, row in top5.iterrows():
        print(f"  {i+1}. Lambda={row['Lambda_EDE']:.2f}, theta_i={row['theta_i']:.2f}, beta={row['beta']:.3f}")
        print(f"     χ² = {row['chi2']:.2f} (Δχ² = {row['delta_chi2']:+.2f})")
        print(f"     H₀ = {row['H0']:.2f} (ΔH₀ = {row['delta_H0']:+.2f})")
    
    print("")
    print("TOP 5 HIGHEST H₀:")
    top5_H0 = df_success.nlargest(5, 'H0')
    for i, row in top5_H0.iterrows():
        print(f"  {i+1}. Lambda={row['Lambda_EDE']:.2f}, theta_i={row['theta_i']:.2f}, beta={row['beta']:.3f}")
        print(f"     H₀ = {row['H0']:.2f} (ΔH₀ = {row['delta_H0']:+.2f})")
        print(f"     χ² = {row['chi2']:.2f} (Δχ² = {row['delta_chi2']:+.2f})")
    
    print("")
    print("ACCEPTABLE MODELS (Δχ² < 10 AND ΔH₀ > 0.5):")
    acceptable = df_success[(df_success['delta_chi2'] < 10) & (df_success['delta_H0'] > 0.5)]
    if len(acceptable) > 0:
        for i, row in acceptable.iterrows():
            print(f"  ✓ Lambda={row['Lambda_EDE']:.2f}, theta_i={row['theta_i']:.2f}, beta={row['beta']:.3f}")
            print(f"    χ² = {row['chi2']:.2f} (Δχ² = {row['delta_chi2']:+.2f})")
            print(f"    H₀ = {row['H0']:.2f} (ΔH₀ = {row['delta_H0']:+.2f})")
    else:
        print("  ❌ No models found with Δχ² < 10 AND ΔH₀ > 0.5")
        print("  → Need to expand parameter ranges or fix V2 implementation")
    
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description='V2 Parameter Grid Scanner')
    parser.add_argument('--quick', action='store_true', help='Quick scan (5 points, ~5 min)')
    parser.add_argument('--full', action='store_true', help='Full scan (25 points, ~25 min)')
    parser.add_argument('--aggressive', action='store_true', help='Aggressive scan (larger Lambda, ~10 min)')
    
    args = parser.parse_args()
    
    if args.quick:
        # Quick scan: 5 points
        Lambda_range = [0.0, 1.0, 2.0]
        theta_i_range = [2.0]
        beta_range = [0.0, 0.05]
        
    elif args.full:
        # Full scan: 25 points
        Lambda_range = [0.0, 0.5, 1.0, 1.5, 2.0]
        theta_i_range = [1.5, 2.0, 2.5]
        beta_range = [0.0, 0.02, 0.05]
        
    elif args.aggressive:
        # Aggressive: larger Lambda values
        Lambda_range = [0.0, 2.0, 5.0, 10.0]
        theta_i_range = [2.0, 2.5]
        beta_range = [0.0, 0.05]
        
    else:
        print("Please specify --quick, --full, or --aggressive")
        return
    
    # Run grid scan
    df = grid_scan(Lambda_range, theta_i_range, beta_range)
    
    # Plot results
    plot_results(df)
    
    # Summarize
    summarize_results(df)


if __name__ == '__main__':
    main()

