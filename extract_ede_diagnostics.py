#!/usr/bin/env python3
"""
Proper EDE Diagnostics from CLASS Background Table

Reads the full CLASS background output and computes:
- f_EDE(z) = rho_ridder(z) / rho_tot(z) over full range
- f_EDE_peak = global maximum (restricted to z > 100 for early universe)
- z_peak = redshift where peak occurs
- a_peak = scale factor at peak

No reliance on sparse debug prints - this is the ground truth.
"""

import numpy as np
import sys
import os
from pathlib import Path

def read_class_background(background_file):
    """
    Read CLASS background.dat file.
    
    Returns:
        dict with arrays: z, a, H, rho_cdm, rho_b, rho_g, rho_ur, rho_ridder, etc.
    """
    
    if not os.path.exists(background_file):
        raise FileNotFoundError(f"Background file not found: {background_file}")
    
    # Read header - CLASS format is "# 1:colname1 2:colname2 ..."
    columns = []
    with open(background_file, 'r') as f:
        for line in f:
            if line.startswith('#') and ':' in line:
                # Parse CLASS column header format: "# 1:z 2:time ..."
                parts = line.strip('#').split()
                for part in parts:
                    if ':' in part:
                        # Extract column name after ':'
                        col_name = part.split(':', 1)[1].strip()
                        columns.append(col_name)
                if columns:  # Found the column line
                    break
    
    if not columns:
        raise ValueError("Could not parse column headers from CLASS background file")
    
    # Read data
    data = np.loadtxt(background_file)
    
    # Build dictionary - CLASS columns are 1-indexed in header but 0-indexed in data
    bg = {}
    for i, col in enumerate(columns):
        if i < data.shape[1]:
            bg[col] = data[:, i]
    
    return bg, columns

def compute_ede_diagnostics(bg, z_min=100.0, z_max=1e6):
    """
    Compute EDE diagnostics from background arrays.
    
    Args:
        bg: dict with background arrays from CLASS
        z_min: minimum redshift for peak search (exclude late times)
        z_max: maximum redshift for peak search
    
    Returns:
        dict with: f_peak, z_peak, a_peak, z_array, f_array (full curves)
    """
    
    diagnostics = {
        'f_peak': None,
        'z_peak': None,
        'a_peak': None,
        'z_array': None,
        'f_array': None,
        'success': False,
        'error': None
    }
    
    try:
        # Get redshift array
        if 'z' in bg:
            z = bg['z']
        else:
            # Compute from scale factor if z not present
            if 'a' in bg:
                z = (1.0 / bg['a']) - 1.0
            else:
                raise KeyError("Neither 'z' nor 'a' found in background")
        
        # Get total density
        # CLASS format uses "(.)rho_tot" notation
        rho_tot = None
        for key in ['(.)rho_tot', 'rho_tot', '(.)rho_crit']:
            if key in bg:
                rho_tot = bg[key]
                break
        
        if rho_tot is None:
            # Try to reconstruct from components
            rho_tot = np.zeros_like(z)
            for key in bg.keys():
                if 'rho' in key.lower() and 'tot' not in key.lower() and 'ridder' not in key.lower():
                    rho_tot += bg[key]
        
        # Get Ridder density
        # CLASS format uses "(.)rho_ridder" notation
        rho_ridder = None
        for key in ['(.)rho_ridder', 'rho_ridder', '(.)rho_scf', 'rho_scf']:
            if key in bg:
                rho_ridder = bg[key]
                break
        
        if rho_ridder is None:
            diagnostics['error'] = "Could not find rho_ridder in background file"
            return diagnostics
        
        # Compute f_ridder = rho_ridder / rho_tot
        with np.errstate(divide='ignore', invalid='ignore'):
            f_ridder = rho_ridder / rho_tot
            f_ridder = np.nan_to_num(f_ridder, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Store full curves
        diagnostics['z_array'] = z
        diagnostics['f_array'] = f_ridder
        
        # Find peak in early universe (z > z_min)
        mask = (z >= z_min) & (z <= z_max) & np.isfinite(f_ridder)
        
        if not np.any(mask):
            diagnostics['error'] = f"No valid data points in range z ∈ [{z_min}, {z_max}]"
            return diagnostics
        
        z_search = z[mask]
        f_search = f_ridder[mask]
        
        # Find maximum
        idx_peak = np.argmax(f_search)
        
        diagnostics['f_peak'] = f_search[idx_peak]
        diagnostics['z_peak'] = z_search[idx_peak]
        diagnostics['a_peak'] = 1.0 / (1.0 + z_search[idx_peak])
        diagnostics['success'] = True
        
        return diagnostics
        
    except Exception as e:
        diagnostics['error'] = str(e)
        return diagnostics

def main():
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="Extract EDE diagnostics from CLASS background output"
    )
    parser.add_argument('background_file', type=str,
                        help='Path to CLASS background.dat file')
    parser.add_argument('--z-min', type=float, default=100.0,
                        help='Minimum redshift for peak search (default: 100)')
    parser.add_argument('--z-max', type=float, default=1e6,
                        help='Maximum redshift for peak search (default: 1e6)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output JSON file (default: print to stdout)')
    parser.add_argument('--plot', action='store_true',
                        help='Generate f_EDE(z) plot')
    
    args = parser.parse_args()
    
    # Read background
    try:
        bg, columns = read_class_background(args.background_file)
        print(f"Read background file with {len(bg['z'])} points", file=sys.stderr)
        print(f"Columns: {columns}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR reading background file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Compute diagnostics
    diag = compute_ede_diagnostics(bg, z_min=args.z_min, z_max=args.z_max)
    
    if not diag['success']:
        print(f"ERROR: {diag['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Print results
    print(f"\nEDE Diagnostics (z ∈ [{args.z_min}, {args.z_max}]):", file=sys.stderr)
    print(f"  f_EDE_peak = {diag['f_peak']:.6f}", file=sys.stderr)
    print(f"  z_peak     = {diag['z_peak']:.1f}", file=sys.stderr)
    print(f"  a_peak     = {diag['a_peak']:.6e}", file=sys.stderr)
    
    # Save or print JSON
    output_data = {
        'f_peak': float(diag['f_peak']),
        'z_peak': float(diag['z_peak']),
        'a_peak': float(diag['a_peak']),
        'z_min_search': args.z_min,
        'z_max_search': args.z_max,
        'background_file': args.background_file
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nSaved to: {args.output}", file=sys.stderr)
    else:
        print("\n" + json.dumps(output_data, indent=2))
    
    # Optional plot
    if args.plot:
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            z_arr = diag['z_array']
            f_arr = diag['f_array']
            
            # Plot full curve
            ax.loglog(z_arr, f_arr, 'b-', linewidth=2, label='f_EDE(z)')
            
            # Mark peak
            ax.plot(diag['z_peak'], diag['f_peak'], 'ro', markersize=10,
                    label=f'Peak: z={diag["z_peak"]:.1f}, f={diag["f_peak"]:.4f}')
            
            # Mark search window
            ax.axvline(args.z_min, color='gray', linestyle='--', alpha=0.5,
                      label=f'Search window: z > {args.z_min}')
            
            ax.set_xlabel('Redshift z', fontsize=14)
            ax.set_ylabel('f_EDE = ρ_ridder / ρ_tot', fontsize=14)
            ax.set_title('Early Dark Energy Fraction', fontsize=16)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=12)
            
            plot_file = args.background_file.replace('.dat', '_ede_diagnostic.png')
            plt.savefig(plot_file, dpi=150, bbox_inches='tight')
            print(f"Plot saved to: {plot_file}", file=sys.stderr)
            
        except ImportError:
            print("WARNING: matplotlib not available, skipping plot", file=sys.stderr)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

