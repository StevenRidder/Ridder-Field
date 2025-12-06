# Dark Radiation Coupling for Ridder Field

## The Physics Case

### Why This Is Required by Theory
Your Ridder field is an **axion** from string compactifications. Axions don't just have potentials—they **must** couple to gauge fields via Chern-Simons terms:

```
L ⊃ (φ/f) F_μν F̃^μν
```

Setting β=0 (no couplings) was a minimal choice. Turning on coupling to dark photons is **restoring** what should be there.

### Why This Breaks the Geometric Ceiling

**The Problem**: Current model stalls at H₀ ≈ 70 because kinetic decay (w≈1) is too fast.
- Energy density: ρ_φ ∝ a^{-6} (faster than radiation)
- The "boost" disappears quickly after peak

**The Solution**: Decay into dark radiation (w=1/3)
- Energy density: ρ_DR ∝ a^{-4} (same as radiation)
- The boost "hangs around" longer
- More integrated reduction in r_s for same peak amplitude

### The Efficiency Gain

**Current Model (Kinetic Decay)**:
- f_EDE fraction decays as (1+z)^{0.5} across window z=3500→1100
- Average efficiency: ~78%

**Radiation Decay**:
- f_EDE fraction stays FLAT across window
- Average efficiency: 100%
- **Gain factor: 1.28** (28% more r_s reduction)

**Translate to H₀**:
- Current: 67.4 → 69.8 (ΔH₀ ≈ 2.4)
- With radiation: 2.4 × 1.28 ≈ 3.1
- **New H₀ ≈ 70.5–71.0** km/s/Mpc

---

## The ΔN_eff Danger

Pure dark radiation persists into late universe as extra relativistic species.

**Planck constraint**: ΔN_eff < 0.3

**Napkin estimate for f_EDE = 8%**:
```
ρ_DR ≈ 0.08 × 1.69 ρ_γ ≈ 0.135 ρ_γ
ΔN_eff ≈ 0.135 / 0.227 ≈ 0.6  ← TOO HIGH!
```

---

## The Solution: Massive Dark Radiation

Instead of massless dark photons, couple to **massive** dark photons or a "transitional" sector:

1. **Phase 1 (z > 1100)**: Acts like radiation (w=1/3), maximizing r_s reduction
2. **Phase 2 (z < 1100)**: Becomes non-relativistic (w→0), hiding as trace dark matter

This is mathematically equivalent to NEDE's decay mechanism but using your Monodromy potential.

---

## Implementation Strategy

### Option A: Direct Dark Photon Coupling
Add to CLASS background equations:
```c
// Decay rate: Γ ∝ m_φ³ / f²
Gamma_decay = phi_mass^3 / f_axion^2;

// Transfer energy to dark radiation
drho_phi/dt = -Gamma_decay * rho_phi;
drho_DR/dt = +Gamma_decay * rho_phi;
```

### Option B: Massive Dark Radiation (Preferred)
Track a dark radiation fluid that becomes massive:
```c
// Dark radiation with mass m_DR
w_DR = p_DR / rho_DR;

// At high z (T >> m_DR): w_DR = 1/3
// At low z (T << m_DR): w_DR → 0
w_DR = (1/3) * (1 - (m_DR/T)^2)^{-1/2}  // relativistic → non-relativistic transition
```

### New Parameters

| Parameter | Symbol | Physical Meaning | Range |
|-----------|--------|------------------|-------|
| Decay rate | Γ_φ | Coupling to dark sector | 0.01 - 10 H(z_c) |
| DR mass | m_DR | Mass of dark radiation | 0.1 - 10 eV |
| Branching | f_DR | Fraction to dark radiation | 0 - 1 |

---

## CLASS Modifications Required

### 1. Add new fluid component (dark radiation)
```c
// In background.h
double rho_dr;  // dark radiation density
double p_dr;    // dark radiation pressure
double m_dr;    // dark radiation mass
```

### 2. Modify Ridder decay in background.c
```c
// Current: Field just oscillates/rolls
// New: Add decay channel to dark radiation

if (rho_ridder > 0 && Gamma_decay > 0) {
    // Transfer rate
    double transfer = Gamma_decay * rho_ridder * dt;
    
    // Update densities
    rho_ridder -= transfer;
    rho_dr += transfer;
}

// Dark radiation equation of state
if (m_dr > 0) {
    double T_dr = pow(rho_dr, 0.25);  // effective temperature
    w_dr = 1.0/3.0 * sqrt(1 - pow(m_dr/T_dr, 2));
} else {
    w_dr = 1.0/3.0;  // massless limit
}
```

### 3. Add to total density and pressure
```c
rho_tot += rho_dr;
p_tot += w_dr * rho_dr;
```

---

## Cobaya Configuration

```yaml
theory:
  classy:
    extra_args:
      # Ridder field (geometric shoulder)
      n_ridder: 3
      theta_i_ridder: 1.0
      beta_ridder: 0.0
      f_axion_ridder: 1.0e+27
      
      # NEW: Dark radiation coupling
      Gamma_decay_ridder: 1.0   # decay rate in units of H(z_c)
      m_dr_ridder: 1.0          # dark radiation mass in eV (0 = massless)
      f_dr_ridder: 1.0          # branching fraction to DR (1 = all to DR)

params:
  # Geometric amplitude
  Lambda_EDE_ridder:
    prior: {min: 0.01, max: 0.15}
    ref: 0.05
    
  # Decay parameters (can sample or fix)
  Gamma_decay_ridder:
    prior: {min: 0.1, max: 10}
    ref: 1.0
    
  m_dr_ridder:
    prior: {min: 0.1, max: 10}
    ref: 1.0
```

---

## Expected Physical Effects

| Effect | Mechanism | Observable |
|--------|-----------|------------|
| Larger H₀ | More efficient r_s reduction | H₀ → 70.5-71 |
| Same f_EDE | Peak amplitude unchanged | CMB peaks preserved |
| Lower S₈ | Extra relativistic phase | σ₈ suppressed |
| ΔN_eff safe | DR becomes massive | N_eff < 3.3 |

---

## The "Goldilocks" Decay

The goal is to find parameters where:

1. **Decay is fast enough** (Γ > H at z_c) to convert field energy to radiation during critical window
2. **DR becomes massive** (m_DR ~ few eV) before recombination to avoid ΔN_eff constraint
3. **Peak amplitude** (Lambda_EDE ~ 0.05-0.08) stays within CMB bounds

This is the physically motivated way to break the H₀ ≈ 70 ceiling.

---

## Next Steps

1. [ ] Implement dark radiation fluid in CLASS background.c
2. [ ] Add decay channel from Ridder field to DR
3. [ ] Add massive DR equation of state transition
4. [ ] Run test chain with DR coupling
5. [ ] Verify ΔN_eff stays below 0.3
6. [ ] Check if H₀ > 70 is achieved
