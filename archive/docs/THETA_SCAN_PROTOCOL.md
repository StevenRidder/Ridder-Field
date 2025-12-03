# Theta Scan Protocol - Mapping the (θ_i, z_peak) Space

**Date:** November 24, 2025  
**Status:** Ready to execute  
**Goal:** Map how peak redshift shifts with initial displacement for fixed f_EDE target

---

## Physics Question

**For fixed f_EDE = 10%**, how does the peak redshift z_peak depend on initial displacement θ_i?

**Why this matters:**
- EDE models targeting H0 tension need z_peak ~ 3000-5000
- Current baseline (θ_i = 1.5) gives z_peak ~ 500 (too late!)
- Need to find θ_i that places peak at desired redshift

---

## Experimental Design

### Fixed Parameters (Baseline)
```ini
# Cosmology
H0 = 70.0
omega_b = 0.0224
omega_cdm = 0.120
A_s = 2.1e-9
n_s = 0.965
tau_reio = 0.054
YHe = 0.245
gauge = newtonian

# Ridder field (fixed)
f_axion_ridder = 2.435e27      # M_Pl scale
beta_ridder = 0.0              # No DM coupling
n_ridder = 3                   # Cosine-monodromy power

# Shooting (fixed)
use_ridder_shooting = 1
ridder_fEDE_target = 0.10      # Target 10% EDE
ridder_zc_min = 500.0
ridder_zc_max = 10000.0
ridder_shoot_log10Lambda_min = 10.0
ridder_shoot_log10Lambda_max = 16.0
ridder_shoot_tol_f = 0.001
ridder_c_slow = 1.0

# Output (minimal for speed)
output = 
write background = yes         # Enable to save rho(a) for plotting
root = output/theta_scan_
```

### Variable Parameter (Scan)
```
theta_i_ridder = [1.0, 1.2, 1.5, 1.8, 2.0, 2.2, 2.5]
```

**Rationale for range:**
- θ = 0: Field at minimum (no dynamics)
- θ = π ≈ 3.14: Field at hilltop (unstable, V'' < 0)
- θ ∈ [1.0, 2.5]: Covers "rolling down from midpoint" regime

---

## Data Collection

For each θ_i, record:

| θ_i | Lambda (eV) | log10(Lambda) | f_peak | z_peak | Notes |
|-----|-------------|---------------|--------|--------|-------|
| 1.0 |             |               |        |        |       |
| 1.2 |             |               |        |        |       |
| 1.5 | 4.85e13     | 13.686        | 0.098  | 500    | Baseline |
| 1.8 |             |               |        |        |       |
| 2.0 |             |               |        |        |       |
| 2.2 |             |               |        |        |       |
| 2.5 |             |               |        |        |       |

**How to extract:**
- Lambda: From shooter convergence trace (`RIDDER_SHOOT iter=N`)
- f_peak, z_peak: From same trace
- If shooting fails → note "no bracket" or "did not converge"

---

## Expected Behavior

### Hypothesis 1: Larger θ_i → Earlier z_peak
**Physical reasoning:**
- Larger θ_i → steeper initial gradient dV/dφ
- Steeper gradient → faster rolling
- Faster rolling → field reaches peak energy density earlier
- Earlier peak → higher z_peak

**Test:** Plot z_peak vs. θ_i, expect positive slope

---

### Hypothesis 2: Lambda scales with θ_i for fixed f_EDE
**Physical reasoning:**
- Larger θ_i → more potential energy available
- To hit same f_EDE target, need lower Lambda
- **Prediction:** Lambda decreases with θ_i

**Test:** Plot Lambda vs. θ_i, expect negative slope

---

## Execution Steps

### Step 1: Create scan script
```bash
#!/bin/bash
# theta_scan.sh - Run theta scan on VM

THETA_VALUES=(1.0 1.2 1.5 1.8 2.0 2.2 2.5)
BASE_INI="theta_scan_base.ini"  # Contains fixed params above

for THETA in "${THETA_VALUES[@]}"; do
    echo "Running theta_i = $THETA..."
    
    # Create .ini for this theta
    cp $BASE_INI theta_scan_${THETA}.ini
    echo "theta_i_ridder = $THETA" >> theta_scan_${THETA}.ini
    
    # Run CLASS
    ssh <VM_USER>@172.174.34.125 \
        "cd ~/Ridder-Field/phase2/class && \
         timeout 120 ./class ~/Ridder-Field/theta_scan_${THETA}.ini \
         2>&1 | grep -E 'RIDDER_SHOOT|converged|warning' \
         > ~/Ridder-Field/output/theta_${THETA}.log"
    
    echo "  Done. Results in output/theta_${THETA}.log"
done

echo "Scan complete! Parse logs to fill data table."
```

### Step 2: Parse results
```python
import re
import glob

results = []
for logfile in sorted(glob.glob('output/theta_*.log')):
    theta = float(re.search(r'theta_(\d+\.\d+)\.log', logfile).group(1))
    
    with open(logfile) as f:
        for line in f:
            if 'RIDDER_SHOOT iter=' in line:
                match = re.search(r'log10_Lambda=(\S+)\s+f_peak=(\S+)\s+z_peak=(\S+)', line)
                if match:
                    log10_Lambda = float(match.group(1))
                    f_peak = float(match.group(2))
                    z_peak = float(match.group(3))
    
    results.append((theta, 10**log10_Lambda, f_peak, z_peak))

# Print table
print("theta_i | Lambda (eV) | f_peak | z_peak")
print("--------|-------------|--------|-------")
for theta, Lambda, f, z in results:
    print(f"{theta:6.2f} | {Lambda:11.3e} | {f:6.4f} | {z:6.0f}")
```

### Step 3: Plot
```python
import matplotlib.pyplot as plt

theta_vals = [r[0] for r in results]
z_peaks = [r[3] for r in results]
Lambdas = [r[1] for r in results]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: z_peak vs theta_i
ax1.plot(theta_vals, z_peaks, 'o-', markersize=8)
ax1.axhline(3000, color='red', linestyle='--', alpha=0.5, label='Target z~3000')
ax1.set_xlabel('Initial displacement θ_i [rad]')
ax1.set_ylabel('Peak redshift z_peak')
ax1.set_title('EDE Peak Redshift vs. Initial Displacement')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: Lambda vs theta_i
ax2.semilogy(theta_vals, Lambdas, 's-', markersize=8, color='orange')
ax2.set_xlabel('Initial displacement θ_i [rad]')
ax2.set_ylabel('Potential scale Λ [eV]')
ax2.set_title('Lambda Required for f_EDE = 10%')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('theta_scan_results.pdf')
plt.show()
```

---

## Decision Criteria

After completing scan:

### If z_peak increases with θ_i (as expected):
**Action:** Identify θ_i that gives z_peak ~ 3000-5000

**Example:** If θ = 2.2 → z_peak ~ 3500, use that as your baseline

### If z_peak is insensitive to θ_i:
**Possible causes:**
1. Peak is hitting search boundary (z_min or z_max)
2. f dominates dynamics more than θ_i
3. Slow-roll c_slow needs tuning

**Action:** 
- Widen z_min/z_max window
- Repeat scan with different f values
- Adjust c_slow and rescan

### If no convergence for some θ_i:
**Likely causes:**
- θ too small → insufficient energy → f_EDE always below target
- θ too large → near hilltop → V'' < 0 → numerical issues

**Action:** Note "out of range" and exclude from fits

---

## Next Steps After Scan

### Once you have a good (θ_i, f_EDE) → z_peak mapping:

1. **Pick one "fiducial" EDE model:**
   - θ_i = [value that gives z_peak ~ 3000]
   - f_EDE_target = 0.10
   - Lambda = [whatever shooter finds]

2. **Freeze those parameters**, move to CMB:
   - Compute C_ℓ^TT, C_ℓ^TE, C_ℓ^EE
   - Compare to Planck
   - Check H0, r_s, A_s

3. **If CMB looks good**, start MCMC:
   - Sample over (ω_b, ω_cdm, θ_i, f_EDE_target)
   - Let shooter auto-tune Lambda at each step
   - Measure H0 posterior, compare to SH0ES

---

## Troubleshooting

### Shooter fails to converge
**Error:** "target fEDE not bracketed"
- **Fix:** Widen log10_Lambda_min/max (e.g., [8, 18])
- **Or:** Lower f_EDE_target (try 0.05)

### z_peak always at z_min = 500
**Cause:** Field rolling too late
- **Fix:** Increase θ_i (steeper start)
- **Or:** Increase c_slow (earlier onset)
- **Or:** Decrease f (higher m_eff)

### z_peak always at z_max = 10000
**Cause:** Field rolling too early
- **Fix:** Decrease θ_i
- **Or:** Increase f (lower m_eff)

### Lambda > 10¹⁶ eV (upper bracket)
**Cause:** Target f_EDE too high for this potential
- **Fix:** Lower f_EDE_target
- **Or:** Widen bracket to [10, 20]

---

## File Outputs

For each theta value, save:
```
output/theta_1.0.log         # Shooter convergence trace
output/theta_1.0_background.dat  # rho(a) tables (if write_background=yes)
```

Final deliverables:
```
theta_scan_results.pdf       # Plots
theta_scan_data.csv          # Table for paper
theta_scan_fiducial.ini      # Best-fit parameters for CMB
```

---

## Timeline

- **Scan execution:** ~30 minutes (7 points × 2-5 min each)
- **Parsing & plotting:** ~15 minutes
- **Analysis & decision:** ~30 minutes

**Total:** ~1-2 hours from start to "fiducial EDE model identified"

---

## Success Criterion

✅ **Complete** when you can fill in this sentence:

> "For f_EDE = 10%, setting θ_i = [VALUE] gives z_peak ~ [VALUE] and requires Lambda ~ [VALUE] eV. This configuration is now our baseline EDE model for CMB analysis."

---

**Status:** Protocol ready. Execute when validation is complete!  
**Next milestone:** CMB spectra with fiducial model → H0 measurement

