# Ridder-Field Repository Cleanup Audit

**Date**: November 2025  
**Current Branch**: `v3-development`  
**Goal**: Make repo public-ready, clean, and dead-simple to use

---

## 🔴 CRITICAL ISSUES

### 1. **Root Directory is a Disaster Zone**

**Problem**: 129 markdown files + 78 Python scripts + 40 INI files at root level

```
Current root level:
├── 129 *.md files (session notes, status reports, bug reports)
├── 78 *.py files (scattered scripts)
├── 40 *.ini files (old test configs)
├── Multiple V1/V2/V3 status files
├── Debugging artifacts everywhere
```

**Impact**: A new user sees chaos, not a usable project.

**Fix**:
```
archive/
├── session_notes/     # All those status MDs
├── legacy_configs/    # Old .ini files
├── v1_v2_development/ # Old development artifacts
```

### 2. **No Clear Entry Point**

**Problem**: README.md is 930 lines of theory + speculation + sci-fi. No quick "pip install && run" path.

**Impact**: Scientists want to run MCMC chains, not read about Ridder corridors.

**Fix**: Split README into:
- `README.md` - 50 lines: what it is, how to install, how to run
- `docs/THEORY.md` - Full mathematical theory
- `docs/SCIENCE_FICTION.md` - Speculative applications

### 3. **Multiple CLASS/AxiCLASS Copies (2GB+)**

**Problem**: 
```
AxiCLASS/           383 MB
phase2/class/       ~500 MB
phase2_v2/class/    ~500 MB
Recovered_CLASSY/   ~100 MB
```

**Impact**: Massive repo size, confusing which version to use.

**Fix**:
- Keep ONE canonical `class/` directory with Ridder modifications
- Move others to `.gitignore` or delete
- Document which CLASS version is canonical

### 4. **No requirements.txt / setup.py for Phase 3**

**Problem**: `requirements.txt` at root is minimal. No instructions for Cobaya/CLASS setup.

**Impact**: Users can't reproduce your MCMC results.

**Fix**: Create `phase3/requirements.txt` with:
```
cobaya>=3.3
numpy>=1.21
scipy>=1.7
matplotlib>=3.5
getdist>=1.3
mpi4py>=3.1
```

---

## 🟡 MEDIUM ISSUES

### 5. **Branch Structure is Messy**

**Current**:
```
main              # Outdated, needs merge
v2-development    # Legacy
v3-development    # Current work (you're here)
```

**Problem**: Main is ~300+ commits behind v3-development

**Fix Before Going Public**:
1. Merge `v3-development` → `main`
2. Delete `v2-development` branch
3. Tag release: `v1.0.0-paper-submission`

### 6. **Paper Assets Mixed with Code**

**Problem**: 
```
phase2/paper/           # Paper tex, figures, overleaf zips
figures/                # Old figures at root
plots/                  # More plots at root  
track2_plots/          # Even more plots
```

**Impact**: Where do I find the paper?

**Fix**:
```
paper/
├── ridder_cosmology_paper.tex
├── figures/
└── submission/
```

### 7. **No .gitattributes for Large Files**

**Problem**: Binary files (`.npz`, `.png`, `.dat`) bloat repo history

**Fix**: Add `.gitattributes`:
```
*.npz filter=lfs diff=lfs merge=lfs -text
*.dat filter=lfs diff=lfs merge=lfs -text
```

Or exclude them entirely and host elsewhere.

### 8. **Sensitive Azure Info**

**Problem**: `azure/` directory might contain subscription IDs (gitignored but mentioned in files)

**Fix**: Audit `azure/README.md` for any sensitive data before making public.

---

## 🟢 GOOD THINGS (Keep These)

✅ **`.gitignore` is solid** - Good coverage of build artifacts, chains, sensitive data

✅ **`phase3/configs/` is organized** - YAML configs are named well

✅ **Paper figures are generated** - `paper_*.png` files exist and look professional

✅ **Core CLASS modifications exist** - `patches/` directory has the key diffs

---

## 📋 CLEANUP CHECKLIST

### Phase A: Archive & Organize (Before Merge)

- [ ] Create `archive/session_notes/` and move all root-level status MDs
- [ ] Create `archive/legacy_configs/` and move all root-level `.ini` files
- [ ] Create `archive/v1_v2_scripts/` and move old Python scripts
- [ ] Delete duplicate CLASS installations (keep one canonical)
- [ ] Consolidate `figures/`, `plots/`, `track2_plots/` into one location

### Phase B: Documentation (Before Merge)

- [ ] **Rewrite README.md** to be <100 lines:
  ```markdown
  # Ridder Field: Geometric EDE for Cosmology
  
  ## Quick Start
  pip install -r requirements.txt
  cd phase3
  cobaya-run configs/tier5_ede_shoes_predesi.yaml
  
  ## What This Is
  [2 paragraphs]
  
  ## Paper
  See `paper/ridder_cosmology_paper.tex`
  
  ## Full Documentation
  See `docs/`
  ```

- [ ] Create `docs/INSTALLATION.md` with full CLASS+Cobaya setup
- [ ] Create `docs/RUNNING_CHAINS.md` with MCMC instructions
- [ ] Move theory content to `docs/THEORY.md`
- [ ] Move sci-fi content to `docs/SPECULATIVE.md` (or delete)

### Phase C: Reorganize Structure

**Target structure for public repo:**
```
Ridder-Field/
├── README.md                 # <100 lines, quick start
├── LICENSE
├── requirements.txt          # Python deps
├── setup.py                  # Optional: pip installable
│
├── class/                    # Single canonical CLASS with Ridder mods
│   ├── source/
│   ├── python/
│   └── README.md             # "How to build"
│
├── configs/                  # All MCMC configs
│   ├── tier5/
│   ├── phase2_act/
│   └── README.md             # "Which config does what"
│
├── paper/                    # Publication materials
│   ├── ridder_cosmology_paper.tex
│   ├── figures/
│   └── PRE_PUBLICATION_CHECKLIST.md
│
├── docs/                     # Full documentation
│   ├── INSTALLATION.md
│   ├── RUNNING_CHAINS.md
│   ├── THEORY.md
│   └── RESULTS.md
│
├── scripts/                  # Utility scripts
│   ├── status_monitors/
│   ├── diagnostics/
│   └── plotting/
│
├── results/                  # Published results (CSVs, JSONs)
│   ├── tier10_publication_results.json
│   └── cross_world_summary.csv
│
└── archive/                  # Historical development (optional)
    ├── session_notes/
    ├── legacy_configs/
    └── v1_v2_development/
```

### Phase D: Merge to Main

- [ ] Create PR from `v3-development` to `main`
- [ ] Squash or keep commits (your choice)
- [ ] Tag release: `v1.0.0`
- [ ] Delete old branches
- [ ] Update repo description on GitHub

### Phase E: Final Polish

- [ ] Add `CONTRIBUTING.md`
- [ ] Add `CITATION.cff` for proper academic citation
- [ ] Test fresh clone + install + run on clean machine
- [ ] Write GitHub Actions CI (optional but nice)

---

## 🎯 "DEAD SIMPLE" USER EXPERIENCE

After cleanup, a new user should be able to:

```bash
# Clone
git clone https://github.com/yourusername/Ridder-Field.git
cd Ridder-Field

# Install (5 minutes)
pip install -r requirements.txt
cd class && make && cd ..

# Run a chain (instant start)
cd configs
cobaya-run tier5_ede_shoes_predesi.yaml

# Read the paper
open paper/ridder_cosmology_paper.pdf
```

**That's it. No hunting through 129 markdown files.**

---

## 📊 SIZE REDUCTION ESTIMATE

| Component | Current | After Cleanup |
|-----------|---------|---------------|
| Root MD files | 129 | 5 (README, LICENSE, CHANGELOG, CONTRIBUTING, CITATION) |
| Root PY files | 78 | 0 (moved to scripts/) |
| Root INI files | 40 | 0 (moved to archive/) |
| CLASS copies | 4 (~2GB) | 1 (~400MB) |
| **Total repo** | **3.1 GB** | **~500 MB** |

---

## ⏱️ TIME ESTIMATE

| Task | Time |
|------|------|
| Archive root files | 30 min |
| Rewrite README | 1 hour |
| Reorganize structure | 2 hours |
| Test fresh install | 1 hour |
| Merge + tag | 30 min |
| **Total** | **~5 hours** |

---

## 🚫 DO NOT TOUCH YET

This is an audit only. Before any changes:
1. Finish paper submission preparation
2. Complete chain convergence
3. Back up current state

**Cleanup should happen AFTER the paper is on arXiv, not before.**

---

*Audit complete. No files were modified.*
