# Working EDE Configurations Found

## Session: 2025-11-24

### Configuration 1: Small but Working
```ini
ridder_m_axion = 7.0      # H0 units
ridder_f_axion = 0.025    # M_Pl units
ridder_f = 6.0875e25      # eV (must match f_eV!)
theta_i_ridder = 2.72
ridder_n_EDE = 3.0
```
**Results:**
- V_scale = 1.0e39 eV^4
- Initial f_ridder ~ 2%
- Peak f_ridder ~ 5.8% at z ~ 10^13
- Background completes successfully
- Age = 13.81 Gyr (ΛCDM-like)

### Configuration 2: Ultra-small
```ini
ridder_m_axion = 100.0    # H0 units
ridder_f_axion = 0.0001   # M_Pl units
ridder_f = 2.435e23       # eV (must match f_eV!)
theta_i_ridder = 2.72
ridder_n_EDE = 3.0
```
**Results:**
- V_scale = 3.3e36 eV^4
- Initial f_ridder ~ 6.8e-5
- Peak f_ridder ~ 4.3% at z ~ 7.9e13
- Background completes successfully

## Key Insights

### Unit Consistency Critical
- `ridder_f` MUST equal `f_axion * M_Pl` in eV
- Bug #15: phi_ini = f_eV * theta_i (now fixed)

### Energy Scale
- V_scale ~ m²f² must be small enough to avoid "too much non-radiation"
- Current working range: V_scale ~ 10^36 - 10^39 eV^4

### Timing Issue
- Peak at z ~ 10^13 instead of z ~ 3000-5000
- Need larger m to shift peak to lower z
- But larger m increases energy → hits "too much non-radiation"

## Shooting Bug
- `ridder_get_f_peak` returns garbage values (10^52)
- Actual values in background file are correct (~0.04)
- Need to debug the peak-finding function

## Next Steps
1. Fix shooting bug in ridder_get_f_peak
2. Find m, f combination that gives:
   - f_peak ~ 10% at z ~ 3000-5000
   - Passes "Omega_nonr < 0.1" check
3. Enable CDM coupling
4. Run Phase 1A beta ladder

