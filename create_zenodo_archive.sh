#!/bin/bash
# Create Zenodo archive for PRD submission
# Run from Ridder-Field root directory

ARCHIVE_NAME="ridder_field_prd_v1"
ARCHIVE_DIR="release/${ARCHIVE_NAME}"

echo "Creating Zenodo archive..."

# Create release directory
mkdir -p ${ARCHIVE_DIR}/{chains,configs,figures,code}

# Copy key MCMC chains (the ones cited in paper)
echo "Copying MCMC chains..."
cp phase3/chains/tier5_*.txt ${ARCHIVE_DIR}/chains/ 2>/dev/null
cp phase3/chains/tier4_lcdm_baseline.1.txt ${ARCHIVE_DIR}/chains/ 2>/dev/null

# Copy key config files
echo "Copying config files..."
cp phase3/configs/*.yaml ${ARCHIVE_DIR}/configs/ 2>/dev/null

# Copy figures
echo "Copying figures..."
cp overleaf_final/figures/*.png ${ARCHIVE_DIR}/figures/ 2>/dev/null
cp overleaf_final/figures/*.pdf ${ARCHIVE_DIR}/figures/ 2>/dev/null

# Copy key code
echo "Copying code..."
cp phase3/*.py ${ARCHIVE_DIR}/code/ 2>/dev/null
cp setup.py ${ARCHIVE_DIR}/ 2>/dev/null
cp requirements.txt ${ARCHIVE_DIR}/ 2>/dev/null

# Copy paper
cp overleaf_final/main.tex ${ARCHIVE_DIR}/paper.tex

# Copy documentation
cp README.md ${ARCHIVE_DIR}/
cp REPRODUCIBILITY.md ${ARCHIVE_DIR}/
cp LICENSE ${ARCHIVE_DIR}/

# Create archive README
cat > ${ARCHIVE_DIR}/ZENODO_README.md << 'EOF'
# Ridder Field: Geometric EDE Analysis

## Paper
"Early Dark Energy and the Geometric Ceiling: Constraints from Planck, ACT DR6, and DESI Y1"

## Contents

- `chains/` - MCMC chains from Cobaya (Tier 4-5 production runs)
- `configs/` - Cobaya YAML configuration files
- `figures/` - All figures from the paper
- `code/` - Analysis scripts (Python)
- `paper.tex` - LaTeX source

## Key Chains

| File | Description |
|------|-------------|
| `tier5_ede_shoes_predesi` | EDE + SH0ES, pre-DESI BAO |
| `tier5_ede_shoes_desi` | EDE + SH0ES + DESI Y1 |
| `tier5_ede_trgb_*` | EDE + TRGB prior |
| `tier5_lcdm_*` | ΛCDM baselines |
| `tier5_ede_shoes_desi_h0_fixed_*` | Fixed-H₀ profile scans |
| `tier5_ede_des_y1` | EDE + DES Y1 weak lensing |

## Requirements

- Python 3.9+
- CLASS (Boltzmann solver, with EDE modifications)
- Cobaya 3.3+
- See `requirements.txt`

## Citation

If you use these data, please cite:
Ridder, S. (2025). Physical Review D.

## License

MIT License
EOF

# Create the zip
echo "Creating ZIP archive..."
cd release
zip -r ${ARCHIVE_NAME}.zip ${ARCHIVE_NAME}/
cd ..

# Report
echo ""
echo "=== Archive Created ==="
du -sh release/${ARCHIVE_NAME}.zip
echo ""
echo "Files included:"
find release/${ARCHIVE_NAME} -type f | wc -l
echo ""
echo "Ready for upload to Zenodo!"

