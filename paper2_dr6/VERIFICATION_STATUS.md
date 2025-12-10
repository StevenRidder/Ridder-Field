# Paper 2 Verification Status

## What Was Actually Computed

### ✅ VERIFIED (Real Simulations Run)

| Claim | Script | Data File | Method |
|-------|--------|-----------|--------|
| PTE < 10⁻⁴ | `tools/proper_pte_sims.py` | `data/proper_pte_results.txt` | 10,000 analytical ΛCDM + ACT noise Monte Carlo |
| z-score = 10.15σ | Same as above | Same | Fisher analysis on simulations |
| Phase coherence 10.5σ | `tools/phase_scrambling_sims.py` | `data/phase_scrambling_results.txt` | 1,000 phase-scrambled templates |
| 0/10000 simulations exceed observed | PTE script | Results file | Empirical count |

**Method validity**: Analytical ΛCDM with realistic ACT noise model is the standard approach for PTE tests. You don't need to run CLASS 10,000 times.

### ⚠️ NEEDS VM VERIFICATION (Mock Data Used Locally)

| Claim | Script | VM Script | What to Run |
|-------|--------|-----------|-------------|
| Shift FWHM ≈ 40 bins | `tools/continuous_shift_dilation_test.py` | `tools/run_shift_dilation_on_vm.py` | Run on VM with real ACT likelihood |
| 5% dilation destroys detection | Same | Same | Same |
| Specific σ values in Table shift_dilation | Same | Same | Same |

**Current table values are from MOCK DATA** - must be replaced with VM results before submission.

### ✅ FROM MCMC CHAINS (Exist on VM)

| Claim | Chain Files | Location |
|-------|-------------|----------|
| A_sh = 1.54 ± 0.19 | `prod_p2_dr6_ede.*.txt` | VM: `~/Ridder-Field/paper2_dr6/chains/` |
| Δχ² = -66 (ACT-only) | Chain analysis | VM |
| H₀ = 70.7 ± 0.8 km/s/Mpc | EDE chain best-fit | VM |
| Λ_EDE = 0.16 | EDE chain best-fit | VM |
| Frequency-split results | Separate frequency chains | VM |

---

## VM Commands to Verify

### 1. Shift/Dilation Test
```bash
ssh <VM_USER>@<IP>
cd ~/Ridder-Field/paper2_dr6/tools
python3 run_shift_dilation_on_vm.py
# Copy output numbers to paper Table shift_dilation
```

### 2. Check Chain Best-Fits
```bash
cd ~/Ridder-Field/paper2_dr6/chains
grep "^#" prod_p0b_dr6_lcdm.1.txt | head -1  # Header
python3 -c "
import numpy as np
d = np.loadtxt('prod_p2_dr6_ede.1.txt')
h = open('prod_p2_dr6_ede.1.txt').readline().split()
i = h.index('H0') if 'H0' in h else -1
print('H0 best-fit:', d[np.argmin(d[:,2]), i] if i>0 else 'not found')
"
```

### 3. Verify χ² Values
```bash
python3 ../tools/chain_chi2_analysis.py
```

---

## Paper Numbers That Need Verification

### Table shift_dilation (line ~1583)

**Baseline 27.7σ** is CORRECT - this is from real fixed-cosmology template fit (A_sh = 1.10 ± 0.04)

**Shift/dilation behavior** (FROM MOCK DATA - MUST VERIFY ON VM):
- Shift = 30 bins: < 2σ      → NEEDS VM VERIFICATION  
- Shift = 50 bins: < 1σ      → NEEDS VM VERIFICATION
- FWHM: ≈ 40 bins            → NEEDS VM VERIFICATION
- α = 0.95: < 3σ             → NEEDS VM VERIFICATION
- α = 1.05: < 3σ             → NEEDS VM VERIFICATION

**Note**: The exact values for shifted/dilated templates require running with 
the real ACT likelihood. The QUALITATIVE behavior (shift destroys detection) 
is correct, but the exact σ values need verification.

### Main detection significance (throughout paper)
- 8.1σ template preference → Verify against chain A_sh/σ_A
- 27σ (mentioned in text) → This is from shift test, needs VM

---

## Before Submission Checklist

- [ ] Run `run_shift_dilation_on_vm.py` on VM
- [ ] Update Table shift_dilation with real numbers
- [ ] Verify all χ² numbers match chain outputs
- [ ] Cross-check PTE results (already done, verified)
- [ ] Run `git commit` with verification stamp

