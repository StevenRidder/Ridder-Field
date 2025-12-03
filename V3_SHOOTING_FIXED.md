# V3 Shooting: Fixed and Working

**Date:** 2025-11-25  
**Status:** ✅ SHOOTING OPERATIONAL

---

## The Shooting Bugs (All Fixed)

1. **Lambda bounds too small** → Changed from [1e-4, 0.1] to [0.001, 0.5] eV
2. **Working directory wrong** → Added `cwd=CLASS_PATH` to subprocess calls
3. **Output path absolute** → Changed INI `root` from absolute to relative path
4. **File counter mismatch** → Used glob + mtime to find latest background file (not hardcoded `00`)

---

## Test Results (EDE-only, tail disabled)

```json
{
    "Lambda_EDE_eV": 0.383,
    "observables": {
        "H0_km_s_Mpc": 67.36,
        "f_EDE_peak": 0.1705,
        "z_peak": 2135
    }
}
```

**Shooting converged in 6 iterations** ✓

---

## Known Issue: Tail Calibration

With `Lambda_tail = 16 meV`, the tail dominates at z=0 (f_tail~99.9%), giving H0~2840 km/s/Mpc.

**Root cause:** V3 tail parameters need recalibration. The v2 tail had different normalization.

**Workaround:** Run 24-point scan with **tail disabled** (`Lambda_tail=0`) to get clean EDE-only v3 results.

---

## Next: 24-Point Scan

Ready to run v3 scan with:
- EDE enabled, tail disabled
- Shooting calibrates Lambda_EDE for each (z_c, sigma_lna) point
- Compare v3 vs v1 results

See `scan_v3_24point.py` for implementation.

