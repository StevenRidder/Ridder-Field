#!/usr/bin/env python3
"""
ΛCDM vs Ridder Field Comparison Framework

Purpose:
- Run both ΛCDM and Ridder chains with same data
- Compare χ², posteriors, derived parameters
- Generate comparison plots and tables

Usage:
    python3 compare_lcdm_vs_ridder.py --profile planck_core --theory ridder
    python3 compare_lcdm_vs_ridder.py --profile planck_bao --theory lcdm
    python3 compare_lcdm_vs_ridder.py --profile planck_bao --compare
"""

import argparse
import subprocess
import sys
from pathlib import Path
import yaml

def create_lcdm_config(profile_config, output_prefix):
    """Create ΛCDM config from profile"""
    # Load profile
    with open("data_ladder_profiles.yaml", 'r') as f:
        profiles = yaml.safe_load(f)
    
    if profile_config not in profiles:
        print(f"❌ Profile not found: {profile_config}")
        sys.exit(1)
    
    profile = profiles[profile_config]
    
    # Create ΛCDM config
    lcdm_config = {
        "theory": {
            "classy": {
                "extra_args": {
                    "h": 0.72,
                    "omega_b": 0.02237,
                    "omega_cdm": 0.120,
                    "A_s": 2.1e-9,
                    "n_s": 0.9649,
                    "tau_reio": 0.054,
                    "output": "tCl",
                    "l_max_scalars": 2500,
                    "lensing": "yes",
                    "nonlinear": "halofit"
                }
            }
        },
        "likelihood": profile["likelihood"],
        "params": {
            "h": {"prior": {"min": 0.6, "max": 0.8}, "latex": "H_0"},
            "omega_b": {"prior": {"min": 0.02, "max": 0.025}, "latex": "\\Omega_b"},
            "omega_cdm": {"prior": {"min": 0.1, "max": 0.15}, "latex": "\\Omega_{cdm}"},
            "A_s": {"prior": {"min": 1.5e-9, "max": 2.5e-9}, "latex": "A_s"},
            "n_s": {"prior": {"min": 0.9, "max": 1.0}, "latex": "n_s"},
            "tau_reio": {"prior": {"min": 0.04, "max": 0.08}, "latex": "\\tau"}
        },
        "sampler": profile["sampler"],
        "output": f"chains/lcdm_{profile_config}"
    }
    
    # Save config
    config_file = f"lcdm_{profile_config}.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(lcdm_config, f, default_flow_style=False)
    
    return config_file

def create_ridder_config(profile_config, output_prefix):
    """Create Ridder config from profile"""
    # Load profile
    with open("data_ladder_profiles.yaml", 'r') as f:
        profiles = yaml.safe_load(f)
    
    if profile_config not in profiles:
        print(f"❌ Profile not found: {profile_config}")
        sys.exit(1)
    
    profile = profiles[profile_config]
    
    # Create Ridder config
    ridder_config = {
        "theory": {
            "classy": {
                "path": "/home/ridderadmin/Ridder-Field/phase2/class",
                "extra_args": {
                    "use_scf": "yes",
                    "scf_tuning_index": 0,
                    "attractor_ic_scf": "no",
                    "scf_parameters": "0.0, 0.0, 0.0, 0.0",
                    "Lambda_EDE_ridder": 1.0,
                    "f_axion_ridder": 1.0e27,
                    "n_ridder": 3,
                    "h": 0.72,
                    "omega_b": 0.02237,
                    "omega_cdm": 0.120,
                    "A_s": 2.1e-9,
                    "n_s": 0.9649,
                    "tau_reio": 0.054,
                    "output": "tCl",
                    "l_max_scalars": 2500,
                    "gauge": "newtonian",
                    "lensing": "yes",
                    "nonlinear": "halofit"
                }
            }
        },
        "likelihood": profile["likelihood"],
        "params": {
            "h": {"prior": {"min": 0.6, "max": 0.8}, "latex": "H_0"},
            "omega_b": {"prior": {"min": 0.02, "max": 0.025}, "latex": "\\Omega_b"},
            "omega_cdm": {"prior": {"min": 0.1, "max": 0.15}, "latex": "\\Omega_{cdm}"},
            "A_s": {"prior": {"min": 1.5e-9, "max": 2.5e-9}, "latex": "A_s"},
            "n_s": {"prior": {"min": 0.9, "max": 1.0}, "latex": "n_s"},
            "tau_reio": {"prior": {"min": 0.04, "max": 0.08}, "latex": "\\tau"},
            "theta_i_ridder": {
                "prior": {"min": 2.0, "max": 2.2},
                "latex": "\\theta_i"
            },
            "beta_ridder": {
                "prior": {"min": 0.005, "max": 0.015},
                "latex": "\\beta"
            }
        },
        "sampler": profile["sampler"],
        "output": f"chains/ridder_{profile_config}"
    }
    
    # Save config
    config_file = f"ridder_{profile_config}.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(ridder_config, f, default_flow_style=False)
    
    return config_file

def run_chain(config_file, theory_name):
    """Run MCMC chain"""
    print(f"Running {theory_name} chain with {config_file}...")
    cmd = ["python3", "-m", "cobaya", "run", config_file, "--force"]
    result = subprocess.run(cmd)
    return result.returncode == 0

def compare_chains(profile_config):
    """Compare ΛCDM and Ridder chains"""
    print("=" * 70)
    print(f"COMPARING ΛCDM vs RIDDER: {profile_config}")
    print("=" * 70)
    print()
    
    lcdm_dir = Path(f"chains/lcdm_{profile_config}")
    ridder_dir = Path(f"chains/ridder_{profile_config}")
    
    if not lcdm_dir.exists():
        print(f"❌ ΛCDM chains not found: {lcdm_dir}")
        return False
    
    if not ridder_dir.exists():
        print(f"❌ Ridder chains not found: {ridder_dir}")
        return False
    
    print("✓ Both chain directories found")
    print()
    print("Comparison metrics:")
    print("  - χ² comparison")
    print("  - Posterior distributions")
    print("  - Derived parameters (H₀, r_s, S₈)")
    print("  - Δχ² = χ²_Ridder - χ²_ΛCDM")
    print()
    print("Use GetDist or similar tool to generate comparison plots")
    print()
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Compare ΛCDM vs Ridder")
    parser.add_argument("--profile", required=True,
                       choices=["planck_core", "planck_bao", "planck_bao_sh0es", "full_core"],
                       help="Data profile to use")
    parser.add_argument("--theory", choices=["lcdm", "ridder"],
                       help="Run single theory")
    parser.add_argument("--compare", action="store_true",
                       help="Compare existing chains")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_chains(args.profile)
        return
    
    if args.theory == "lcdm":
        config_file = create_lcdm_config(args.profile, f"lcdm_{args.profile}")
        success = run_chain(config_file, "ΛCDM")
    elif args.theory == "ridder":
        config_file = create_ridder_config(args.profile, f"ridder_{args.profile}")
        success = run_chain(config_file, "Ridder")
    else:
        # Run both
        print("Running both ΛCDM and Ridder chains...")
        lcdm_config = create_lcdm_config(args.profile, f"lcdm_{args.profile}")
        ridder_config = create_ridder_config(args.profile, f"ridder_{args.profile}")
        
        success_lcdm = run_chain(lcdm_config, "ΛCDM")
        success_ridder = run_chain(ridder_config, "Ridder")
        
        if success_lcdm and success_ridder:
            compare_chains(args.profile)
        else:
            print("❌ One or both chains failed")
            sys.exit(1)

if __name__ == "__main__":
    main()

