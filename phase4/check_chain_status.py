#!/usr/bin/env python3
"""
Paper 2 Chain Status Monitor
Shows: running status, samples, convergence, key parameters
"""

import os
import sys
import glob
import numpy as np
from datetime import datetime

# Try to import getdist for chain analysis
try:
    from getdist import loadMCSamples
    HAS_GETDIST = True
except ImportError:
    HAS_GETDIST = False
    print("Warning: getdist not installed. Install with: pip install getdist")

CHAINS_DIR = os.path.expanduser("~/Ridder-Field/phase4/chains")

# Key parameters to display
KEY_PARAMS = ['H0', 'omega_cdm', 'omega_b', 'tau_reio', 'n_s', 'sigma8', 'S8', 'rs_drag']
EDE_PARAMS = ['ridder_Lambda_EDE_eV', 'ridder_a_c', 'Lambda_EDE_ridder']

def check_process_running(chain_name):
    """Check if cobaya is running for this chain"""
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', chain_name], capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def get_log_info(chain_name):
    """Extract info from log file"""
    log_file = os.path.join(CHAINS_DIR, f"{chain_name}.log")
    if not os.path.exists(log_file):
        log_file = os.path.join(CHAINS_DIR, f"run_{chain_name.split('_')[-1]}.log")
    
    if not os.path.exists(log_file):
        return None
    
    info = {'samples': 0, 'accepted': 0, 'R-1': None, 'chi2': None, 'stage': 'unknown'}
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()[-200:]  # Last 200 lines
            for line in lines:
                if 'accepted' in line.lower() and '/' in line:
                    # Try to parse acceptance info
                    pass
                if 'R-1' in line or 'Rminus1' in line:
                    try:
                        # Extract R-1 value
                        parts = line.split('=')
                        if len(parts) > 1:
                            info['R-1'] = float(parts[-1].strip().split()[0])
                    except:
                        pass
                if 'chi2' in line.lower() or 'logp' in line.lower():
                    try:
                        if 'best' in line.lower():
                            parts = line.split('=')
                            if len(parts) > 1:
                                info['chi2'] = float(parts[-1].strip().split()[0])
                    except:
                        pass
                if 'burn' in line.lower():
                    info['stage'] = 'burn-in'
                elif 'sampling' in line.lower() or 'sample' in line.lower():
                    info['stage'] = 'sampling'
                elif 'initial' in line.lower():
                    info['stage'] = 'initializing'
    except:
        pass
    
    return info

def analyze_chain(chain_prefix):
    """Analyze chain using getdist"""
    if not HAS_GETDIST:
        return None
    
    chain_files = glob.glob(os.path.join(CHAINS_DIR, f"{chain_prefix}*.txt"))
    if not chain_files:
        return None
    
    try:
        samples = loadMCSamples(os.path.join(CHAINS_DIR, chain_prefix))
        
        stats = {
            'n_samples': samples.numrows,
            'params': {}
        }
        
        # Get parameter stats
        for param in KEY_PARAMS + EDE_PARAMS:
            try:
                p = samples.getParams()
                if hasattr(p, param):
                    vals = getattr(p, param)
                    stats['params'][param] = {
                        'mean': np.mean(vals),
                        'std': np.std(vals),
                        'best': vals[np.argmax(samples.loglikes)] if hasattr(samples, 'loglikes') else np.mean(vals)
                    }
            except:
                pass
        
        # Get chi2 if available
        try:
            if hasattr(samples, 'loglikes'):
                stats['best_chi2'] = -2 * np.max(samples.loglikes)
                stats['mean_chi2'] = -2 * np.mean(samples.loglikes)
        except:
            pass
        
        # Get R-1 convergence
        try:
            from getdist import plots
            # R-1 not directly available, would need multiple chains
        except:
            pass
        
        return stats
    except Exception as e:
        print(f"  Error analyzing {chain_prefix}: {e}")
        return None

def print_chain_status(name, prefix):
    """Print status for a single chain"""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    
    # Check if running
    is_running = check_process_running(prefix)
    status = "🟢 RUNNING" if is_running else "⏹️  STOPPED"
    print(f"Status: {status}")
    
    # Check log info
    log_info = get_log_info(prefix)
    if log_info:
        print(f"Stage:  {log_info.get('stage', 'unknown')}")
        if log_info.get('R-1'):
            print(f"R-1:    {log_info['R-1']:.4f}")
        if log_info.get('chi2'):
            print(f"χ²:     {log_info['chi2']:.1f}")
    
    # Analyze chain files
    stats = analyze_chain(prefix)
    if stats:
        print(f"\nSamples: {stats['n_samples']:,}")
        
        if stats.get('best_chi2'):
            print(f"Best χ²: {stats['best_chi2']:.1f}")
        
        print("\nKey Parameters:")
        print("-" * 45)
        for param, vals in stats.get('params', {}).items():
            if param in ['H0', 'sigma8', 'S8', 'rs_drag']:
                print(f"  {param:20s}: {vals['mean']:.3f} ± {vals['std']:.3f}")
            elif param in EDE_PARAMS:
                print(f"  {param:20s}: {vals['mean']:.4f} ± {vals['std']:.4f}")
    else:
        # Check for chain files
        chain_files = glob.glob(os.path.join(CHAINS_DIR, f"{prefix}*.txt"))
        if chain_files:
            print(f"\nChain files found: {len(chain_files)}")
            for f in chain_files[:3]:
                size = os.path.getsize(f) / 1024
                print(f"  {os.path.basename(f)}: {size:.1f} KB")
        else:
            print("\nNo chain files yet")

def main():
    print("\n" + "="*60)
    print("  PAPER 2 CHAIN STATUS MONITOR")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Memory check
    try:
        import subprocess
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        mem_line = [l for l in result.stdout.split('\n') if 'Mem:' in l][0]
        print(f"\nMemory: {mem_line}")
    except:
        pass
    
    # Check each chain
    chains = [
        ("Run A: EDE Marginalized", "run_a_ede_marginalized"),
        ("Run B: ΛCDM + Template", "run_b_lcdm_template"),
        ("Run C: Control (Planck-only)", "run_control_planck_only"),
    ]
    
    for name, prefix in chains:
        print_chain_status(name, prefix)
    
    print("\n" + "="*60)
    print("  Commands:")
    print("    tail -f chains/*.log     # Watch logs")
    print("    python check_chain_status.py  # Refresh status")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

