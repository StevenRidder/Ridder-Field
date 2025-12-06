#!/usr/bin/env python3
"""
Chain Status Report - Paper 2 Production Runs (DR6)
Run with: python3 ~/Ridder-Field/phase4/scripts/chain_status.py
"""

import numpy as np
import os
import glob

CHAIN_DIR = "/home/azureuser/Ridder-Field/phase4/chains"

# Chain definitions - DR6 ONLY (Paper 2 production)
CHAINS = {
    "P0b_DR6": {"prefix": "prod_p0b_dr6",  "desc": "LCDM + ACT DR6",        "model": "LCDM"},
    "P2_DR6":  {"prefix": "prod_p2_dr6",   "desc": "EDE + ACT DR6",         "model": "EDE"},
    "P3_DR6":  {"prefix": "prod_p3_dr6",   "desc": "Template + ACT DR6",    "model": "LCDM+A_sh"},
}


def get_chain_data(prefix):
    """Load chain data and return statistics."""
    files = glob.glob(f"{CHAIN_DIR}/{prefix}.*.txt")
    files = [f for f in files if "input" not in f and "updated" not in f and "progress" not in f]
    
    # Check log for status
    log = f"{CHAIN_DIR}/{prefix}.log"
    stage = "waiting"
    burnin_left = 0
    if os.path.exists(log):
        with open(log) as lf:
            lines = lf.readlines()[-10:]
            for l in lines:
                if "burning" in l:
                    stage = "burn-in"
                    try:
                        burnin_left = int(l.split("accepted steps left")[0].split()[-1])
                    except:
                        pass
                elif "Sampling!" in l or ("Progress" in l and "burning" not in l):
                    stage = "sampling"
    
    if not files:
        return {"n": 0, "stage": stage, "burnin_left": burnin_left}
    
    try:
        all_d = []
        for f in files:
            if os.path.getsize(f) > 100:
                d = np.loadtxt(f)
                if d.ndim == 1:
                    d = d.reshape(1, -1)
                all_d.append(d)
        
        if not all_d:
            return {"n": 0, "stage": stage, "burnin_left": burnin_left}
        
        data = np.vstack(all_d)
        n = len(data)
        
        # Read header
        with open(files[0]) as hf:
            hdr = hf.readline().strip()
        cols = [c for c in hdr.split() if c and c != "#"]
        
        def get_col(name):
            if name in cols:
                idx = cols.index(name)
                if idx < data.shape[1]:
                    return idx
            return None
        
        result = {"n": n, "stage": "done" if n > 50 else stage, "burnin_left": burnin_left}
        
        h0_idx = get_col("H0")
        s8_idx = get_col("S8")
        logl_idx = get_col("minuslogpost")
        ash_idx = get_col("A_sh")
        
        if h0_idx is not None:
            result["H0"] = np.mean(data[:, h0_idx])
            result["H0_std"] = np.std(data[:, h0_idx])
        if s8_idx is not None:
            result["S8"] = np.mean(data[:, s8_idx])
            result["S8_std"] = np.std(data[:, s8_idx])
        if logl_idx is not None:
            result["chi2"] = 2 * np.min(data[:, logl_idx])
        if ash_idx is not None:
            result["A_sh"] = np.mean(data[:, ash_idx])
            result["A_sh_std"] = np.std(data[:, ash_idx])
        
        return result
    except Exception as e:
        return {"n": 0, "stage": "error", "error": str(e)}


def main():
    print("\n" + "=" * 60)
    print("PAPER 2 PRODUCTION RUN STATUS (DR6)")
    print("=" * 60)
    
    # Collect results
    results = {}
    for name, info in CHAINS.items():
        results[name] = get_chain_data(info["prefix"])
    
    # Main table
    print("\nRun\t\tSamples\t\tH₀\t\tS₈\t\tχ²\t\tA_sh")
    print("-" * 80)
    
    for name in ["P0b_DR6", "P2_DR6", "P3_DR6"]:
        r = results[name]
        
        if r["n"] > 0:
            n_str = "{:,}".format(r["n"])
        elif r["stage"] == "burn-in":
            n_str = "burn({})".format(r.get('burnin_left', '?'))
        else:
            n_str = r["stage"]
        
        h0 = "{:.2f}".format(r['H0']) if "H0" in r else "—"
        s8 = "{:.3f}".format(r['S8']) if "S8" in r else "—"
        chi2 = "{:.0f}".format(r['chi2']) if "chi2" in r else "—"
        
        if "A_sh" in r:
            ash = "{:.2f} ± {:.2f}".format(r['A_sh'], r.get('A_sh_std', 0))
        else:
            ash = "—"
        
        print("{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}".format(name, n_str, h0, s8, chi2, ash))
    
    # Fair Comparisons
    print("\n" + "=" * 60)
    print("Fair Comparisons (all use ACT DR6)")
    print("=" * 60)
    print("Compare\t\t\t\tΔχ²\t\tΔH₀\t\tΔS₈")
    print("-" * 60)
    
    comparisons = [
        ("P0b_DR6", "P2_DR6", "LCDM vs EDE"),
        ("P0b_DR6", "P3_DR6", "LCDM vs Template"),
    ]
    
    for a, b, desc in comparisons:
        ra, rb = results[a], results[b]
        
        if "chi2" in ra and "chi2" in rb:
            dchi2 = "{:+.0f}".format(rb["chi2"] - ra["chi2"])
        else:
            dchi2 = "pending"
        
        if "H0" in ra and "H0" in rb:
            dh0 = "{:+.2f}".format(rb["H0"] - ra["H0"])
        else:
            dh0 = "pending"
        
        if "S8" in ra and "S8" in rb:
            ds8 = "{:+.3f}".format(rb["S8"] - ra["S8"])
        else:
            ds8 = "pending"
        
        print("{} vs {}\t\t{}\t\t{}\t\t{}".format(a, b, dchi2, dh0, ds8))
    
    # P3 Template Test highlight
    print("\n" + "=" * 60)
    print("🔥 P3_DR6 Template Test (marginalized A_sh)")
    print("=" * 60)
    
    r3 = results["P3_DR6"]
    if "A_sh" in r3:
        ash = r3["A_sh"]
        ash_std = r3.get("A_sh_std", 0.01)
        sigma = ash / ash_std if ash_std > 0 else 0
        print("A_sh = {:.2f} ± {:.2f}  —  {:.1f}σ from zero".format(ash, ash_std, sigma))
        
        if "chi2" in results["P0b_DR6"] and "chi2" in r3:
            dchi2 = r3["chi2"] - results["P0b_DR6"]["chi2"]
            if dchi2 > 0:
                print("Δχ² = {:+.0f}  —  Template costs χ², doesn't help".format(dchi2))
            else:
                print("Δχ² = {:+.0f}  —  Template HELPS fit! 🎉".format(dchi2))
        
        if "H0" in r3:
            print("H₀ = {:.2f} (vs Paper 1 conditional: 13.7σ)".format(r3["H0"]))
    elif r3["stage"] == "burn-in":
        print("Still in burn-in ({} steps left)".format(r3.get('burnin_left', '?')))
    else:
        print("Waiting for samples...")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
