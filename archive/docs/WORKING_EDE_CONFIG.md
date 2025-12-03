# Working EDE Configurations - SHOOTING NOW FUNCTIONAL

## Session: 2025-11-24

### 🎉 MAJOR MILESTONE: Shooting Converged!

```
✅ SHOOTING CONVERGED in 7 iterations!
   Final m_axion = 8.164062e+01 H0
   f_EDE = 10% at z_peak ~ 10^14
```

### Successful Shooting Configuration
```ini
ridder_model_type = unified
ridder_use_shelf = yes
ridder_use_tail = no
ridder_use_plateau = no

# Parameters that achieved f_EDE = 10%
ridder_m_axion = 81.64      # H0 units (found by shooting)
ridder_f_axion = 0.0002     # M_Pl units
ridder_f = 4.87e23          # eV (must match f_eV!)
theta_i_ridder = 2.72
ridder_n_EDE = 3.0

# Shooting parameters
ridder_use_shooting_EDE = yes
ridder_f_EDE_target = 0.10
ridder_z_c_target = 3500
ridder_shooting_m_min = 50.0
ridder_shooting_m_max = 500.0
ridder_shooting_tolerance = 0.01
```

### Key Bug Fixes This Session

1. **Bug #15 Fixed**: `phi_ini` now correctly uses unified `f_eV`
   - Old: `phi_ini = pba->f_axion_ridder * theta_i`
   - New: `phi_ini = pba->ridder_unified.f_eV * theta_i` for unified mode

2. **f_peak Calculation Bug Fixed**: Changed from `rho_crit` to `rho_tot`
   - Old: `f_ridder = rho_ridder / rho_crit` (rho_crit was wrong/constant)
   - New: `f_ridder = rho_ridder / rho_tot` (correct!)

3. **Search Range Bug Fixed**: Full redshift scan
   - Old: `z_search = [z_target/10, z_target*10]` (missed peak at z~10^14)
   - New: `z_search = [1, 10^15]` (full cosmic history)

### Parameter Relationships

```
f_eV = f_axion × M_Pl = f_axion × 2.435e27 eV
m_eV = m_axion × H0 × (1e5/c) ≈ m_axion × 8.1e-8 eV
V_scale ~ m²f² 
ridder_f MUST equal f_eV for correct θ = φ/f mapping
```

### Bracket Behavior (with f_axion = 0.0002 M_Pl)

| m_axion (H0) | f_EDE | Notes |
|--------------|-------|-------|
| 50           | 1.6%  | Too weak |
| 78           | 8.9%  | Close |
| **81.6**     | **10%** | **TARGET** |
| 106          | 25%   | Strong |
| 500          | 99%   | Too strong |

### Remaining Issue: z_peak Timing

Current configuration gives f_EDE = 10% at **z_peak ~ 10^14**, not z ~ 3500.

To shift peak to z ~ 3500:
- Need larger m_axion (shifts peak to lower z)
- But larger m increases energy → may hit "too much non-radiation"
- May need to adjust f_axion and m together

### Next Steps (Phase 1A Unblocked!)

1. ✅ Shooting works - can calibrate f_EDE automatically
2. ⏳ Tune parameters to get z_peak ~ 3500 (not just f_EDE = 10%)
3. ⏳ Add CDM coupling (beta_ridder)
4. ⏳ Run beta ladder scan
5. ⏳ Extract H0, S8, CMB metrics

### Files Changed
- `phase2/class/source/background.c`: Fixed ridder_get_f_peak, search range
- `extract_f_peak.py`: Reference Python implementation
- `axiclass_anchor_proper.ini`: Working shooting configuration
