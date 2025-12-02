# Quick Fix for Bus Errors (No Code Changes)

## Immediate Solution: Run Fewer Chains

Since you can run 15 other chains fine, the issue is likely:
1. **Specific to H0 fixed chains** - maybe certain H0 values trigger a bug
2. **Resource contention** - 7 H0 chains + other chains = too many
3. **Parameter combination** - fixed H0 might cause Ridder field to hit edge cases

## Quick Fix Options

### Option 1: Run H0 Chains in Smaller Batches (RECOMMENDED)

```bash
# Batch 1: Lower H0 values (4 chains)
for h0 in 68.5 69.5 70.5 71.5; do
    COBAYA_USE_FILE_LOCKING=False nohup cobaya-run configs/tier5_ede_shoes_desi_h0_fixed_${h0}.yaml > logs/tier5_ede_h0_fixed_${h0}.log 2>&1 &
done

# Wait for these to complete, then:
# Batch 2: Higher H0 values (3 chains)
for h0 in 72.5 73 73.5; do
    COBAYA_USE_FILE_LOCKING=False nohup cobaya-run configs/tier5_ede_shoes_desi_h0_fixed_${h0}.yaml > logs/tier5_ede_h0_fixed_${h0}.log 2>&1 &
done
```

### Option 2: Run Only Critical H0 Values

You already have complete results for H0=69, 70, 71, 72. For the ceiling plot, you really need:
- **Essential:** 68.5, 69.5, 70.5, 71.5 (to find exact elbow)
- **Nice to have:** 72.5, 73, 73.5 (to show catastrophic rejection)

**Skip 72.5, 73, 73.5 for now** - you can infer the curve from H0=72.

### Option 3: Increase Safety Thresholds (Code Change - Minimal)

If you want to try a code fix, the most likely culprit is line 615 in `background.c`:

```c
double decay_factor = pow(a / pba->a_osc_ridder, -3.0 * (1.0 + pba->w_eff_ridder));
```

**Potential issues:**
- If `a_osc_ridder` is 0 or uninitialized → division by zero or invalid pow()
- If `w_eff_ridder` is NaN/Inf → invalid exponent

**Quick safety check to add:**
```c
// Before line 615
if (pba->a_osc_ridder <= 0.0 || !isfinite(pba->a_osc_ridder)) {
    class_stop(pba->error_message, "Invalid a_osc_ridder = %e", pba->a_osc_ridder);
}
if (!isfinite(pba->w_eff_ridder)) {
    class_stop(pba->error_message, "Invalid w_eff_ridder = %e", pba->w_eff_ridder);
}
```

---

## Testing Strategy

### Test 1: Run One H0 Chain Alone
```bash
# Kill all other chains, run just one
pkill -f cobaya
sleep 2
COBAYA_USE_FILE_LOCKING=False cobaya-run configs/tier5_ede_shoes_desi_h0_fixed_70.5.yaml
```

**If this works:** It's a concurrency/resource issue → use Option 1
**If this crashes:** It's a parameter-specific bug → need code fix

### Test 2: Check Which H0 Values Crash
```bash
# Run each H0 value one at a time, record which crash
for h0 in 68.5 69.5 70.5 71.5 72.5 73 73.5; do
    echo "Testing H0=$h0..."
    timeout 300 cobaya-run configs/tier5_ede_shoes_desi_h0_fixed_${h0}.yaml 2>&1 | grep -E "(Bus error|Signal|Error)" || echo "  OK"
done
```

**If specific H0 values crash:** That tells us which parameter combination is problematic.

---

## Recommended Action Plan

1. **Right now:** Run only 4 H0 chains at a time (Option 1)
2. **If crashes continue:** Test each H0 value individually (Test 2)
3. **If specific H0 values crash:** Add safety checks to code (Option 3)
4. **For paper:** You already have enough data (H0=69,70,71,72) to show the ceiling

---

## Why This Might Work

The bus errors happen when:
- Multiple H0 chains run simultaneously
- All crash at roughly the same time
- Error: "Non-existant physical address"

This suggests:
- **Not hardware** (you run 15 other chains fine)
- **Not general memory** (other chains work)
- **Specific to H0 fixed chains** (parameter combination or code path)

Running fewer at a time reduces the chance of hitting the bug, and if it's resource-related, smaller batches should work.
