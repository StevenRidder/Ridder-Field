# Documentation Index

This document provides a navigation guide to all documentation in the Ridder-Field repository.

---

## 📚 Papers

### Paper 1: Geometric Early Dark Energy
- **Paper**: [`phase2/paper/ridder_cosmology_paper.tex`](phase2/paper/ridder_cosmology_paper.tex)
- **Reproduction Guide**: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- **Key Results**: See [README.md](README.md#paper-1-geometric-ceiling)

### Paper 2: Damping-Tail Feature Detection
- **Paper**: [`paper2_dr6/paper2_v2_anomaly.tex`](paper2_dr6/paper2_v2_anomaly.tex)
- **Alternative Version**: [`paper2_dr6/paper2_soft_shoulder.tex`](paper2_dr6/paper2_soft_shoulder.tex)
- **Reproduction Guide**: [`paper2_dr6/REPRODUCTION.md`](paper2_dr6/REPRODUCTION.md)
- **Key Results**: See [README.md](README.md#paper-2-template-detection)

---

## 🔬 Paper 2 Documentation

### Core Documentation

1. **[REPRODUCTION.md](paper2_dr6/REPRODUCTION.md)**
   - Complete step-by-step guide to reproduce all Paper 2 results
   - Installation, configuration, and running instructions
   - Troubleshooting guide

2. **[PAPER2_PROJECT_PLAN.md](paper2_dr6/PAPER2_PROJECT_PLAN.md)**
   - Comprehensive project plan and status
   - Defense strategy against red team attacks
   - Current status of all verification tasks

3. **[CHAIN_VERIFICATION.md](paper2_dr6/CHAIN_VERIFICATION.md)**
   - Detailed verification of all MCMC chains
   - Comparison of chain results to paper claims
   - Chain locations and file names

4. **[VERIFICATION_STATUS.md](paper2_dr6/VERIFICATION_STATUS.md)**
   - Status of all verification tests
   - What has been verified vs. what needs VM verification
   - Commands to run verification tests

### Analysis Documentation

5. **[PAPER2_CHAIN_ANALYSIS.md](paper2_dr6/PAPER2_CHAIN_ANALYSIS.md)**
   - Detailed analysis of MCMC chain results
   - Parameter constraints and posteriors
   - Comparison between different configurations

6. **[BUG_REPORT.md](paper2_dr6/BUG_REPORT.md)**
   - Known issues and their resolutions
   - Parameter mismatches and fixes
   - Historical debugging notes

7. **[WALKBACK_FIXES.md](paper2_dr6/WALKBACK_FIXES.md)**
   - Fixes applied during analysis
   - Corrections to earlier results
   - Lessons learned

### Validation Plans

8. **[LAMBDA_016_VALIDATION_PLAN.md](paper2_dr6/LAMBDA_016_VALIDATION_PLAN.md)**
   - Validation plan for Λ = 0.16 profile likelihood
   - Specific tests and expected results

9. **[PIPELINE_VALIDATION_PLAN.md](paper2_dr6/PIPELINE_VALIDATION_PLAN.md)**
   - Validation of analysis pipeline
   - Reproducibility checks
   - Comparison to published results

10. **[RED_TEAM_ATTACKS.md](paper2_dr6/RED_TEAM_ATTACKS.md)**
    - Potential criticisms and responses
    - Defense strategy
    - Pre-emptive fixes

### Technical Documentation

11. **[DEBUGGING_CHECKLIST.md](paper2_dr6/DEBUGGING_CHECKLIST.md)**
    - Systematic debugging checklist
    - Common issues and solutions

12. **[MCMC_PRIORITY_LIST.md](paper2_dr6/MCMC_PRIORITY_LIST.md)**
    - Priority list of MCMC chains to run
    - Status of each chain

13. **[DARK_RADIATION_COUPLING.md](paper2_dr6/DARK_RADIATION_COUPLING.md)**
    - Documentation on dark radiation coupling
    - Analysis of α-branching effects

14. **[FINAL_DECAY_ANALYSIS.md](paper2_dr6/FINAL_DECAY_ANALYSIS.md)**
    - Analysis of decay parameters
    - Results and implications

### Data Documentation

15. **[data/DATA_DRIVEN_SUMMARY.md](paper2_dr6/data/DATA_DRIVEN_SUMMARY.md)**
    - Summary of data-driven analysis
    - Key findings from data files

---

## 📁 Repository Structure

### Main Directories

- **`paper2_dr6/`**: Paper 2 analysis and documentation
  - `configs/`: Cobaya YAML configuration files
  - `chains/`: MCMC chain outputs (on VM: `/home/azureuser/Ridder-Field/paper2_dr6/chains/`)
  - `figures/`: All paper figures
  - `data/`: Analysis data files
  - `tools/`: Analysis and plotting scripts

- **`phase2/`**: Paper 1 materials
  - `paper/`: LaTeX paper and figures
  - `class/`: Modified CLASS source code

- **`phase3/`**: Paper 1 MCMC analysis
  - `configs/`: Cobaya configurations
  - `chains/`: MCMC chains
  - `figures/`: Analysis figures

- **`AxiCLASS/`**: Reference CLASS implementation

- **`patches/`**: CLASS modification patches

- **`archive/`**: Historical documentation

---

## 🛠️ Quick Reference

### Running Analysis

**Paper 1**:
```bash
cd phase3
cobaya-run configs/tier5_baseline.yaml -f
```

**Paper 2**:
```bash
cd paper2_dr6
cobaya-run configs/prod_p2_dr6_ede.yaml -f
```

### Key Configuration Files

**Paper 2**:
- `configs/prod_p2_dr6_ede.yaml`: Main EDE result
- `configs/prod_p0b_dr6_lcdm.yaml`: ΛCDM baseline
- `configs/p2_act_only.yaml`: ACT-only analysis

**Paper 1**:
- `phase3/configs/tier5_baseline.yaml`: Production baseline
- `phase3/configs/tier5_v3_shoes.yaml`: With SH0ES prior

### Key Scripts

**Paper 2**:
- `tools/proper_pte_sims.py`: PTE simulation
- `tools/phase_scrambling_sims.py`: Phase coherence test
- `tools/generate_robustness_figure.py`: Robustness figure
- `tools/continuous_shift_dilation_test.py`: Shift/dilation test

---

## 📊 Key Results Summary

### Paper 1
- Geometric ceiling: H₀ ≈ 69-70 km/s/Mpc
- H₀ tension: 4.3σ → 2.3σ
- S₈ tension: 2.7σ → 1.1σ

### Paper 2
- Template amplitude: A_sh = 1.61 ± 0.22 (7.4σ)
- Δχ² = -474 (template vs ΛCDM)
- Δχ² = -766 (EDE at Λ=0.16 vs ΛCDM)
- PTE < 10⁻⁴
- Phase coherence: 10.5σ

---

## 🔍 Finding Specific Information

### I want to...

**Reproduce Paper 2 results**:
→ Start with [`paper2_dr6/REPRODUCTION.md`](paper2_dr6/REPRODUCTION.md)

**Understand the analysis status**:
→ Check [`paper2_dr6/PAPER2_PROJECT_PLAN.md`](paper2_dr6/PAPER2_PROJECT_PLAN.md)

**Verify chain results**:
→ See [`paper2_dr6/CHAIN_VERIFICATION.md`](paper2_dr6/CHAIN_VERIFICATION.md)

**Find known issues**:
→ Read [`paper2_dr6/BUG_REPORT.md`](paper2_dr6/BUG_REPORT.md)

**Run a specific test**:
→ Check [`paper2_dr6/VERIFICATION_STATUS.md`](paper2_dr6/VERIFICATION_STATUS.md)

**Understand the model**:
→ See [`README.md`](README.md#the-model)

**Find configuration files**:
→ Look in `paper2_dr6/configs/` or `phase3/configs/`

**Locate chains**:
→ VM: `/home/azureuser/Ridder-Field/paper2_dr6/chains/`
→ Local: `paper2_dr6/chains/`

---

## 📞 Getting Help

- **Email**: sridder@post.harvard.edu
- **GitHub Issues**: [Open an issue](https://github.com/StevenRidder/Ridder-Field/issues)
- **Documentation**: Check this index and specific documentation files

---

*Last updated: December 2025*

