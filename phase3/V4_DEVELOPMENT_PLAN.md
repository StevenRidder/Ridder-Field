# V4 Development Plan: Data-First, Theory-Second

## Status
- [x] V3 frozen with tag
- [x] CI infrastructure in place
- [x] Tier 6 phenom configs created
- [x] Reconstruction script created
- [ ] Run Tier 6 phenom chains
- [ ] Analyze what w(z) the data want
- [ ] Reconstruct V(φ) from best-fit
- [ ] Fit simple template to V(φ)
- [ ] Implement V4 in CLASS
- [ ] Run Tier 7 V4 chains

## Directory Structure
```
phase3/
├── tier6_phenom/
│   ├── tier6_phenom_baseline.yaml  # CPL DE, no H0 prior
│   └── tier6_phenom_shoes.yaml     # CPL DE + SH0ES
├── v4_development/
│   ├── reconstruct_V_from_phenom.py
│   └── (future: fit_template.py, V4 implementation)
├── tests/
│   ├── golden_lcdm_baseline.json
│   └── check_lcdm_golden.py
└── run_tests.sh
```

## The Plan

### Step 1: Run Tier 6 Phenomenological Chains
Let w(z) = w0 + wa*z/(1+z) float freely with Planck+BAO(+SH0ES).
Ask: what expansion history does the data actually want?

### Step 2: Reconstruct V(φ)
From best-fit w0, wa → reconstruct numerical V(φ) curve.
This is the "data-preferred potential shape."

### Step 3: Fit Simple Template
Find minimal analytic V(φ) that matches the reconstruction.
Candidates:
- Sum of exponentials
- Broken power law
- Two-regime (EDE bump + late plateau)

### Step 4: Implement V4
Add new potential to CLASS, run Tier 7 chains.
Compare to LCDM and V3.

## Key Principle
Never guess the potential first. Let the data tell you the history,
then invert to find the field theory that produces it.
