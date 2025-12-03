#!/usr/bin/env python3
"""
Full V(φ) reconstruction from CPL parameters.
Outputs suggested Ridder V4 priors.
"""
import numpy as np
from pathlib import Path

def get_cpl_evolution(w0, wa, Omega_DE=0.7, z_max=3000):
    """CPL evolution: w(z) = w0 + wa * z/(1+z)"""
    z = np.logspace(-3, np.log10(z_max), 500)
    a = 1.0 / (1.0 + z)
    
    # Equation of state
    w = w0 + wa * (1 - a)
    
    # DE density: ρ(a) = ρ₀ * a^(-3(1+w0+wa)) * exp(3wa(a-1))
    rho_norm = a**(-3*(1 + w0 + wa)) * np.exp(3 * wa * (a - 1))
    
    return {"z": z, "a": a, "w": w, "rho": rho_norm}

def reconstruct_V(cpl):
    """Reconstruct V(φ) from CPL w(z), ρ(z)."""
    a, w, rho = cpl["a"], cpl["w"], cpl["rho"]
    
    # V = (1-w)/2 * ρ
    V = (1 - w) / 2 * rho
    
    # Kinetic = (1+w)/2 * ρ
    kinetic = (1 + w) / 2 * rho
    
    # φ̇ = sqrt(2*kinetic), dφ/da ~ φ̇/(aH)
    # Approximate H for matter+DE universe
    Omega_m = 0.3
    H2 = Omega_m * a**(-3) + (1 - Omega_m) * rho
    phi_dot = np.sqrt(2 * np.abs(kinetic)) * np.sign(kinetic)
    dphi_da = phi_dot / (a * np.sqrt(H2) + 1e-30)
    
    # Integrate φ from a=1 (today, φ=0)
    idx_sort = np.argsort(a)
    a_s = a[idx_sort]
    dphi_s = dphi_da[idx_sort]
    
    phi = np.zeros_like(a)
    i_now = np.argmin(np.abs(a_s - 1.0))
    
    # Forward integration (future)
    for i in range(i_now + 1, len(a_s)):
        phi[idx_sort[i]] = phi[idx_sort[i-1]] + 0.5*(dphi_s[i] + dphi_s[i-1])*(a_s[i] - a_s[i-1])
    
    # Backward integration (past)
    for i in range(i_now - 1, -1, -1):
        phi[idx_sort[i]] = phi[idx_sort[i+1]] - 0.5*(dphi_s[i] + dphi_s[i+1])*(a_s[i+1] - a_s[i])
    
    return {"a": a, "z": cpl["z"], "phi": phi, "V": V, "w": w, "kinetic": kinetic}

def estimate_ridder_params(recon, cpl):
    """Estimate Ridder potential parameters."""
    a, V, phi = recon["a"], recon["V"], recon["phi"]
    
    # 1. Find EDE peak (early times, a < 0.01)
    early = a < 0.01
    if np.any(early) and np.any(V[early] > 0):
        idx = np.argmax(V[early])
        a_c = a[early][idx]
        V_peak = V[early][idx]
    else:
        a_c, V_peak = 3e-4, np.max(V)
    
    # 2. Estimate width (where V > V_peak/2)
    above = V > V_peak / 2
    if np.sum(above) > 1:
        ln_a = np.log(a[above] + 1e-30)
        sigma_lna = (ln_a.max() - ln_a.min()) / 2.355
    else:
        sigma_lna = 0.5
    
    # 3. Late-time power law: V ~ |φ|^n
    late = (a > 0.3) & (V > 0) & (np.abs(phi) > 1e-10)
    if np.sum(late) > 10:
        lp, lv = np.log(np.abs(phi[late])), np.log(V[late])
        ok = np.isfinite(lp) & np.isfinite(lv)
        if np.sum(ok) > 5:
            n = np.polyfit(lp[ok], lv[ok], 1)[0]
        else:
            n = 3.0
    else:
        n = 3.0
    n = np.clip(n, 1.5, 6.0)
    
    # 4. EDE fraction estimate
    z_peak = 1/a_c - 1
    Omega_m = 0.3
    rho_m = Omega_m * (1 + z_peak)**3
    rho_de = cpl["rho"][np.argmin(np.abs(a - a_c))]
    f_ede = rho_de / (rho_m + rho_de + 1e-30)
    lambda_ede = np.clip(f_ede * 10, 0.1, 5.0)
    
    return {
        "n_ridder": n, "log10_ac": np.log10(a_c),
        "sigma_lna": sigma_lna, "lambda_ede": lambda_ede,
        "f_ede": f_ede, "a_c": a_c
    }

def main():
    base = Path("/Users/steveridder/Git/Ridder-Field/phase3/chains")
    
    chains = {
        "tier6_phenom_shoes": {"w0": -1.008, "wa": -0.039, "desc": "Data-driven CPL"},
        "tier6_phenom_shoes_Hprior": {"w0": -1.137, "wa": -0.001, "desc": "Forced H0=73"},
    }
    
    print("="*80)
    print("V(φ) RECONSTRUCTION & RIDDER V4 PARAMETER ESTIMATION")
    print("="*80)
    
    for name, p in chains.items():
        print(f"\n{'='*40}")
        print(f"{name}")
        print(f"Description: {p['desc']}")
        print(f"w0={p['w0']:.3f}, wa={p['wa']:.3f}")
        print(f"{'='*40}")
        
        # Get CPL evolution
        cpl = get_cpl_evolution(p["w0"], p["wa"])
        
        # Reconstruct V(φ)
        recon = reconstruct_V(cpl)
        
        # Estimate parameters
        params = estimate_ridder_params(recon, cpl)
        
        print(f"\nRECOMMENDED V4 PRIORS:")
        print(f"  n_ridder:   {params['n_ridder']:.2f}  (power-law tail exponent)")
        print(f"  log10_ac:   {params['log10_ac']:.2f}  (EDE peak at z ~ {1/params['a_c']-1:.0f})")
        print(f"  sigma_lna:  {params['sigma_lna']:.2f}  (width of EDE bump)")
        print(f"  lambda_ede: {params['lambda_ede']:.2f}  (EDE amplitude)")
        print(f"  f_EDE_peak: {params['f_ede']:.4f}  (peak EDE fraction)")
        
        # Generate YAML snippet
        print(f"\nYAML snippet for V4 config:")
        print(f"""
  n_ridder:
    prior: [2.0, 5.0]
    ref: {{loc: {params['n_ridder']:.2f}, scale: 0.5}}
  
  log10_ac:
    prior: [-4.5, -2.5]
    ref: {{loc: {params['log10_ac']:.2f}, scale: 0.3}}
  
  sigma_lna:
    prior: [0.3, 1.0]
    ref: {{loc: {params['sigma_lna']:.2f}, scale: 0.1}}
  
  lambda_ede:
    prior: [0.1, 3.0]
    ref: {{loc: {params['lambda_ede']:.2f}, scale: 0.3}}
""")
        
        # Save reconstruction
        out = Path("/Users/steveridder/Git/Ridder-Field/phase3/v4_development")
        np.savez(out / f"recon_{name}.npz", **recon, **params)
        print(f"Saved reconstruction to: {out / f'recon_{name}.npz'}")

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("""
1. Use these priors in tier7_v4_optimized.yaml
2. Run MCMC: cobaya-run tier7_v4_optimized.yaml
3. Compare results:
   - Does V4 achieve similar χ² to tier6 CPL?
   - Does it give H0 ≈ 69-71 without forcing?
   - Does S8 come down to ~0.79-0.81?

Target: Δχ² ≈ 0 vs ΛCDM with natural H0 tension relief
""")

if __name__ == "__main__":
    main()
