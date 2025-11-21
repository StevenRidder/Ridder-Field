# Ridder Field Reproduction Guide

## Important: CLASS Modifications

The CLASS code has been modified to implement the Ridder Field model. The modified source files are backed up in `patches/class/` directory:

- `patches/class/background.h.modified`
- `patches/class/input.c.modified`
- `patches/class/background.c.modified`
- `patches/class/perturbations.c.modified`

See `patches/class/README.md` for details on how to apply these modifications.

## 1. Prerequisites
- C compiler (gcc/clang)
- Python 3 with numpy
- Make

## 2. Build Instructions
The CLASS code is located in `phase2/class`. To build:

```bash
cd phase2/class
make clean
make -j 4
```

## 3. Running the Smoke Test
A specification-compliant configuration file is located at `phase3/ridder_smoketest_spec.ini`.

To run the smoke test:

```bash
cd phase2/class
./class ../../phase3/ridder_smoketest_spec.ini
```

## 4. Verifying Results
The output files will be generated in `phase2/class/output/`.
Key files:
- `ridder_smoketest_00_background.dat`: Background evolution (phi, rho_scf, etc.)
- `ridder_smoketest_00_cl.dat`: CMB power spectra

Expected values (Safe Mode):
- Sound Horizon ($r_s$): ~139.06 Mpc
- Peak EDE fraction ($f_{EDE}$): ~15.46%
- Peak redshift ($z_{peak}$): ~6697
- Initial field value ($\phi_{ini}$): ~0.84 (Planck units)

## 5. Troubleshooting
If $z_{peak}$ is too low (~634), it means the field mass is too small (oscillates late).
This usually indicates `Lambda` is too small or `f` is too large.
Check `scf_parameters` in the `.ini` file.

