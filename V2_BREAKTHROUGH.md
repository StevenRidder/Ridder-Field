# V2 BREAKTHROUGH - November 23, 2025

## 🎉 MAJOR PROGRESS

### Root Cause Found and Fixed

**PROBLEM**: Python wrapper was using a stale `libclass.a` library!

**SOLUTION**: Force complete rebuild with:
```bash
cd phase2/class
rm -f libclass.a
make clean
make -j8
cd python
rm -rf build classy.c *.so
python3 -m Cython.Build.Cythonize classy.pyx
python3 setup.py install --user --force
```

### What Now Works ✅

1. ✅ `background_init` is called
2. ✅ `background_solve` is called
3. ✅ `background_derivs` is called
4. ✅ Ridder field derivatives block is entered
5. ✅ Integration is attempting to run

### Current Issue 🔧

**Integration fails with "Step size too small":**

```
Error in evolver_ndf15: Step size too small: step:5.15779e-14, minimum:5.15779e-14
```

**This is GOOD news!** It means:
- The field IS trying to evolve
- The equation of motion IS being integrated
- The problem is now numerical (stiff dynamics) not structural

### Next Steps

1. **Fix unit conversions** (still wrong)
   - Current: V in eV⁴ being converted incorrectly
   - Need: Proper conversion to CLASS H² units (Mpc⁻²)

2. **Check initial conditions**
   - φ_ini = 2.0 ✓
   - φ'_ini = 0.0 (might need small initial velocity)

3. **Adjust integration tolerances**
   - May need to relax `tol_background_integration`
   - Or use smaller initial step size

4. **Verify potential shape**
   - V(φ=2.0) = 2.84×10⁴ eV⁴
   - dV/dφ at φ=2.0 should drive evolution

### Key Lesson

**ALWAYS do a complete rebuild after modifying C code!**

The Python wrapper can cache old `.so` files, leading to confusing behavior where:
- Code changes don't take effect
- Debug prints don't appear
- Old bugs persist despite "fixes"

**Fix**: Use `make clean` and remove all Python build artifacts before rebuilding.

### Status

**UNBLOCKED**: The field is now attempting to evolve!

Next task: Fix the numerical integration issue (stiff dynamics).

